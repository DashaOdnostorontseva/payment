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
    
class Discount(models.Model):
    name = models.CharField(max_length=255, help_text="Наименование скидки", blank=True)
    amount = models.FloatField(default=0, help_text="Сумма скидки")
    stripe_discount_id = models.CharField(max_length=255, help_text="ID скидки в stripe", blank=True)

    def __str__(self):
        display_name = f"{self.name}, сумма: {self.amount}"
        return display_name
    
    def _set_stripe_discount_id(self, discount_id):
        self.stripe_discount_id = discount_id
        self.save(update_fields=["stripe_discount_id"])

class Tax(models.Model):
    name = models.CharField(max_length=255, help_text="Наименование налога", blank=True)
    percent = models.FloatField(default=0, help_text="Налоговая ставка в процентах")
    stripe_tax_id = models.CharField(max_length=255, help_text="ID налоговой ставки в stripe", blank=True)

    def __str__(self):
        display_name = f"{self.name}, ставка: {self.percent}%"
        return display_name
    
    def _set_stripe_tax_id(self, tax_id):
        self.stripe_tax_id = tax_id
        self.save(update_fields=["stripe_tax_id"])
    
class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, help_text="Дата и время создания заказа")
    paid = models.BooleanField(default=False, help_text="Заказ оплачен")
    stripe_session_id = models.CharField(max_length=255, help_text="ID сессии в stripe", blank=True)
    total_amount = models.FloatField(default=0, help_text="Сумма заказа")

    discount = models.ForeignKey(Discount, help_text="Размер скидки", on_delete=models.SET_NULL, blank=True, null=True)
    tax = models.ForeignKey(Tax, help_text="Налоговая ставка", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return "Order ID: " + str(self.id)
    
    @property
    def total(self):
        return sum(i.total for i in self.items.all())
    
    def _update_total_amount(self):
        self.total_amount = self.total
        self.save(update_fields=["total_amount"])

    def _set_stripe_session_id(self, session_id):
        self.stripe_session_id = session_id
        self.save(update_fields=["stripe_session_id"])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, help_text="ID заказа из таблицы Order", on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, help_text="ID товара из таблицы Item", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, help_text="Количество товаров") 

    @property
    def total(self):
        return self.item.price * self.quantity