from django.contrib import admin
from . import models
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
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    list_per_page = 10

admin.site.register(models.Collection)


@admin.register(models.Order)
class OrderAmin(admin.ModelAdmin):
    list_display = ['placed_at', 'customer_full_name']
    list_select_related = ['customer']
    list_per_page=10
    @admin.display()
    def customer_full_name(self, order):
        return order.customer.first_name + ' ' +order.customer.last_name
