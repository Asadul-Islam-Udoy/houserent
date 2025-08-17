from django.shortcuts import render
import requests
from django.conf import settings
from rest_framework import viewsets,status
from rest_framework.response import Response
from .simplejwt import JWTUserlessAuthentication
from .models import Order
from .serializer import OrderSerializer
from rest_framework.views import APIView

PROPERTY_SERVICE_URL = settings.PROPERTY_SERVICE_URL


# Create your views here.
class BookingViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTUserlessAuthentication]
    queryset = Order.objects.all();
    serializer_class = OrderSerializer
    
    def create(self,request,*args,**kwargs):
        property_id = request.data.get('property_id')
        if not property_id:
           return Response({"error": "property_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            response = requests.get(f"{PROPERTY_SERVICE_URL}/properties/{property_id}/")
        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to connect Property Service", "details": str(e)},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
      
        if response.status_code !=200:
            return Response({"error": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

        property_data = response.json()
        # --- Build order data ---
        order_data = {
            "property_id": property_id,
            "buyer_id": request.user.id,
            "owner_id": property_data.get("user_id"),
            "total_price": property_data.get("price"),
            "status": "pending",
        }  
        
        serializer = self.get_serializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
            
    

    