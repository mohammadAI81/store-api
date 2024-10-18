from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from .models import Category, Product, Comment
from .serializers import CategorySerializer, ProductSerializer, CommentSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    
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
            return Comment.objects.filter(product_id=product_pk)
        else:
            return Comment.objects.select_related('product')
