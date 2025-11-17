from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=256, help_text="Наименование товара")
    description = models.CharField(max_length=1000, help_text="Описание товара")
    price = models.IntegerField(default=0, help_text="Цена товара")