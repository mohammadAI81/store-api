from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated, DjangoModelPermissions

from django_filters.rest_framework import DjangoFilterBackend

from .paginations import DefaultProductPagination
from .filters import ProductFilterSet
from .models import Cart, CartItem, Category, Customer, Order, OrderItem, Product, Comment
from .permissions import IsAdminOrReadOnly, SendPrivateEmailToCustomer, CustomDjangoModelPermission
from .serializers import (
                    AddCartItemSerializer, CartItemSerailizer, CartSerailizer, 
                    CategorySerializer, CustomerSerializer, OrderAdminSerializer, OrderItemSerializer,  
                    CommentSerializer, OrderSerializer, UpdateCartItemSerializer, ProductSerializer,
                    OrderCreateSerializer
                )


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ['name', 'inventory']
    search_fields = ['name', 'inventory']
    pagination_class = DefaultProductPagination
    # filterset_fields = ['category_id', 'inventory']
    filterset_class = ProductFilterSet
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.order_items.count()> 0:
            return Response({'error': 'you have orider items you should first delete then'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.prefetch_related('products')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def destroy(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        if category.products.count() > 0:
            return Response({'errors': 'error you can not delete'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.select_related('product').all()
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        if 'product_pk' in self.kwargs:
            product_pk = self.kwargs['product_pk']
            return Comment.objects.filter(product_id=product_pk).select_related('product')
        else:
            return Comment.objects.select_related('product')
        
    def get_serializer_context(self):
        if 'product_pk' in self.kwargs:
            return {'product_pk': self.kwargs['product_pk']}
        
        
class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerailizer
    queryset = Cart.objects.prefetch_related('items__product')    
    
class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'patch', 'post', 'delete']
    
    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        return CartItem.objects.filter(cart_id=cart_pk).select_related('product').all()
        
    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk']}
        
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerailizer
        

class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.select_related('user')
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user_id = request.user.id
        customer = Customer.objects.select_related('user').get(user_id=user_id)
        if request.method == 'GET':    
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(instance=customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
    @action(detail=True, permission_classes=[SendPrivateEmailToCustomer])
    def send_private_email(self, request, pk):
        return Response(f'Sending email to customer {pk=}')
    
    
    
class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related(
            Prefetch(
                'items',
                OrderItem.objects.select_related('product')
            )
        ).select_related('customer__user')
        user = self.request.user
        if user.is_staff:
            return queryset
        
        return queryset.filter(customer__user_id=self.request.user.id)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        if self.request.user.is_staff:
            return OrderAdminSerializer
        return OrderSerializer
    
    def get_serializer_context(self):
        return {'user_id': self.request.user.id}



class OrderItemsViewSet(ModelViewSet):
    serializer_class = OrderItemSerializer
    
    def get_queryset(self):
        order_pk = self.kwargs.get('order_pk')
        return OrderItem.objects.select_related('product').filter(order_id=order_pk)
    