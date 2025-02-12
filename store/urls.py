from django.urls import path
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()

router.register('products', views.ProductViewSet, basename='product')
router.register('categories', views.CategoryViewSet, basename='category')
router.register('comments', views.CommentViewSet, basename='comment')
router.register('carts', views.CartViewSet, basename='carts')
router.register('customers', views.CustomerViewSet, basename='customer')
router.register('orders', views.OrderViewSet, basename='orders')


products_comment_router = routers.NestedSimpleRouter(router, 'products', lookup='product')
products_comment_router.register('comment', views.CommentViewSet, basename='comment-product')

cart_cart_item_router = routers.NestedSimpleRouter(router, 'carts', lookup='cart')
cart_cart_item_router.register('items', views.CartItemViewSet, 'cart-items')

order_items_router = routers.NestedSimpleRouter(router, 'orders', lookup='order')
order_items_router.register('items', views.OrderItemsViewSet, basename='order-items')

urlpatterns = router.urls + products_comment_router.urls + cart_cart_item_router.urls + order_items_router.urls


