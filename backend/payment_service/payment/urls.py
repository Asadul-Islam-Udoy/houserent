from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet,ConfirmPaymentView,RefundPaymentView,StripeWebhookView

router = DefaultRouter()
router.register(r'payments',PaymentViewSet,basename='payment')

urlpatterns = [
    path('',include(router.urls)),
    path("confirm/", ConfirmPaymentView.as_view(), name="confirm-payment"),
    path("refund/", RefundPaymentView.as_view(), name="refund-payment"),
    path("webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]