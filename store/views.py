from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer

@api_view()
def product_list(request):
    product = Product.objects.select_related('category')
    serializer = ProductSerializer(product, many=True)
    return Response({'title': 'list of product', 'products': serializer.data})

@api_view()
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    serializer = ProductSerializer(product)
    return Response(serializer.data)