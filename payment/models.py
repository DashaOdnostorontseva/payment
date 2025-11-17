from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=255, help_text="Наименование товара")
    description = models.CharField(max_length=1000, help_text="Описание товара")
    price = models.FloatField(default=0, help_text="Цена товара")

    stripe_product_id = models.CharField(max_length=255, help_text="ID продукта в stripe")
    stripe_price_id = models.CharField(max_length=255, help_text="ID цены в stripe")