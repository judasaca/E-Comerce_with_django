from django.shortcuts import render
from django.http import HttpResponse
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from django.db.models import Q, F,Value, ExpressionWrapper
from store.models import Product, Customer, Collection, Order, OrderItem, Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from tags.models import TaggedItem
from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMessage
from templated_mail.mail import BaseEmailMessage
from .tasks import notify_customers
from django.db import transaction
from django.core.cache import cache
from django.views.decorators.cache import cache_page
import requests

#This decorator can make a transaction
#@transaction.atomic()
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

    #result = Product.objects.filter(collection__id = 1).aggregate(count = Count('id'), min_price = Min('unit_price'))


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

    # This group the orders and retrrieves a column with the count of any customer
    """ query_set = Customer.objects.annotate(
        orders_count = Count('order')
    ) """

    # This calculate an expression with specific DecimalField 
    """ discounted_price = ExpressionWrapper(F('unit_price')*0.8, output_field=DecimalField())
    query_set = Product.objects.annotate(
        discounted_price = discounted_price
    ) """

    # Excersices
    # Point 1: get Customers with their last order ID
    """ point_1 = Customer.objects.annotate(
        last_order_id = Max('order__id')
    )
    # Point 2: Collections and count of their products
    point_2 = Collection.objects.annotate(
        count_products = Count('product__id')
    )

    #Point 3: Customers with more than 5 orders
    point_3 = Customer.objects.annotate(
        count_orders = Count('order')
    ).filter(count_orders__gt=5)
    #Point 4: Customers and the total amount theyve spent
    point_4 = Customer.objects.annotate(
        total_spent = Sum(
            F('order__orderitem__unit_price')*
            F('order__orderitem__quantity')
        )
    )
    #Point 5: Top 5 best-selling products and their total sales
    point_5 = Product.objects.\
        annotate(
            total_sales = F('orderitem__unit_price')*F('orderitem__quantity')
        ).order_by('-total_sales')[:5] """

    #Query generic relationships

    """ content_type = ContentType.objects.get_for_model(Product)
    query_set = TaggedItem.objects.select_related('tag').filter(
        content_type = content_type,
        object_id = 1
    ) """

    # inserting, updating and deliting objects 
    # Inserting
    """ collection = Collection()
    collection.title = 'Video Games'
    collection.featured_product = Product(pk=11)
    collection.save() """

    # updating

    """     collection = Collection.objects.filter(pk=11).update(featured_product = None)
    """
        #deleting

    """ collection = Collection(pk=11)
        collection.delete()

        Collection.objects.filter(id__gt=5).delete() """
    # Excersice 
    # Point 1: Create a shopping cart with an item.

    """ new_cart = Cart()
    new_cart.save()
    new_cart_item = CartItem()
    new_cart_item.cart = new_cart
    new_cart_item.quantity = 1
    new_cart_item.product = Product.objects.get(pk = 1)
    new_cart_item.save()
 """
    #point 2: Remove a shopping cart with its items 

    """ cart = CartItem.objects.get(pk=1)
    cart.delete() """

    """ order = Order()
    order.customer_id = 1
    order.save()

    item = OrderItem()
    item.order = order
    item.product_id = 1
    item.quantity = 1
    item.unit_price=1
    item.save() """

    # This makes a transaction inside a function
    #with transaction.atomic():


    try:
        # This function retrieves an error if an attacant modifies the header.
        send_mail('subject', 'message', 'sender@receiver.com', ['receiver@email.com'])
    except BadHeaderError: 
        pass 

    return render(request, 'hello.html', {
        'name': 'David',
        'result':list([1,2])
    })

def test_view_2(request):
    try: 
        mail_admins('subject', 'message', html_message='html message')
    except BadHeaderError:
        pass
    return render(request, 'hello.html', {
        'name': 'David',
        'result':list([1,2])
    })

def atatch_files_to_emails(request):
    try: 
        message = EmailMessage('subject', 'message', 'sender@receiver.com', ['receiver@email.com'])
        message.attach_file('playground/static/images/OIP.jpg')
        message.send()
    except BadHeaderError:
        pass
    return render(request, 'hello.html', {
        'name': 'David',
        'result':list([1,2])
    })

def use_templated_emails(request):
    try: 
        message = BaseEmailMessage(
            template_name='emails/hello.html',
            context={
                'name': 'judasaca'
            }
        )
        message.send(['receiver@email.com'])
    except BadHeaderError:
        pass
    return render(request, 'hello.html', {
        'name': 'David',
        'result':list([1,2])
    })

def send_email_to_all_customers(request):
    notify_customers.delay('Hello')
    return render(request, 'hello.html', {'name': 'Mosh'})

def slow_api_call(request):
    key = 'httpbin_result'
    if cache.get(key) is None:
        
        #This simulates slow api response
        response = requests.get('https://httpbin.org/delay/2')
        data = response.json()
        # Save the response on cache
        cache.set(key, data)
    
    return render(request, 'hello.html', {'name': cache.get(key)})