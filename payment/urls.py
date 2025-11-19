from django.urls import path
from . import views

urlpatterns = [
    path("", views.main, name="main"),
    path("success", views.success, name="success"),
    path("cancel", views.cancel, name="cancel"),
    path("item/<int:id>", views.item, name="item"), 
    path("pay_item/<int:id>", views.pay_item, name="pay_item"),
    path("order/<int:id>", views.order, name="order"),
    path("pay_order/<int:id>", views.pay_order, name="pay_order")
]