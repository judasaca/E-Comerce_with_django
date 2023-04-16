from rest_framework import serializers
from decimal import Decimal
from .models import Cart, CartItem, Customer, Order, OrderItem, Product, Collection, ProductImage, Review
from django.db import transaction
from .signals import order_created
class CollectionSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.SerializerMethodField(method_name='count_products')
    def count_products(self, collection: Collection):
        return collection.products.count()
    


class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    # This avoids the duplicated code.
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'title', 'description','slug', 'inventory', 'unit_price', 'collection', 'price_with_tax', 'images']

        # This is a bad practice:
        # fields = '__all__'
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length = 255)
    # price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    # # This query the collection title
    # """ collection = serializers.PrimaryKeyRelatedField(
    #     queryset = Collection.objects.all()
    # ) """

    # #this gets the object of collections
    # #collection = CollectionSerializer()

    # #This makes an hyperlink
    # collection = serializers.HyperlinkedRelatedField(
    #     queryset = Collection.objects.all(),
    #     view_name= 'collection-detail'
    # )

    def calculate_tax(self, product: Product):
        return product.unit_price*Decimal(1.1)

    # This makes a custom validation function
    # def validate(self, data):
    #     if data['password'] != data['confirm_password']:
    #         return serializers.ValidationError('Passwords dont match')

    #     return data

    #This makes a custom function to save an object
    # def create(self, validated_data):
    #     product = Product(**validated_data)
    #     product.other = 1
    #     product.save()
    #     return product


    #This makes a custom update function 
    # def update(self, instance, validated_data):
    #     instance.unit_price = validated_data.get('unit_price')
    #     instance.save()
    #     return instance

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']


    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)




class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model =Product
        fields = ['id', 'title', 'unit_price' ]





class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price', 'product_id']
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    def create(self, validated_data):
        cart_id = self.context['cart_id']
        return CartItem.objects.create(cart_id = validated_data, **validated_data)




class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'items_count', 'items', 'total_price']
        
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, cart: Cart):
        return sum([item.quantity*item.product.unit_price for item in cart.items.all()])
    
    items_count = serializers.SerializerMethodField(method_name='count_items')
    def count_items(self, cart: Cart):
        return cart.items.count()
    

class AddCartItemSerializer(serializers.ModelSerializer):
    # This force django to admit product id as a field to POST request
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk = value).exists():
            raise serializers.ValidationError('No product with the given id was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            # This can raise an exception if it doen't exist
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            # This must be donde to save method works properly
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id = cart_id, **self.validated_data)
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']

class OrderItemSerializer(serializers.ModelSerializer):
    #product = SimpleProductSerializer(read_only=True)
    product = SimpleProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = [
            "id", 'product','unit_price', 'quantity'
        ]
    

class OrderSerializer(serializers.ModelSerializer):
    
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status',
                  'items'
                  ]


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    #this validates if there is a cart with given id
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk = cart_id).exists():
            raise serializers.ValidationError('No cart with given ID was found')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            customer = Customer.objects.get(user_id = self.context['user_id'])
            order = Order.objects.create(customer = customer)
            #This returns a queryset
            cart_items = CartItem.objects.select_related('product').filter(cart_id = cart_id )
            order_items = [
                OrderItem(
                    order = order,
                    product = item.product,
                    unit_price = item.product.unit_price,
                    quantity = item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk = cart_id).delete()
            # self.__class__ class the class where is defined the function
            order_created.send_robust(sender=self.__class__, order = order)
            return order


