from django.db import models

# Create your models here.
class Promotion(models.Model):
    descrion = models.CharField(max_length=255)
    discount = models.FloatField()
    # product_set -> default convention created by django when using many to many relationship


class Collection(models.Model):
    title = models.CharField(max_length=255)
    #product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # cuando se elimina un producto se coloca un valor de nullo
    featured_product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True,
    related_name='+') # This name makes django don't create the reverse-relationship
class Product(models.Model):
    #sku = models.CharField(max_length=10, primary_key=True) #Esto crea una llave primaria
    MEMBERSHIP_BRONZE ='B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'
    MEMBERSHIP_CHOICES= [
        (MEMBERSHIP_BRONZE, 'BronZe'),
        (MEMBERSHIP_SILVER, 'Silver') ,
        (MEMBERSHIP_GOLD, 'Gold'),
    ]

    slug = models.SlugField()
    title = models.CharField(max_length=255) 
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True) # auto_now_add ingrsa la fecha actual al momento de añadir un producto solamente
    memberchip = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)

    # se coloca protecto así si se borra una colección no se borra los producto
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    # se define relación muchos a muchos, el related name es la relación con promocion
    promotions = models.ManyToManyField(Promotion, related_name='products')

class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1, choices = PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    #customer = models.ForeignKey('Customer', on_delete=models.PROTECT)

class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    # No es necesario crear un campo Address en la orden debido a que django lo crea automáticamente con la relación 1-1
    # Aquí puede ir model.SET_NULL - PROTECT
    #customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    
class Cart(models.Model):
    created_at = models.DateTimeField(auto_created=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()



