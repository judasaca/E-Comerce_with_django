from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin
from store.filters import ProductFilter
from rest_framework.decorators import action

from store.permissions import FullDjangoModelPermissions, IsAdminOrReadOnly, ViewCustomerPermission
from .models import Cart, CartItem, Customer, Order, OrderItem, Product, Collection, ProductImage, Review
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CreateOrderSerializer, CustomerSerializer, OrderItemSerializer, OrderSerializer, ProductImageSerializer, ProductSerializer, CollectionSerializer, ReviewSerializer, UpdateCartItemSerializer, UpdateOrderSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions


# Create your views here.

# If we want to dont allow moodification methods we can inherit this class from ReadOnlyModelViewSet.
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    permission_classes = [IsAdminOrReadOnly]

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
        return CartItem.objects.select_related('product')\
            .filter(cart_id = self.kwargs['cart_pk'])
    
    

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.prefetch_related('product_set').all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

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
    

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [FullDjangoModelPermissions]

    @action(detail=True, permission_classes=[ViewCustomerPermission])
    def history(self, request, pk):
        return Response('ok')
    #This is an action
    # Detail makes the action to be in customer/me
    # If it is true then will be in customer/user_id/me
    # Permission classes allow authenticated users to use the action
    @action(detail = False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        # get_or_create return a tuple that means if the customer was created or not
        customer= Customer.objects.get(user_id = request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method =='PUT':
            serializer = CustomerSerializer(customer, data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class OrderViewSet(ModelViewSet):

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    def get_permissions(self):
        # Only admin users can patch or delete an order
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data = request.data, 
                                           context = {'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        customer_id = Customer.objects.only('id').get(user_id = user.id)
        return Order.objects.filter(customer_id = customer_id)
    
    def get_serializer_context(self):
        return {'user_id': self.request.user.id}
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    def get_queryset(self):
        return ProductImage.objects.filter(product_id = self.kwargs['product_pk'])
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
