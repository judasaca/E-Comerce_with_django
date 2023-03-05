from django.urls import include, path
from rest_framework_nested import routers
from . import views
from pprint import pprint



router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)

# Lookup indicates the parameter name product_pk
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
#basename is just a prefix
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

#
cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + cart_router.urls