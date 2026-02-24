from django.db import models

class Destination(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    flight_cost = models.DecimalField(max_digits=10, decimal_places=2) # كلفة الطيران
    daily_living_cost = models.DecimalField(max_digits=10, decimal_places=2) # معيشة بدون فندق
    is_coastal = models.BooleanField(default=False) # منطقة ساحلية
    description = models.TextField()
    best_seasons = models.CharField(
        max_length=100,
        blank=True,
        help_text="مثال: صيف,ربيع أو شتاء,خريف"
    )

class Hotel(models.Model):
    destination = models.ForeignKey(Destination, related_name='hotels', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)]) # فخامة
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    is_sea_view = models.BooleanField(default=False) # مطل على البحر

class Event(models.Model):
    destination = models.ForeignKey(Destination, related_name='events', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    season = models.CharField(max_length=50, choices=[
        ('summer', 'صيف'), ('winter', 'شتاء'), ('spring', 'ربيع'), ('autumn', 'خريف'), ('all', 'كل المواسم')
    ])
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_hours = models.PositiveIntegerField(default=2)
    is_free = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.destination.name}"

class ImageAsset(models.Model):
    destination = models.ForeignKey(Destination, null=True, blank=True, on_delete=models.CASCADE, related_name='dest_images')
    hotel = models.ForeignKey(Hotel, null=True, blank=True, on_delete=models.CASCADE, related_name='hotel_images')
    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.CASCADE, related_name='event_images')
    file = models.ImageField(upload_to='travel_assets/')

class ConversationSession(models.Model):
    """حفظ حالة المحادثة للمستخدم"""
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='conversations')
    session_id = models.CharField(max_length=100, unique=True)
    state = models.JSONField(default=dict)  # حفظ المتطلبات المجمعة
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']