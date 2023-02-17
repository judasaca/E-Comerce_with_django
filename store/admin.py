
from typing import Any
from django.contrib import admin, messages
from django.http import HttpRequest
from django.db.models.query import QuerySet

from . import models
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse

# Register your models here.

class InventoryFilter(admin.SimpleListFilter):

    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request: Any, model_admin: Any):
        return [
            ('<10', 'Low')
        ]

    def queryset(self, request: Any, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__lt = 10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):

    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    actions  = ['clear_inventory']
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    search_fields = ['title']
    list_per_page = 10
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory <10:
            return 'LOW'
        return 'OK'
    list_select_related = ['collection']
    
    def collection_title(self, product):
        return product.collection.title

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, query_set):
        updated_count = query_set.update(inventory = 0)

        self.message_user(
            request,
            f'{updated_count} products wew successfully updated.'
        )

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'total_orders']
    list_editable = ['membership']
    
    list_per_page = 10
    search_fields = ['first_name__istartswith', 'last_name__istartswith']
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
    search_fields = ['title']
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


class OrderItemInline(admin.StackedInline):
    model = models.OrderItem
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    extra = 1

@admin.register(models.Order)
class OrderAmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'customer_full_name']
    list_select_related = ['customer']
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_per_page=10
    @admin.display()
    def customer_full_name(self, order):
        return order.customer.first_name + ' ' +order.customer.last_name

    
