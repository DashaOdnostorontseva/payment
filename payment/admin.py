from django.contrib import admin
from .models import Item, Order, OrderItem

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    model = Item
    fields = ("name", "description", "price", "stripe_price_id", "stripe_product_id")
    list_display = ("id", "name", "description", "price", "stripe_price_id", "stripe_product_id")
    search_fields = ("name", "description", "price")
    ordering = ("name", "price")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    model = Order
    fields = ("paid", "stripe_session_id", "total_amount")
    list_display = ("id", "created_at", "paid", "stripe_session_id", "total_amount")
    search_fields = ("id", "created_at", "paid", "total_amount")
    ordering = ("id", "created_at", "total_amount")
    readonly_fields = ("total_amount",)
    inlines = [OrderItemInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        order = form.instance
        order._update_total_amount()