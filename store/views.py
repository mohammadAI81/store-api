from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

@api_view()
def product_list(request):
    product = Product.objects.select_related('category')
    serializer = ProductSerializer(product, many=True, context={'request': request})
    return Response({'title': 'list of product', 'products': serializer.data})

@api_view(['GET', 'POST'])
def product_detail(request, pk):
    if request.method == 'GET':
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        product = ProductSerializer(data=request.data)
        product.is_valid(raise_exception=True)
        print(request.data)
        return Response('Okay')

@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serializer = CategorySerializer(category)
    return Response({'category': serializer.data})