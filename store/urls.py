from django.urls import include, path
from rest_framework_nested import routers
from . import views
from pprint import pprint



router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)

# Lookup indicates the parameter name that we are going to have in the 
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
#basename is just a prefix
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

urlpatterns = router.urls + products_router.urls