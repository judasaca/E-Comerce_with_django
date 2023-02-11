from django.shortcuts import render
from django.http import HttpResponse
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from django.db.models import Q, F
from store.models import Product, Customer, Collection, Order, OrderItem
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

def say_hello(request):
    #query_set = Product.objects.all() # -filter return a query set
    
    #query_set = Product.objects.get(pk=0).exist() #first return none o exit()
    # esto es un field lookup
    #query_set = Product.objects.filter(description__isnull=True) # __gt -> greater than
    # it is possible to do concatenated lookups f.e. collection__id__range
    # icontain is makes contains not sensitive
    # last_update__year=2021 gets the year, it can be done with month and days
    # description__isnull=True  gets null entries
    #query_set = Product.objects.filter(Q(inventory__lt=10) | ~Q(unit_price__lt=20))
    #query_set = Product.objects.filter(Q(inventory__lt=10) | ~Q(unit_price__lt=20))
    #get(pk=1)
    #Customers with .com email ending
    # this retrieves those product who have been ordered sorted by title
    #query_set = Product.objects.filter(
    #    id__in= OrderItem.objects.values('product__id').distint().order_by('title'))
    #query_set = OrderItem.objects.values('product__id').distint()

    #query_set = Product.objects.select_related('collection').all()

    # This gets the last 5 orders with their related products and curstomers
    #query_set = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]

    result = Product.objects.filter(collection__id = 1).aggregate(count = Count('id'), min_price = Min('unit_price'))


    #customers_1 = Customer.objects.filter(email__icontains='.com')
    #collections_2 = Collection.objects.filter(featured_product_id__isnull=True)
    #products_3 = Product.objects.filter(inventory__lt = 10)
    #orders_4 = Order.objects.filter(customer__id=1)
    #order_item_5 = OrderItem.objects.filter(product__collection__id=3)

    # This is a solution from an excersise
    """ orders_count = Order.objects.aggregate(orderds_count = Count('id'))
    
    sold_products = OrderItem.objects.select_related('product').filter(product__id=1).aggregate(suma=Sum('quantity'))

    orders_customer_1 = Order.objects.select_related('customer').filter(customer__id=1).aggregate(Count('id'))

    point_4 = Product.objects.select_related('collection').filter(collection__id = 3).aggregate(min_price = Min('unit_price'),
        max_price=Max('unit_price'),
        avg_price=Avg('unit_price')
    ) """
    #for product in query_set:
    #    print(product)

    # query set busca los productos solo cuando se utiliza
    return render(request, 'hello.html', {
        'name': 'David',
        'result':point_4
    })