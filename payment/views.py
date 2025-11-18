from django.shortcuts import render
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed

from .models import Item, Order
from .stripeScripts import scripts as stripeScript

stripe.api_key = settings.SECRET_KEY_STRIPE

def main(request):
    return render(request, "main.html")

def pay_item(request, id):
    print("call pay_item", pay_item)
    if request.method == "GET":
        item = get_object_or_404(Item, id=id)
        
        price_id = stripeScript.get_stripe_price_id(item)
        
        session = stripe.checkout.Session.create(
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
        )

        print("session.url", session.url)

        return JsonResponse({"sessionUrl": session.url})
    else:
        return HttpResponseNotAllowed(["GET"])

def item(request, id):
    print("call item", item)
    if request.method == "GET":
        item_obj = get_object_or_404(Item, id=id)
        return render(request, "item.html", {"item":item_obj})
    else:
        return HttpResponseNotAllowed(["GET"])
    
def pay_order(request, id):
    if request.method == "GET":
        order = get_object_or_404(Order, id=id)
        items = list()
        tax_id = None
        discount_id = None

        if order.tax:
            tax_id = stripeScript.get_stripe_tax_ids(order.tax)

        for i in order.items.select_related("item").all():
            item = i.item
            price_id = stripeScript.get_stripe_price_id(item)

            item_data = {"price":price_id, "quantity":i.quantity}

            if tax_id:
                item_data["tax_rates"] = [tax_id]

            items.append(item_data)

        if order.discount:
            discount_id = stripeScript.get_stripe_discount_id(order.discount)

        session = stripe.checkout.Session.create(
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            line_items=items,
            mode="payment",
            discounts=[{"coupon":discount_id}]
        )

        order.stripe_session_id = session.id
        order.save(update_fields=["stripe_session_id"])

        return JsonResponse({"sessionUrl": session.url})
    else:
        return HttpResponseNotAllowed(["GET"])
    
def order(request, id):
    if request.method == "GET":
        order = get_object_or_404(Order, id=id)
        return render(request, "order.html", {"order":order})
    else:
        return HttpResponseNotAllowed(["GET"])
