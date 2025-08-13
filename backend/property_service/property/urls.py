from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'properties',PropertyViewSet,basename='property')

urlpatterns = [
    path('',include(router.urls)),
]
