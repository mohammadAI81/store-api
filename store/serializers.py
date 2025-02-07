from rest_framework import serializers
from decimal import Decimal
from django.urls import reverse
from django.utils.text import slugify

from .models import Cart, CartItem, Category, Customer, Product, Comment


class CategorySerializer(serializers.ModelSerializer):
    
    porducts_num = serializers.IntegerField(source='products.count', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'porducts_num']
        
    
    # def get_porducts_num(self, category):
    #     return category.products.count()
    
    def validate(self, attrs):
        if len(attrs['title']) < 3:
            raise serializers.ValidationError({'name': 'your name is must more than 3'})
        return attrs

    def create(self, validated_data):
        category = Category(**validated_data)
        category.save()
        return category
    
    # def update(self, instance, validated_data):
    #     instance.title = validated_data.get('title')
    #     instance.save()
    #     return instance
    



class ProductSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(max_length=255)
    # unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    price_after_tax = serializers.SerializerMethodField(method_name='get_after_tax')
    # detail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price','category', 'price_after_tax', 'inventory', 'description']



    def get_after_tax(self, product):
        return round(product.unit_price * Decimal(1.09), 2)

    def get_detail(self, product):
        request = self.context['request']
        return request.build_absolute_uri(reverse('product-detail', args=[product.pk]))
    
    def validate(self, data):
        if len(data['name']) < 6:
            raise serializers.ValidationError({'name': 'Product title shoulde be at leate 6'})
        return data
    
    def create(self, validated_data):
        product = Product(**validated_data)
        product.slug = slugify(product.name)
        product.save()
        return product
 
    # def update(self, instance, validated_data):
    #     instance.inventory = validated_data.get('inventory')
    #     instance.save()
    #     return instance
    
   
class CommentSerializer(serializers.ModelSerializer):
    
    # product = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ['id', 'name', 'body', 'status']
        
    def create(self, validated_data):
        product_id = self.context.get('product_pk')
        return Comment.objects.create(product_id=product_id, **validated_data)
    

class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price']



class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']
        
    def create(self, validated_data):
        cart_pk = self.context.get('cart_pk')
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')
        
        try:
            cart_item = CartItem.objects.get(cart_id=cart_pk, product_id=product.id)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id=cart_pk, **validated_data)

        self.instance = cart_item
        return cart_item
    
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
    
    
class CartItemSerailizer(serializers.ModelSerializer):
    product = CartProductSerializer()
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_total_price(self, cart_item):
        return cart_item.quantity * cart_item.product.unit_price
    
    
class CartSerailizer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'total_price']
        read_only_fields = ['id',]
        
    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
        

class CustomerSerializer(serializers.ModelSerializer):
    
    user = serializers.StringRelatedField()
    
    class Meta:
        model = Customer
        fields = ['id', 'user', 'phone_number']
        read_only_fields = ['user']