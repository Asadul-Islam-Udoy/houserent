
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

def stripe_payment(amount,order_id):
    intent = stripe.PaymentIntent.create(
        amount=int(float(amount) * 100),  # Stripe works in cents
        currency="usd",
        metadata={"order_id": order_id},
        automatic_payment_methods={"enabled": True},
    )
    return intent

def stripe_confirm(transaction_id):
    intent = stripe.PaymentIntent.confirm(transaction_id)
    return intent["status"]


def stripe_refund(transaction_id, amount=None):
    refund = stripe.Refund.create(
        payment_intent=transaction_id,
        amount=int(float(amount) * 100) if amount else None,
    )
    return refund["status"]