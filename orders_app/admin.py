from django.contrib import admin

from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_name', 'business_user', 'customer_user', 'price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['product_name', 'business_user__username', 'customer_user__username']
    readonly_fields = ['created_at']
