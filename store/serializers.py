from rest_framework import serializers
from decimal import Decimal
from store.models import Cart, CartItem, Product, Collection, Review

class CollectionSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.SerializerMethodField(method_name='count_products')
    def count_products(self, collection: Collection):
        return collection.product_set.count()
    




class ProductSerializer(serializers.ModelSerializer):
    # This avoids the duplicated code.
    class Meta:
        model = Product
        fields = ['id', 'title', 'description','slug', 'inventory', 'unit_price', 'collection', 'price_with_tax']

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
