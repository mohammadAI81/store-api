from django.urls import path
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()

router.register('products', views.ProductViewSet, 'product')
router.register('categories', views.CategoryViewSet, 'category')
router.register('comments', views.CommentViewSet, 'comment')
router.register('carts', views.CartViewSet, 'carts')


products_comment_router = routers.NestedSimpleRouter(router, 'products', lookup='product')
products_comment_router.register('comment', views.CommentViewSet, basename='comment-product')

cart_cart_item_router = routers.NestedSimpleRouter(router, 'carts', lookup='cart')
cart_cart_item_router.register('items', views.CartItemViewSet, 'cart-items')

urlpatterns = router.urls + products_comment_router.urls + cart_cart_item_router.urls

# urlpatterns = [
#     path('products/', views.ProductList.as_view(), name='product-list'),
#     path('categories/', views.CategoryList.as_view(), name='category-list'),
#     path('products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
#     path('categories/<int:pk>/', views.CategoryDetail.as_view(), name='category-detail'),
# ]
