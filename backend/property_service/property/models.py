from django.db import models

# Create your models here.
class Property(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField()
    price = models.DecimalField(max_digits=12,decimal_places=2)
    location = models.CharField(max_length=255)
    owner_type = models.CharField(max_length=50,choices=(('rent','Rent'),('sell','Sell')))
    property_type = models.CharField(max_length=50,choices=(('house','House'),('townhouse','Townhouse'),('apartment','Apartment'),('roomonly','Room Only'),('bedonly','Bed Only')))
    rent_type = models.CharField(max_length=50,choices=(('hours','Hours'),('days','Days'),('months','Months'),('years','Years'),('none','None')),default='none')
    bedroom = models.IntegerField(blank=True,null=True)
    bathroom= models.IntegerField(blank=True,null=True)
    square = models.IntegerField(blank=True,null=True)
    laundry_type = models.CharField(max_length=50,choices=(('in_until_laundry','In_until laundry'),('laundry_in_building','Laundry in building'),('laundry_available','Laundry available'),('none','None')),default='none')
    parking_type = models.CharField(max_length=50,choices=(('garage_parking','Garage Parking'),('strest_parking','Street parking'),('off_street_parking','Off street parking'),('parking_available','Parking available'),('none','None')),default='none')
    air_conditioning_type = models.CharField(max_length=50,choices=(('central_ac','Central AC'),('ac_available','AC available'),('none','None')),default='none')
    heating_type = models.CharField(max_length=50,choices=(('central_heating','Central heating'),('electric_heating','Electric heating'),('gas_heating','Gas heating'),('radiator_heating','Radiator heating'),('heating_available','Heating available'),('none','None')),default='none')
    user_id = models.IntegerField()
    video = models.FileField(upload_to='properties/videos/',blank=True,null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
    
class PropertyImage(models.Model):
    property = models.ForeignKey(Property,related_name='image',on_delete=models.CASCADE)
    image = models.ImageField(upload_to='properties/')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Image for {self.property.title}"