# orders/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

@shared_task
def notify_admin_worker_login(worker_identifier, timestamp, ip_address=None):
    subject = f" Работник {worker_identifier}: вошёл в систему. "
    message = (
        f"Сотрудник с идентификатором: {worker_identifier}\n"
        f"Время входа: {timestamp}\n"
        f"IP-адрес: {ip_address or 'неизвестен'}\n"
        f"Система: Управление кафе"
    )
    recipient_list = [settings.ADMIN_EMAIL]

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )
    return f"Уведомление отправлено для {worker_identifier}"