import stripe
from django.conf import settings

stripe.api_key = settings.SECRET_KEY_STRIPE

def create_stripe_product(item):
    print(create_stripe_product)
    product = stripe.Product.create(name=item.name)
    item._set_stripe_product_id(product.id)

    return product.id
    
def create_stripe_price(item, product_id):
    print(create_stripe_price)
    price = stripe.Price.create(
        currency=item.currency,
        unit_amount=int(item.price * 100),
        product=product_id
    )
    item._set_stripe_price_id(price.id)

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

def get_stripe_discount_id(discount, currency):
    if (discount.currency != currency):
        print("different currency")
        return
    
    if discount.stripe_discount_id:
        return discount.stripe_discount_id

    coupon = stripe.Coupon.create(
        name=discount.name,
        amount_off=int(discount.amount * 100),
        currency=discount.currency
    )

    discount._set_stripe_discount_id(coupon.id)

    return coupon.id
