from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin
from store.filters import ProductFilter

from .models import Cart, CartItem, Customer, OrderItem, Product, Collection, Review
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CustomerSerializer, ProductSerializer, CollectionSerializer, ReviewSerializer, UpdateCartItemSerializer
# Create your views here.

# If we want to dont allow moodification methods we can inherit this class from ReadOnlyModelViewSet.
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    #pagination_class = PageNumberPagination
    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id = kwargs['pk']).count() >0:
            return Response({'error':'There are order items asociated with this product.'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    

class CartViewSet(CreateModelMixin, 
                  GenericViewSet, 
                  RetrieveModelMixin, 
                  DestroyModelMixin):
    queryset=Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

    def get_serializer_context(self):
        return {'request': self.request}
    
class CartItemViewSet(ModelViewSet ):
    # The method names muist be in lowercase
    http_method_names = ['get', 'post', 'patch', 'delete']
    def get_serializer_class(self):
        if self.request.method =='POST':
            return AddCartItemSerializer
        # This method is patch because it only updates a proporty of the object
        elif self.request.method =='PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
        

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
    
    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id = self.kwargs['cart_pk'])
    
    

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.prefetch_related('product_set').all()
    serializer_class = CollectionSerializer
    def get_serializer_context(self):
        return {'request': self.request}
    
    # VIews sets use destroy method instead of delete.
    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id = kwargs['pk']).count() > 0:
            return Response({
                'error': 'This collection has products associated.'
            })
        return super().destroy(request, *args, **kwargs)
    


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    
    def get_queryset(self):

        return Review.objects.filter(product_id = self.kwargs['product_pk'])
    

class CustomerViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer