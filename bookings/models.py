from django.db import models


class Booking(models.Model):
    STATUS_CHOICES = [
        ('ON_HOLD', 'ON_HOLD'),
        ('PENDING', 'PENDING'),
        ('ACCEPTED', 'ACCEPTED'),
        ('COMPLETED', 'COMPLETED'),
        ('CANCELLED', 'CANCELLED'),
        ('EXPIRED', 'EXPIRED'),
        ('REJECTED', 'REJECTED'),
    ]
    
    id = models.CharField(max_length=50, primary_key=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    experience = models.CharField(max_length=255)
    rate = models.CharField(max_length=100)
    booking_created = models.DateTimeField()
    participants = models.PositiveIntegerField()
    original_currency = models.CharField(max_length=3)
    price_original_currency = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code or 'No code'} - {self.experience}"
    
    class Meta:
        ordering = ['-booking_created']
