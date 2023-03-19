from ..models import Customer
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

#using setting config we avoid the dependency on core app
# This is a signal handleer
@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def create_customer_for_new_user(sender, **kwargs):
    # if a user is created, then a customer is created too
    if kwargs['created']:
        Customer.objects.create(user = kwargs['instance'])

