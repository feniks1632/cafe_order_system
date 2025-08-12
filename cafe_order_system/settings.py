from dotenv import load_dotenv
import os
from pathlib import Path


load_dotenv()


# Корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent


# секретный ключ
SECRET_KEY = os.getenv('SECRET_KEY', 'default_key')


# При Разработки - True, при Деплое - False
DEBUG = os.getenv('DEBUG', 'False') == 'True'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Админ, которому приходят уведомления
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

# Разрешенные хосты
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split()

# Настройки приложений
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'rest_framework',
    'orders.apps.OrdersConfig',
    'api.apps.ApiConfig',
    'corsheaders',
    'drf_yasg',
]


# Настройки middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',  # Один раз
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# Настройки URL
ROOT_URLCONF = 'cafe_order_system.urls'


# Настройки шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Указывает на корневую папку templates
        'APP_DIRS': True,  # Разрешает Django искать шаблоны в папках приложений
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# для веб-сервиса(в проекте не реализовано)
WSGI_APPLICATION = 'cafe_order_system.wsgi.application'


# Настройки базы данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Язык и таймзоны
LANGUAGE_CODE = 'ru'

TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')

USE_I18N = True

USE_TZ = True


# Все для статики
STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Корневая папка для статических файлов

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'orders/static'),  # путь к статике приложения
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Пагинация и CORS для REST
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # Количество элементов на странице
}


CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",  # Заменить на адрес фронта если на разных портах(нужно для csrf)
]

# Разрешить отправку кук
CORS_ALLOW_CREDENTIALS = True


# Настройки Celery
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'  # RabbitMQ
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'         # Redis для хранения результатов

# Опционально: сериализация
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'Europe/Moscow'  

# Включить обработку периодических задач
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'