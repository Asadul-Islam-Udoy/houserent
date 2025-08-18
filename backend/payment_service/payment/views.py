from django.shortcuts import render
from django.http import HttpResponse
import json, pika
import requests
from django.conf import settings
from rest_framework import viewsets,status
from rest_framework.response import Response
from .simplejwt import JWTUserlessAuthentication
from .models import Payment
from .serializer import PaymentSerializer
from rest_framework.views import APIView
from .payment_method.stripe_payment import stripe_confirm,stripe_payment,stripe_refund
from .payment_method.paypal_payment import paypal_payment,paypal_confirm,paypal_refund
from .payment_method.bkash_payment import bkash_payment,bkash_confirm,bkash_refund
from .payment_method.nagad_payment import nagad_payment,nagad_confirm,nagad_refund


ORDER_SERVICE_URL = settings.ORDER_SERVICE_URL


# RABBITMQ_URL = settings.RABBITMQ_URL

# def publish_event(event_type, data):
#     connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
#     channel = connection.channel()
#     channel.exchange_declare(exchange='microservice_exchange', exchange_type='fanout')
#     message = json.dumps({"event": event_type, "data": data})
#     channel.basic_publish(exchange='microservice_exchange', routing_key='', body=message)
#     connection.close()

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
        
        intent = self.process_payment(provider,amount,order_id)
        
        payment = Payment.objects.create(
            order = order_id,
            amount = amount,
            method = method,
            transaction_id=intent.id,
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
            
    #     publish_event("payment_completed", {
    #     "booking_id": data['booking_id'],
    #     "user_id": data['user_id'],
    #     "seller_id": data['seller_id'],
    #     "amount": amount
    # })
        
        return Response({ "clientSecret": intent.client_secret, "payment":PaymentSerializer(payment).data}, status=status.HTTP_201_CREATED)
     
     
    def process_payment(self, provider, amount ,order_id):
            # Implement SDK/API calls here
        if provider == 'stripe':
            return stripe_payment(amount,order_id)
        elif provider == 'paypal':
            return paypal_payment(amount,order_id)
        elif provider == 'bkash':
            return bkash_payment(amount,order_id)
        elif provider == 'nagad':
            return nagad_payment(amount,order_id)
        else:
            raise ValueError("Invalid provider")
    
    
    
class ConfirmPaymentView(APIView):
    def post(self, request):
        try:
            provider = request.data.get("provider")
            transaction_id = request.data.get("transaction_id")
            if provider == "stripe":
               status = stripe_confirm(transaction_id)
            elif provider == "paypal":
               status = paypal_confirm(transaction_id)
            elif provider == "bkash":
               status = bkash_confirm(transaction_id)
            elif provider == "nagad":
               status = nagad_confirm(transaction_id)
            else:
                return Response({"error": "Invalid provider"}, status=400)
            
            payment = Payment.objects.get(transaction_id=transaction_id)
            payment.status = status
            payment.save()
            
            # publish_event("payment_released", {
            #  "booking_id": data['booking_id'],
            #  "user_id": payment.user_id,
            #  "seller_id": payment.seller_id,
            #  "amount": float(payment.amount)
            # })
            
            return Response({"status": status})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RefundPaymentView(APIView):
    def post(self, request):
        try:
            provider = request.data.get("provider")
            transaction_id = request.data.get("transaction_id")
            amount = request.data.get("amount")
            if provider == "stripe":
                status = stripe_refund(transaction_id, amount)
            elif provider == "paypal":
                status = paypal_refund(transaction_id, amount)
            elif provider == "bkash":
                status = bkash_refund(transaction_id, amount)
            elif provider == "nagad":
                status = nagad_refund(transaction_id, amount)
            else:
                return Response({"error": "Invalid provider"}, status=400)
            payment = Payment.objects.get(transaction_id=transaction_id)
            payment.status = "refunded"
            payment.save()
        #     publish_event("payment_refunded", {
        #    "booking_id": data['booking_id'],
        #    "user_id": payment.user_id,
        #    "seller_id": payment.seller_id,
        #    "amount": float(payment.amount)
        #    })
            return Response({"status": status})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    # def start_consumer():
    #     connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    # channel = connection.channel()
    # channel.exchange_declare(exchange='microservice_exchange', exchange_type='fanout')
    # result = channel.queue_declare(queue='', exclusive=True)
    # queue_name = result.method.queue
    # channel.queue_bind(exchange='microservice_exchange', queue=queue_name)

    # def callback(ch, method, properties, body):
    #     message = json.loads(body)
    #     event = message['event']
    #     data = message['data']
    #     if event == "booking_created":
    #         handle_booking_created(data)
    #     elif event == "booking_confirmed":
    #         handle_booking_confirmed(data)
    #     elif event == "booking_rejected":
    #         handle_booking_rejected(data)

    # channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    # print("Payment Service listening...")
    # channel.start_consuming()    

class StripeWebhookView(APIView):
    def post(self, request):
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        # Handle events
        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            payment = Payment.objects.get(payment_intent_id=intent["id"])
            payment.status = "succeeded"
            payment.save()

        elif event["type"] == "payment_intent.payment_failed":
            intent = event["data"]["object"]
            payment = Payment.objects.get(payment_intent_id=intent["id"])
            payment.status = "failed"
            payment.save()

        return HttpResponse(status=200)
    
         

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
                
                
            # publish_event("order_confirmed", {"order_id": order_id})
            
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