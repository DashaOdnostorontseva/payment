from django.shortcuts import render
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed

from .models import Item, Order

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


def pay_item(request, id):
    print("call pay_item", pay_item)
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
    

def pay_order(request, id):
    if request.method == "GET":
        order = get_object_or_404(Order, id=id)
        items = list()

        for i in order.items.select_related("item").all():
            item = i.item
            price_id = get_stripe_price_id(item)

            items.append({"price":price_id, "quantity":i.quantity})

        session = stripe.checkout.Session.create(
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            line_items=items,
            mode="payment",
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
