from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('categories/<int:pk>/', views.CategoryDetail.as_view(), name='category-detail'),
]
