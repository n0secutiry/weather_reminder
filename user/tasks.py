from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests

from .models import City

@shared_task
def send_email_task(user_email, subject, message):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False,
        )
    except Exception:
        pass

@shared_task
def send_webhook_task(webhook_url, payload_data):
    try:
        requests.post(webhook_url, json=payload_data, timeout=5)
    except Exception:
        pass

@shared_task
def process_weather_notifications():
    now = timezone.now()
    
    for city in City.objects.all():
        if not city.subscribers.exists():
            continue
            
        url = f"https://api.open-meteo.com/v1/forecast?latitude={city.lat}&longitude={city.lon}&current_weather=true"
            
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            weather_data = response.json()
            temp = weather_data.get('current_weather', {}).get('temperature', 'Unknown')
        except Exception:
            continue
            
        subject = f"Weather update for {city.name}"
        message = f"Hello! The current temperature in {city.name} is {temp}°C."
        webhook_payload = {"city": city.name, "temperature": temp, "event": "weather_update"}

        for user in city.subscribers.all():
            needs_notification = False
            
            if not getattr(user, 'last_notified', None):
                needs_notification = True
            elif getattr(user, 'mailing_interval', None):
                next_notification_time = user.last_notified + timedelta(hours=user.mailing_interval)
                if now >= next_notification_time:
                    needs_notification = True
            
            if needs_notification:
                send_email_task.delay(user.email, subject, message)
                
                if getattr(user, 'webhook_url', None):
                    send_webhook_task.delay(user.webhook_url, webhook_payload)
                
                user.last_notified = now
                user.save(update_fields=['last_notified'])