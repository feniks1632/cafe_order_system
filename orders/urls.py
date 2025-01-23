from django.urls import path

from . import views


app_name = 'orders'


urlpatterns = [
    path('', views.order_list, name='order_list'),  # Список заказов
    path('order/<int:pk>/', views.order_detail, name='order_detail'),  # Детали заказа
    path('order/new/', views.order_create, name='order_create'),  # Создание заказа
    path('order/<int:pk>/edit/', views.order_update, name='order_edit'),  # Редактирование заказа
    path('order/<int:pk>/delete/', views.order_delete, name='order_delete'),  # Удаление заказа
    path('revenue/', views.revenue, name='revenue'),  # Доходы
]