from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer



class ProductList(ListCreateAPIView):
    def get_queryset(self):
        return Product.objects.select_related('category')
    
    def get_serializer_class(self):
        return ProductSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}

class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.order_items.count()> 0:
            return Response({'error': 'you have orider items you should first delete then'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryList(ListCreateAPIView):
    queryset = Category.objects.prefetch_related('products')
    serializer_class = CategorySerializer
        

class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.prefetch_related('products')
    serializer_class = CategorySerializer
    
    def delete(self, request, pk):
        category = get_object_or_404(Category.objects.prefetch_related('products'), pk=pk)
        if category.products.count() > 0:
            return Response({"errors": 'error you can not delete'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

