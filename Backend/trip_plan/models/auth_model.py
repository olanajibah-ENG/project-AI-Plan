from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # الخيارات المتاحة للأدوار
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    # الحقل الجديد كنص بدلاً من Boolean
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='user'
    )

    def __str__(self):
        return f"{self.username} - {self.role}"