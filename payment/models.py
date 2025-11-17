from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=255, help_text="Наименование товара")
    description = models.CharField(max_length=1000, help_text="Описание товара")
    price = models.FloatField(default=0, help_text="Цена товара")

    stripe_product_id = models.CharField(max_length=255, help_text="ID продукта в stripe", blank=True)
    stripe_price_id = models.CharField(max_length=255, help_text="ID цены в stripe", blank=True)

    def _set_stripe_product_id(self, product_id):
        self.stripe_product_id = product_id
        self.save(update_fields=["stripe_product_id"])

    def _add_stripe_price_id(self, price_id):
        self.stripe_price_id = price_id
        self.save(update_fields=["stripe_price_id"])

    def __str__(self):
        return self.name