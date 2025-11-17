from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    model = Item
    fields = ("name", "description", "price")
    search_fields = ("name", "description", "price")
    ordering = ("name", "price")