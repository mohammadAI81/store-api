from typing import Any
from django.contrib import admin, messages
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from . import models


class CommentProduct(admin.TabularInline):
    model = models.Comment
    extra = 1
class OrderItemOrder(admin.TabularInline):
    model = models.OrderItem
    extra = 1
    autocomplete_fields = ['product']


class InventoryFilter(admin.SimpleListFilter):
    LESS_THAN_3 = '<3'
    BETWEEN_3_AND_10 = '3=<10'
    MORE_THAN_10 = '>=10'
    title = 'Critical Inventory Status'
    parameter_name = 'inventory'
    
    def lookups(self, request, model_admin):
        return [
            (InventoryFilter.LESS_THAN_3, 'Low'),
            (InventoryFilter.BETWEEN_3_AND_10, 'Medium'),
            (InventoryFilter.MORE_THAN_10, 'High'),
        ]
        
    def queryset(self, request, queryset):
        if self.value() == self.LESS_THAN_3:
            return queryset.filter(inventory__lt=3)
        if self.value() == self.BETWEEN_3_AND_10:
            return queryset.filter(inventory__range=(3, 10))
        if self.value() == self.MORE_THAN_10:
            return queryset.filter(inventory__gte=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'inventory', 'unit_price', 'inve_sta', 'n_category', 'n_comment']
    list_editable = ['unit_price']
    ordering = ['id']
    list_per_page = 50
    list_select_related = ['category']
    list_filter = ['datetime_created', InventoryFilter]
    actions = ['clear_inventory']
    search_fields = ['name']
    prepopulated_fields = {
        'slug': ['name',],
    }
    
    inlines = [
        CommentProduct,
    ]
    
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('comments').annotate(count_comment=Count('comments'))
    
    
    def inve_sta(self, product):
        if product.inventory < 10:
            return 'Low'
        elif product.inventory < 50:
            return 'Mediwm'
        else:
            return 'High'
    
    @admin.display(ordering='category__title', description='name category')
    def n_category(self, product):
        return product.category.title
    
    
    @admin.display(ordering='count_comment', description='# Comments')
    def n_comment(self, product):
        url = (
            reverse('admin:store_comment_changelist')
            + '?'
            + urlencode({
                'product__id':product.id,
            })
        )
        return format_html('<a href="{}">{}</a>', url, product.count_comment)
        # return product.count_comment
    
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{update_count} of product inventories cleared to zero.',
            messages.WARNING,
        )
        
    
    
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'num_of_count']
    list_editable = ['status']
    ordering = ['id']
    list_per_page = 10
    search_fields = ['customer__first_name']
    inlines = [
        OrderItemOrder,
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items').annotate(count=Count('items'))
    
    
    @admin.display(ordering='count', description='# Items')
    def num_of_count(self, order):
        return order.count


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'status']
    list_editable = ['status']
    list_per_page = 250
    ordering = ['id']
    autocomplete_fields = ['product',]


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user__first_name', 'user__last_name', 'user__email', 'name']
    list_display_links = ['user__first_name', 'user__last_name']
    list_per_page = 10
    ordering = ['user__last_name', 'user__first_name']
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith']
    list_select_related = ['user']
    
    @admin.display(ordering='last_name', description='Full name')
    def name(self, customer):
        return customer.user.first_name + ' ' + customer.user.last_name
    
    
@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity']
    list_per_page = 20
    ordering = ['product']
    autocomplete_fields = ['product', 'order']
  
    
class CartItemInline(admin.TabularInline):
    model = models.CartItem
    fields = ['id', 'product', 'quantity']
    extra = 1
    
    
@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id']
    inlines = [CartItemInline]
    
    
@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['city', 'province']
    list_select_related = ['customer']