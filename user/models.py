from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    last_login = None
    first_name = None
    last_name = None
    email = models.EmailField(('email address'), unique=True)
    mailing_interval = models.IntegerField(default=24, help_text="Interval in hours", null=True)
    webhook_url = models.URLField(max_length=255, null=True, blank=True, help_text="URL to receive weather updates (optional)")
    last_notified = models.DateTimeField(null=True, blank=True, help_text="The last time the user was notified about the weather")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

class City(models.Model):
    name = models.CharField(max_length=100, unique=True, null=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    subscribers = models.ManyToManyField(CustomUser, related_name='cities', blank=True)

    def __str__(self):
        return self.name