import logging

import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Item, Order
from .stripeScripts import stripe_scripts

logger = logging.getLogger(__name__)

stripe.api_key = settings.SECRET_KEY_STRIPE
STRIPE_WEBHOOK_SECRET = settings.WEBHOOK_KEY_STRIPE

def build_checkout_urls(request):
    return {
        "success_url": request.build_absolute_uri(reverse("success")),
        "cancel_url": request.build_absolute_uri(reverse("cancel")),
    }

def main(request):
    return render(request, "main.html")

def success(request):
    return render(request, "success.html")

def cancel(request):
    return render(request, "cancel.html")

@require_GET
def pay_item(request, id):
    logger.debug(
        "pay_item() called for item_id=%s, method=%s, path=%s",
        id, request.method, request.path,
    )
    
    item = get_object_or_404(Item, id=id)   
    
    price_id = stripe_scripts.get_stripe_price_id(item)
    urls = build_checkout_urls(request)
    try:
        session = stripe.checkout.Session.create(
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            **urls,
        )
    except stripe.error.StripeError:
        logger.exception("Stripe error for item_id=%s", id)
        return JsonResponse({"error": "Не удалось установить корректное соединение с сервисом Stripe"}, status=502)

    return JsonResponse({"sessionUrl": session.url})


@require_GET
def item(request, id):
    logger.debug(
        "item() called for item_id=%s, method=%s, path=%s",
        id, request.method, request.path,
    )
    item_obj = get_object_or_404(Item, id=id)
    return render(request, "item.html", {"item":item_obj})

@require_GET 
def pay_order(request, id):
    logger.debug(
        "pay_order() called for order_id=%s, method=%s, path=%s",
        id, request.method, request.path,
    )
    order = get_object_or_404(Order, id=id)
    
    tax_id = None
    if order.tax:
        tax_id = stripe_scripts.get_stripe_tax_id(order.tax)
    
    items = list()
    currencies = set()

    for order_item in order.items.select_related("item").all():
        item = order_item.item
        price_id = stripe_scripts.get_stripe_price_id(item)

        item_data = {
            "price":price_id, 
            "quantity":order_item.quantity
        }

        if tax_id:
            item_data["tax_rates"] = [tax_id]

        items.append(item_data)
        currencies.add(item.currency)

    if not items:
        logger.warning("pay_order() called for empty order_id=%s", id)
        return JsonResponse({"error": "Заказ не содержит товаров."}, status=400)

    if len(currencies) > 1:
        logger.warning(
            "pay_order() called for order_id=%s, method=%s, path=%s. Order has multiple currencies: %s",
            id, request.method, request.path, currencies
        )
        return JsonResponse({"error": "В вашем заказе добавлены товары в разных валютах, оплата невозможна."}, status=400)

    currency = next(iter(currencies))

    discounts = list()
    if order.discount:
        discount_id = stripe_scripts.get_stripe_discount_id(order.discount, currency)
        if discount_id:
            discounts = [{"coupon":discount_id}]
        else:
            logger.warning(
                "Discount not configured in Stripe for order_id=%s, discount_id=%s",
                id, order.discount_id,
            )

    urls = build_checkout_urls(request)

    try:
        session = stripe.checkout.Session.create(
            line_items=items,
            mode="payment",
            discounts=discounts,
            **urls,
        )
    except stripe.error.StripeError:
        logger.exception("Stripe error for order_id=%s", id)
        return JsonResponse({"error": "Не удалось установить корректное соединение с сервисом Stripe"}, status=502)

    order._set_stripe_session_id(session.id)
    logger.info(
        "Stripe session created for order_id=%s, session_id=%s",
        id, session.id,
    )

    return JsonResponse({"sessionUrl": session.url})

@require_GET     
def order(request, id):
    logger.debug(
        "order() called for order_id=%s, method=%s, path=%s",
        id, request.method, request.path,
    )
    order = get_object_or_404(Order, id=id)
    if order.paid:
        return render(request, "paid_order.html", {"order":order})
    return render(request, "order.html", {"order":order})

@csrf_exempt    
@require_POST
def stripe_webhook(request):
    logger.debug(
        "stripe_webhook() called with params: method=%s, path=%s",
        request.method, request.path,
    )

    payload = request.body
    sig_header = request.headers.get('stripe-signature')

    if not STRIPE_WEBHOOK_SECRET:
        logger.error("Stripe endpoint_secret is not configured")
        return HttpResponse(status=500)

    if not sig_header:
        logger.error("Missing stripe-signature header in webhook request")
        return HttpResponse(status=400)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError as e:
        logger.exception("Webhook signature verification failed: %s", e)
        return HttpResponse(status=400)
        
    event_type = event.type

    if event_type == 'checkout.session.completed':
        session_id = event.data.object.id

        logger.info("checkout.session.completed, session_id=%s", session_id)

        try:
            order = Order.objects.get(stripe_session_id=session_id)
        except Order.DoesNotExist:
            logger.error(
                "Order with stripe_session_id=%s not found for webhook",
                session_id,
            )
            return HttpResponse(status=200)
        
        logger.info("Updating order status for order_id=%s", order.id)
        order._update_status()

    elif event_type == 'checkout.session.expired':
        session_id = event.data.object.id
        logger.info(
            "checkout.session.expired, session_id=%s",
            session_id
        )
    else:
        logger.info("Unhandled Stripe event type=%s", event_type)

    return HttpResponse(status=200)
