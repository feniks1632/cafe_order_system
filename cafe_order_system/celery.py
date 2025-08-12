# cafe_order_system/celery.py
import os
from celery import Celery
from decouple import config 
import django

# ✅ Устанавливаем DJANGO_SETTINGS_MODULE из .env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', config('DJANGO_SETTINGS_MODULE'))

# Инициализируем Django
django.setup()

# Создаём приложение Celery
app = Celery('cafe_order_system')

# Загружаем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автообнаружение задач в tasks.py приложений
app.autodiscover_tasks()