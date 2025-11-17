from django.shortcuts import render
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed

from .models import Item

stripe.api_key = settings.SECRET_KEY_STRIPE

def buy(request, id):
    print("call buy", buy)
    if request.method == "GET":
        item = get_object_or_404(Item, id=id)

        product = stripe.Product.create(name=item.name)

        price = stripe.Price.create(
            currency="rub",
            unit_amount=item.price*100,
            product=product.id
        )

        session = stripe.checkout.Session.create(
            success_url="https://example.com/success",
            line_items=[{"price": price.id, "quantity": 2}],
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
