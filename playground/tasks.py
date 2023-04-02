from celery import shared_task
from time import sleep
@shared_task
def notify_customers(message):
    print('everything working...')