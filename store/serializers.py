from rest_framework import serializers
from decimal import Decimal
from store.models import Product, Collection

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