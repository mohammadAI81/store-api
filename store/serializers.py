from rest_framework import serializers
from decimal import Decimal


class CategorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)



class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    category = CategorySerializer()
    price_after_tax = serializers.SerializerMethodField(method_name='get_price_rial')


    def get_price_rial(self, product):
        return round(product.unit_price * Decimal(1.09), 2)