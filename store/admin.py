from typing import Any
from django.contrib import admin
from django.http import HttpRequest
from django.db.models.query import QuerySet
from . import models
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse

# Register your models here.
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory <10:
            return 'LOW'
        return 'OK'
    list_select_related = ['collection']
    
    def collection_title(self, product):
        return product.collection.title

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'total_orders']
    list_editable = ['membership']
    list_per_page = 10

    @admin.display(ordering='total_orders')
    def total_orders(self, customer):
        url = (reverse('admin:store_order_changelist')
        + '?'
        + urlencode({
            'customer__id':str(customer.id)
        })
        )

        return format_html('<a href="{}">{}</a>', url, customer.total_orders)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            total_orders = Count('order')
            )

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (reverse('admin:store_product_changelist')
        + '?'
        + urlencode({
            'collection__id': str(collection.id)
        })
        )
        return format_html('<a href="{}">{}</a>', url, collection.products_count)
         
    
    # Modifies the base query-set
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            products_count = Count('product')
        )

@admin.register(models.Order)
class OrderAmin(admin.ModelAdmin):
    list_display = ['placed_at', 'customer_full_name']
    list_select_related = ['customer']
    list_per_page=10
    @admin.display()
    def customer_full_name(self, order):
        return order.customer.first_name + ' ' +order.customer.last_name

    
