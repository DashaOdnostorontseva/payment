from django.shortcuts import render
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse

from django.views.decorators.csrf import csrf_exempt

from .models import Item, Order
from .stripeScripts import scripts as stripeScript

import json

stripe.api_key = settings.SECRET_KEY_STRIPE
endpoint_secret = settings.WEBHOOK_KEY_STRIPE

def main(request):
    return render(request, "main.html")

def success(request):
    return render(request, "success.html")

def cancel(request):
    return render(request, "cancel.html")

def pay_item(request, id):
    print("call pay_item", pay_item)
    if request.method == "GET":
        item = get_object_or_404(Item, id=id)
        
        price_id = stripeScript.get_stripe_price_id(item)
        
        session = stripe.checkout.Session.create(
            success_url=request.build_absolute_uri("/success") ,
            cancel_url=request.build_absolute_uri("/cancel"),
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
        
        tax_id = None
        if order.tax:
            tax_id = stripeScript.get_stripe_tax_ids(order.tax)
        
        items = list()
        currencies = set()
        for i in order.items.select_related("item").all():
            item = i.item
            price_id = stripeScript.get_stripe_price_id(item)

            item_data = {"price":price_id, "quantity":i.quantity}

            if tax_id:
                item_data["tax_rates"] = [tax_id]

            items.append(item_data)

            currencies.add(item.currency)

        if (len(currencies) > 1):
            return JsonResponse({"errorText": "В вашем заказе добавлены товары в разных валютах, оплата невозможна."})

        discount_id = None
        discounts = list()
        if order.discount:
            discount_id = stripeScript.get_stripe_discount_id(order.discount, list(currencies)[0])
            if discount_id:
                discounts = [{"coupon":discount_id}]

        session = stripe.checkout.Session.create(
            success_url=request.build_absolute_uri("/success") ,
            cancel_url=request.build_absolute_uri("/cancel"),
            line_items=items,
            mode="payment",
            discounts=discounts
        )

        order._set_stripe_session_id(session.id)

        return JsonResponse({"sessionUrl": session.url})
    else:
        return HttpResponseNotAllowed(["GET"])
    
def order(request, id):
    if request.method == "GET":
        order = get_object_or_404(Order, id=id)
        return render(request, "order.html", {"order":order})
    else:
        return HttpResponseNotAllowed(["GET"])

@csrf_exempt    
def stripe_webhook(request):
    print("stripe_webhook", stripe_webhook)
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
        print(event)
    except ValueError as e:
        # Invalid payload
        print("e: ", str(e))
        return HttpResponse(status=400)

    if endpoint_secret:
            # Only verify the event if you've defined an endpoint secret
            # Otherwise, use the basic event deserialized with JSON
            sig_header = request.headers.get('stripe-signature')
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, endpoint_secret
                )
                print("endpoint_secret", event)
            except stripe.error.SignatureVerificationError as e:
                print('Webhook signature verification failed.' + str(e))
                return HttpResponse(status=400)

    # Handle the event
    if event.type == 'checkout.session.completed':
        session = event.data.object # contains a stripe.PaymentIntent
        # Then define and call a method to handle the successful payment intent.
        # handle_payment_intent_succeeded(payment_intent)
        print("checkout.session.completed", session.id)
        order = Order.objects.get(stripe_session_id=session.id)
        print("order_id", order.id)
        order._update_status()
    elif event.type == 'checkout.session.expired':
        session = event.data.object # contains a stripe.PaymentMethod
        print("checkout.session.expired", session.id)
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)
