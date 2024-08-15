from rest_framework import serializers


class CategorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255, source='name')
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    category = CategorySerializer()