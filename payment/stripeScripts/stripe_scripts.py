import logging

import stripe
from django.conf import settings

stripe.api_key = settings.SECRET_KEY_STRIPE

logger = logging.getLogger(__name__)

def create_stripe_product(item):
    logger.debug(
        "Creating Stripe product for item_name=%s",
        item.name
    )
    try:
        product = stripe.Product.create(name=item.name)
    except stripe.error.StripeError:
        logger.exception(
            "Failed to create Stripe product for item_name=%s",
            item.name
        )
        raise
    
    item._set_stripe_product_id(product.id)

    logger.info(
        "Stripe product created for item_id=%s, stripe_product_id=%s",
        item.id, product.id
    )

    return product.id
    
def create_stripe_price(item, product_id):
    logger.debug(
        "Creating Stripe price for product_id=%s and value=%s",
        product_id, item.price * 100
    )
    try:
        price = stripe.Price.create(
            currency=item.currency,
            unit_amount=int(item.price * 100),
            product=product_id
        )
    except stripe.error.StripeError:
        logger.exception(
            "Failed to create Stripe price for product_id=%s and value=%s",
            product_id, item.price * 100
        )
        raise

    item._set_stripe_price_id(price.id)

    logger.info(
        "Stripe price created for item_id=%s, stripe_price_id=%s",
        item.id, price.id
    )

    return price.id


def get_stripe_price_id(item):
    if item.stripe_price_id:
        return item.stripe_price_id
    
    product_id = item.stripe_product_id or create_stripe_product(item)
    price_id = create_stripe_price(item, product_id)
    
    return price_id

def create_stripe_tax_id(tax):
    logger.debug(
        "Creating Stripe tax for tax_name=%s and tax_percent=%s",
        tax.name, tax.percent
    )
    try:
        tax_rate = stripe.TaxRate.create(
            display_name=tax.name,
            percentage=tax.percent,
            inclusive=False,
        )
    except stripe.error.StripeError:
        logger.exception(
            "Failed to create Stripe tax for tax_name=%s and tax_percent=%s",
            tax.name, tax.percent
        )
        raise

    tax._set_stripe_tax_id(tax_rate.id)

    logger.info(
        "Stripe tax created for tax_name=%s and tax_percent=%s",
        tax.name, tax.percent
    )

    return tax_rate.id


def get_stripe_tax_id(tax):  
    tax_id = tax.stripe_tax_id or create_stripe_tax_id(tax)

    return tax_id

def create_stripe_discount_id(discount):
    logger.debug(
        "Creating Stripe discount for discount_name=%s and discount_amont=%s",
        discount.name, discount.amount * 100
    )
    try:
        coupon = stripe.Coupon.create(
            name=discount.name,
            amount_off=int(discount.amount * 100),
            currency=discount.currency
        )
    except stripe.error.StripeError:
        logger.exception(
            "Failed to create Stripe discount for discount_name=%s and discount_amont=%s",
            discount.name, discount.amount * 100
        )
        raise

    discount._set_stripe_discount_id(coupon.id)

    logger.info(
        "Stripe discount created for discount_name=%s and discount_amont=%s",
        discount.name, discount.amount * 100
    )

    return coupon.id

def get_stripe_discount_id(discount, currency):
    if (discount.currency != currency):
        logger.warning("Cannot get Stripe discount_id because currency of Order and currency of Discount are different")
        return None
    
    stripe_discount_id = discount.stripe_discount_id or create_stripe_discount_id(discount)

    return stripe_discount_id
