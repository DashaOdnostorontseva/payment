from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    model = Item
    fields = ("name", "description", "price", "stripe_price_id", "stripe_product_id")
    list_display = ("id", "name", "description", "price", "stripe_price_id", "stripe_product_id")
    search_fields = ("name", "description", "price")
    ordering = ("name", "price")