from django.shortcuts import render
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed

from .models import Item, Order

stripe.api_key = settings.SECRET_KEY_STRIPE

def main(request):
    return render(request, "main.html")

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
    
def get_stripe_tax_ids(tax):
    if tax.stripe_tax_id:
        return tax.stripe_tax_id
    
    tax_rate = stripe.TaxRate.create(
        display_name=tax.name,
        percentage=tax.percent,
        inclusive=False,
    )

    tax._set_stripe_tax_id(tax_rate.id)

    return tax_rate.id

def get_stripe_discount_id(discount):
    if discount.stripe_discount_id:
        return discount.stripe_discount_id
    
    coupon = stripe.Coupon.create(
        name=discount.name,
        amount_off=int(discount.amount * 100),
        currency="rub"
    )

    discount._set_stripe_discount_id(coupon.id)

    return coupon.id

def pay_order(request, id):
    if request.method == "GET":
        order = get_object_or_404(Order, id=id)
        items = list()
        tax_id = None
        discount_id = None

        if order.tax:
            tax_id = get_stripe_tax_ids(order.tax)
        
        if order.discount:
            discount_id = get_stripe_discount_id(order.discount)

        for i in order.items.select_related("item").all():
            item = i.item
            price_id = get_stripe_price_id(item)

            item_data = {"price":price_id, "quantity":i.quantity}

            if tax_id:
                item_data["tax_rates"] = [tax_id]

            items.append(item_data)

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
