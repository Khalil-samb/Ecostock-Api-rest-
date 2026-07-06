from django.contrib import admin
from .models import Warehouse, Product


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "capacity")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "expiration_date", "status", "warehouse")
    list_filter = ("status", "warehouse")
