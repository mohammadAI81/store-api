from decimal import Decimal
from django.urls import reverse
from django.utils.text import slugify
from rest_framework import serializers

from .models import Cart, CartItem, Category, Customer, Order, OrderItem, Product, Comment


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
        

class OrderCustomSerailizer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, source='user.first_name')
    last_name = serializers.CharField(max_length=255, source='user.last_name')
    email = serializers.CharField(max_length=255, source='user.email')
    
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email']


class CustomerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Customer
        fields = ['id', 'user', 'phone_number']
        read_only_fields = ['user']
        

class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price']


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


        
class OrderAdminSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = OrderCustomSerailizer()
    class Meta:
        model = Order
        fields = ['id', 'customer', 'datetime_created', 'status', 'items']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id', 'datetime_created', 'status', 'items']


class OrderCreateSerializer(serializers.Serializer):
    cart_id=serializers.UUIDField()
    
    def validate_cart_id(self, cart_id):
        try:
            if Cart.objects.prefetch_related('items').get(id=cart_id).items.count() == 0:
                raise serializers.ValidationError('This cart is empyu.')
        except Cart.DoesNotExist:
            raise serializers.ValidationError('This cart is not.')
        
        # if not Cart.objects.filter(id=cart_id).exists():
        #     raise serializers.ValidationError('This not cart id.')
        # if CartItem.objects.get(cart_id=cart_id).items.count() == 0:
        #     raise serializers.ValidationError('this cart is Empty.')
        
        return cart_id
    
    def save(self, **kwargs):
        cart_id = self.validated_data['cart_id']
        user_id = self.context['user_id']
        customer = Customer.objects.get(user_id=user_id)

        order = Order()
        order.customer_id = customer.id
        order.save()
        
        cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            
        order_items = list()
        for item in cart_items:
            order_item = OrderItem()
            order_item.order_id = order.id
            order_item.product_id = item.product.id
            order_item.quantity = item.quantity
            order_item.unit_price = item.product.unit_price

            order_items.append(order_item)
            
        OrderItem.objects.bulk_create(order_items)
        
        Cart.objects.get(pk=cart_id).delete()
        return order
            