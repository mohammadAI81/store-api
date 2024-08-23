from rest_framework import serializers
from decimal import Decimal

from .models import Category


class CategorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)



class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    price_after_tax = serializers.SerializerMethodField(method_name='get_price_rial')
    category = serializers.HyperlinkedRelatedField(
        queryset=Category.objects.all(),
        view_name='category-detail',
    )


    def get_price_rial(self, product):
        return round(product.unit_price * Decimal(1.09), 2)