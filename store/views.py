from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin

from django_filters.rest_framework import DjangoFilterBackend

from .paginations import DefaultProductPagination
from .filters import ProductFilterSet
from .models import Cart, CartItem, Category, Product, Comment
from .serializers import CartItemSerailizer, CartSerailizer, CategorySerializer, ProductSerializer, CommentSerializer


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ['name', 'inventory']
    search_fields = ['name', 'inventory']
    pagination_class = DefaultProductPagination
    # filterset_fields = ['category_id', 'inventory']
    filterset_class = ProductFilterSet
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.order_items.count()> 0:
            return Response({'error': 'you have orider items you should first delete then'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.prefetch_related('products')
    serializer_class = CategorySerializer
    
    def destroy(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        if category.products.count() > 0:
            return Response({'errors': 'error you can not delete'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.select_related('product').all()
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        if 'product_pk' in self.kwargs:
            product_pk = self.kwargs['product_pk']
            return Comment.objects.filter(product_id=product_pk).select_related('product')
        else:
            return Comment.objects.select_related('product')
        
    def get_serializer_context(self):
        if 'product_pk' in self.kwargs:
            return {'product_pk': self.kwargs['product_pk']}
        
        
class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerailizer
    queryset = Cart.objects.prefetch_related('items__product')
    
    
class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerailizer
    
    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        return CartItem.objects.filter(cart_id=cart_pk).select_related('product').all()
        
    def get_serializer_context(self):
        if 'cart_pk' in self.kwargs:
            return {'cart_pk': self.kwargs['cart_pk']}
        
    
