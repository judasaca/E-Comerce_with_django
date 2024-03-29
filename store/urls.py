from django.urls import include, path
from rest_framework_nested import routers
from . import views
from pprint import pprint



router = routers.DefaultRouter()
# basename -> basename-detail basename-list
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')

# Lookup indicates the parameter name product_pk
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
#basename is just a prefix
products_router.register('reviews', views.ReviewViewSet,
                          basename='product-reviews')
products_router.register('images', views.ProductImageViewSet, basename='product-images')

#
cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + cart_router.urls