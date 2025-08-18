from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

router = DefaultRouter()
router.register(r'bookings',BookingViewSet,basename='booking')

urlpatterns = [
    path('',include(router.urls)),
    path('bookings/<int:booking_id>/confirm/', BookingViewSet.as_view({'post': 'confirm_booking'}), name='booking-confirm'),
    path('bookings/<int:booking_id>/reject/', BookingViewSet.as_view({'post': 'reject_booking'}), name='booking-reject'),
]