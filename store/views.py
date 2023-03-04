from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from store.filters import ProductFilter

from .models import OrderItem, Product, Collection, Review
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer
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
    

    


# @api_view(['GET', 'PUT', 'DELETE'])
# def product_detail(request, id):
#     product = get_object_or_404(Product, pk=id)
#     if request.method == 'GET':
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)

#     elif request.method =='PUT':
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     elif request.method =='DELETE':
#         if product.orderitem_set.count() > 0:
#             return Response({'error':'There are order items asociated with this product.'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET', 'POST'])
# def collection_list(request):
#     if request.method == 'GET':
#         query_set = Collection.objects.prefetch_related('product_set').all()
#         serializer = CollectionSerializer(query_set, many=True, context={
#             'request':request
#         })
#         return Response(serializer.data)
#     if request.method == 'POST':
#         serializer = CollectionSerializer(data = request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    
    def get_queryset(self):

        return Review.objects.filter(product_id = self.kwargs['product_pk'])