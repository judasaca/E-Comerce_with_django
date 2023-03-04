from django.urls import include, path
from rest_framework.routers import SimpleRouter
from . import views
from pprint import pprint

router = SimpleRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)
pprint(router.urls)

#URL config
#urlpatterns = router.urls
urlpatterns = [
    #this allows adding url patterns
    path('', include(router.urls)),
]