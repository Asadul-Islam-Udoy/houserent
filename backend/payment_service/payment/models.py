from django.db import models

# Create your models here.
class Payment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile_banking', 'Mobile Banking'),
    )
    order = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=(
        ('escrow', 'Held by Admin'),
        ('released', 'Released to Seller'),
        ('refunded', 'Refunded to Buyer'),
        ('failed', 'Failed'),
    ), default='escrow')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
     
    def __str__(self):
        return f"Payment {self.amount} for Order {self.order.id} ({self.status})"