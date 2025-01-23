from django.shortcuts import render, redirect, get_object_or_404

from .models import Order
from .services import OrderService


def order_list(request) -> render:
    """
    Список заказов.
    """
    return OrderService.order_list_request(request)


def order_detail(request, pk) -> render:
    """"
    Детали заказа.
    """
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/order_detail.html', {'order': order})


def order_create(request) -> render:
    """
    Создание нового заказа.
    """
    return OrderService.handle_order_request(
        request,
        template_name='orders/order_create.html',
        redirect_view='orders:order_detail'
    )


def order_update(request, pk) -> render:
    """
    Редактирование заказа.
    """
    order = get_object_or_404(Order, pk=pk)
    return OrderService.handle_order_request(
        request,
        order=order,
        template_name='orders/order_edit.html',
        redirect_view='orders:order_detail'
    )

def order_delete(requst, pk) -> redirect:
    """
    Удаление заказа.
    """
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    return redirect('orders:order_list')


def revenue(request) -> render:
    """
    Возвращает общую выручку.
    """
    return OrderService.revenue_request(request)


