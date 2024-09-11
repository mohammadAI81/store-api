from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.product_list, name='product-list'),
    path('categories/', views.category_list, name='category-list'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),
    path('categories/<int:pk>/', views.category_detail, name='category-detail'),
]
