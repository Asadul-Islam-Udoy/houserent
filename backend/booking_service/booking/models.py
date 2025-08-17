from django.db import models
from decimal import Decimal
# Create your models here.


class Order(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    CONFIRM_STATUS=(
        ('waiting', 'Waiting for confirmation'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'), 
    )
    
    property_id = models.IntegerField()
    buyer_id = models.IntegerField()       # Auth Service user ID
    owner_id = models.IntegerField()  
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    advance_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    owner_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    admin_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    confirm_status = models.CharField(max_length=20, choices=CONFIRM_STATUS, default='waiting')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    
    def save(self,*args,**kwargs):
        self.remaining_amount = Decimal(self.total_price) - Decimal(self.advance_paid)
        owner_share = (self.total_price * Decimal('0.95'))
        admin_share = self.total_price - owner_share
        self.owner_amount = owner_share
        self.admin_amount = admin_share
        
        super().save(*args,**kwargs)
        
        def __str__(self):
            return f"Order for {self.property_id.title} by {self.buyer_id.username}"
        