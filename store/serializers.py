from rest_framework import serializers
from decimal import Decimal
from django.urls import reverse

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['title', 'description']
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)



class ProductSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # name = serializers.CharField(max_length=255)
    # unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    price_after_tax = serializers.SerializerMethodField(method_name='get_price_rial')
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    # detail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price', 'inventory', 'category', 'price_after_tax']



    def get_price_rial(self, product):
        return round(product.unit_price * Decimal(1.09), 2)

    def get_detail(self, product):
        request = self.context['request']
        return request.build_absolute_uri(reverse('product-detail', args=[product.pk]))
    
