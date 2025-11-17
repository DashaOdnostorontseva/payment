from django.shortcuts import render
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed

from .models import Item

stripe.api_key = settings.SECRET_KEY_STRIPE

def create_stripe_product(item):
    print(create_stripe_product)
    product = stripe.Product.create(name=item.name)
    item._set_stripe_product_id(product.id)

    return product.id
    
def create_stripe_price(item, product_id):
    print(create_stripe_price)
    price = stripe.Price.create(
        currency="rub",
        unit_amount=int(item.price * 100),
        product=product_id
    )
    item._add_stripe_price_id(price.id)

    return price.id


def get_stripe_price_id(item):
    print(get_stripe_price_id)
    if item.stripe_price_id:
        return item.stripe_price_id
    
    if not item.stripe_product_id:
        product_id = create_stripe_product(item)
    else:
        product_id = item.stripe_product_id
    
    price_id = create_stripe_price(item, product_id)
    return price_id


def buy(request, id):
    print("call buy", buy)
    if request.method == "GET":
        item = get_object_or_404(Item, id=id)
        
        price_id = get_stripe_price_id(item)
        
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
