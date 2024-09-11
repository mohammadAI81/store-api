from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        product = Product.objects.select_related('category')
        serializer = ProductSerializer(product, many=True, context={'request': request})
        return Response({'title': 'list of product', 'products': serializer.data})
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('Okay')


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk): 
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'GET':   
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'title': 'Product Is Update', 'description': serializer.data})
    elif request.method == 'DELETE':
        if product.order_items.count()> 0:
            return Response({'error': 'you have orider items you should first delete then'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def category_list(request):
    if request.method == 'GET':
        categories = Category.objects.annotate(product_count=Count('products')).all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        category = CategorySerializer(data=request.data)
        category.is_valid(raise_exception=True)
        category.save()
        return Response(['okay', category.data], status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, pk):
    category = get_object_or_404(Category.objects.annotate(product_count=Count('products')), pk=pk)
    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CategorySerializer(instance=category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if category.products.count() > 0:
            return Response({"errors": 'error'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)