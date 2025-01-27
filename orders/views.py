from django.shortcuts import render, redirect, get_object_or_404

from .models import Order
from .services import OrderService, WorkerOrderService


"""представления пользователя"""
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


def order_update(request, pk):
    """
    Редактирование заказа пользователем.
    """
    """
    Редактирование заказа.
    """
    order = get_object_or_404(Order, pk=pk)

    if request.session.get('worker_id'):
        # Если пользователь — работник, используем WorkerOrderService
        return WorkerOrderService.worker_update_order_from_request(
            request,
            order,
            template_name='orders/order_edit.html',
            redirect_view='orders:order_detail'
        )
    else:
        # Если пользователь не работник, используем OrderService
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


"""представления работника"""

def revenue(request) -> render:
    """
    Возвращает общую выручку.
    """
    return WorkerOrderService.revenue_request(request)


def worker_login(request) -> render:
    """
    Авторизация работника.
    """
    return WorkerOrderService.worker_login_request(request)


def worker_logout(request) -> redirect:
    """
    Выход работника из системы.
    """
    return WorkerOrderService.worker_logout_request(request)

