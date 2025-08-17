from django.shortcuts import render
import requests
from django.conf import settings
from rest_framework import viewsets,status
from rest_framework.response import Response
from .simplejwt import JWTUserlessAuthentication
from .models import Payment
from .serializer import PaymentSerializer
from rest_framework.views import APIView
from .payment_method import bkash, nagad,paypal,stripe

ORDER_SERVICE_URL = settings.ORDER_SERVICE_URL


# Create your views here.
class PaymentViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTUserlessAuthentication]
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
     
    def create(self,request,*args,**kwargs):
        order_id = request.data.get('order_id')
        amount = request.data.get('amount')
        method = request.data.get('method')
        provider = request.data.get('provider')
        try:
            response = requests.get(f"{ORDER_SERVICE_URL}/orders/{order_id}/")
        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to connect Order Service", "details": str(e)},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
        if response.status_code !=200:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND) 
       
        order_data = response.josn()
        
        transaction_id = self.process_payment(provider, amount)
        
        payment = Payment.objects.create(
            order = order_id,
            amount = amount,
            method = method,
            transaction_id=transaction_id,
            status = 'escrow'
         )
         
        try:
            requests.patch(
                f"{ORDER_SERVICE_URL}/orders/{order_id}/",
                json={
                    "advance_paid": order_data.get("advance_paid", 0) + float(amount),
                    "payment_status": "partial"
                }
            )
        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Payment created but failed to update Order Service",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
     
     
    def process_payment(self, provider, amount):
            # Implement SDK/API calls here
        if provider == 'stripe':
            return stripe(amount)
        elif provider == 'paypal':
            return paypal(amount)
        elif provider == 'bkash':
            return bkash(amount)
        elif provider == 'nagad':
            return nagad(amount)
        else:
            raise ValueError("Invalid provider")
    
class OrderConfirmationView(APIView):
    def post(self, request, pk, action):
        order_id = pk
        if action == "confirm":
            try:
               requests.patch(
                f"{ORDER_SERVICE_URL}/orders/{order_id}/",
                json={
                    "confirm_status": 'confirmed',
                    "payment_status": "completed"
                }
               )
            except requests.exceptions.RequestException as e:
                return Response({
                "error": "Payment created but failed to update Order Service",
                "details": str(e)
               }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # release payment to seller
            Payment.objects.filter(order=order_id, status='escrow').update(status='released')

            return Response({"message": "Order confirmed, money released to seller."}, status=200)

        elif action == "reject":
                try:
                    requests.patch(
                    f"{ORDER_SERVICE_URL}/orders/{order_id}/",
                    json={
                        "confirm_status": "rejected",
                        "payment_status": "refunded"
                    }
                )
                except requests.exceptions.RequestException as e:
                    return Response({
                    "error": "Failed to update Order Service",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # refund payment to buyer
                Payment.objects.filter(order=order_id, status='escrow').update(status='refunded')

                return Response({"message": "Order rejected, money refunded to buyer."}, status=200)

        return Response({"error": "Invalid action"}, status=400)