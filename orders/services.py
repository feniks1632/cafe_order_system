from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import OrderForm, OrderSearchForm, WorkerLoginForm
from .models import Order, Worker


class OrderService:
    @staticmethod
    def get_occupied_tables() -> list[int]:
        """
        Возвращает список занятых столов.
        """
        return Order.objects.filter(status__in=['waiting', 'ready', 'paid']).values_list('table_number', flat=True)

    @staticmethod
    def process_dishes(request, existing_items=None) -> list:
        """
        Обрабатывает блюда из запроса.
        Если переданы existing_items, исключает дубликаты.
        """
        items = []
        
        # Обработка существующих блюд
        i = 0
        while f'dish_name_{i}' in request.POST:
            name = request.POST[f'dish_name_{i}']
            price = request.POST[f'dish_price_{i}']
            if name and price:  # Проверяем, что поля не пустые
                # Проверяем, что блюдо ещё не добавлено
                if not existing_items or not any(
                    item['name'] == name and item['price'] == float(price) 
                    for item in existing_items
                ):
                    items.append({'name': name, 'price': float(price)})
            i += 1

        # Обработка новых блюд
        j = 0
        while f'new_dish_name_{j}' in request.POST:
            name = request.POST[f'new_dish_name_{j}']
            price = request.POST[f'new_dish_price_{j}']
            if name and price:  # Проверяем, что поля не пустые
                # Проверяем, что блюдо ещё не добавлено
                if not existing_items or not any(
                    item['name'] == name and item['price'] == float(price) 
                    for item in existing_items
                ):
                    items.append({'name': name, 'price': float(price)})
            j += 1

        return items

    @staticmethod
    def create_order_from_request(request, cleaned_data) -> Order:
        """
        Создает заказ на основе данных из запроса.
        """
        table_number = cleaned_data.get('table_number')
        occupied_tables = OrderService.get_occupied_tables()

        if table_number in occupied_tables:
            raise ValueError(f'Стол {table_number} уже занят. Выберите другой стол.')

        items = OrderService.process_dishes(request)
        if not items:
            raise ValueError('В заказе должна быть хотя бы одна позиция.')

        order = Order.objects.create(
            table_number=table_number,
            items=items,
            total_price=sum(item['price'] for item in items),
            status='waiting',  # Пример статуса по умолчанию
        )
        return order  # Возвращаем созданный заказ

    @staticmethod
    def update_order_from_request(request, order, cleaned_data) -> Order:
        """
        Обновляет заказ на основе данных из запроса.
        Новые блюда добавляются к существующим, исключая дубликаты.
        """
        # Получаем новые блюда, исключая те, которые уже есть в заказе
        new_items = OrderService.process_dishes(request, existing_items=order.items)
        
        # Если новые блюда переданы, добавляем их к существующим
        if new_items:
            order.items.extend(new_items)  # Добавляем только новые блюда

        # Проверяем, что в заказе есть хотя бы одна позиция
        if not order.items:
            raise ValueError('В заказе должна быть хотя бы одна позиция.')

        # Обновляем данные заказа
        order.table_number = cleaned_data.get('table_number')
        order.total_price = sum(item['price'] for item in order.items)
        order.save()
        return order
    
    @staticmethod
    def handle_order_request(request, order=None, template_name=None, redirect_view=None):
        """
        Обрабатывает запросы для создания или обновления заказа.
        """
        if request.method == 'POST':
            form = OrderForm(request.POST, instance=order)
            if form.is_valid():
                try:
                    if order:
                        order = OrderService.update_order_from_request(request, order, form.cleaned_data)
                    else:
                        order = OrderService.create_order_from_request(request, form.cleaned_data)
                    
                    if order is None:
                        raise ValueError("Не удалось создать или обновить заказ.")
                    
                    return redirect(redirect_view, pk=order.pk)
                except ValueError as e:
                    messages.error(request, str(e))
        else:
            form = OrderForm(instance=order)

        return render(request, template_name, {
            'form': form,
            'dishes': order.items if order else [],
            'order': order,
        })

    @staticmethod
    def order_list_request(request) -> render:
        """
        Обрабатывает запросы для списка заказов.
        """
        form = OrderSearchForm(request.GET or None)
        orders = Order.objects.all()
        search_performed = False  # Флаг, указывающий, был ли выполнен поиск

        if form.is_valid():
            query = form.cleaned_data.get('query', '').strip()
            if query:
                search_performed = True  # Меняем флаг на True(поиск выполнен)
                orders = form.filter_queryset(orders)  # Фильтруем заказы

        return render(request, 'orders/order_list.html', {
            'orders': orders,
            'search_form': form,
            'search_performed': search_performed,  # Передаём флаг в шаблон
        })


"""Логика работы с заказами для работника"""
class WorkerOrderService(OrderService):
    @staticmethod
    def worker_update_order_from_request(request, order, template_name=None, redirect_view=None):
        if request.method == 'POST':
            if not request.session.get('worker_id'):
                messages.error(request, "Вы не авторизованы как работник.")
                return redirect('orders:worker_login')

            form = OrderForm(request.POST, instance=order)
            if form.is_valid():
                try:
                    # Получаем индексы блюд для удаления
                    remove_indices = request.POST.get('remove_dishes', '').split(',')
                    remove_indices = [int(idx) for idx in remove_indices if idx.strip()]

                    # Удаляем блюда по индексам
                    if remove_indices:
                        order.items = [item for idx, item in enumerate(order.items) if idx not in remove_indices]

                    # Обрабатываем новые блюда
                    new_items = OrderService.process_dishes(request, existing_items=order.items)
                    if new_items:
                        order.items.extend(new_items)

                    # Проверяем, что в заказе есть хотя бы одна позиция
                    if not order.items:
                        raise ValueError('В заказе должна быть хотя бы одна позиция.')
                    
                    # Обновляем данные заказа
                    order.table_number = form.cleaned_data.get('table_number')
                    order.status = form.cleaned_data.get('status')  # Обновляем статус
                    order.total_price = sum(item['price'] for item in order.items)

                    # Сохраняем заказ
                    order.save(update_fields=['items', 'table_number', 'total_price', 'status'])  # Явно указываем поля для обновления
                    messages.success(request, "Заказ успешно обновлен.")
                    return redirect(redirect_view, pk=order.id)
                except ValueError as e:
                    messages.error(request, str(e))
            else:
                print("Форма невалидна:", form.errors)
        else:
            form = OrderForm(instance=order)

        return render(request, template_name, {
            'form': form,
            'order': order,
            'dishes': order.items,
        })

    def worker_logout_request(request) -> redirect:
        """
        Выход работника из системы.
        """
        if 'worker_id' in request.session:
            del request.session['worker_id']
        return redirect('orders:order_list')

    @staticmethod
    def revenue_request(request) -> render:
        """
        Обрабатывает запросы для расчета выручки.
        """
        paid_orders = Order.objects.filter(status='paid')
        total_revenue = sum(order.total_price for order in paid_orders)
        return render(request, 'orders/revenue.html', {'total_revenue': total_revenue})

    def worker_login_request(request):
        """
        Обрабатывает запросы для авторизации работника.
        """
        if request.method == 'POST':
            form = WorkerLoginForm(request.POST)
            if form.is_valid():
                identifier = form.cleaned_data['identifier']
                password = form.cleaned_data['password']

                try:
                    worker = Worker.objects.get(identifier=identifier)
                    if worker.check_password(password):
                        # Сохраняем идентификатор работника в сессии
                        request.session['worker_id'] = worker.id
                        request.session['worker_identifier'] = worker.identifier 
                        messages.success(request, "Вы успешно авторизовались!")
                        return redirect('orders:order_list')  # Используем именованный URL-адрес
                    else:
                        messages.error(request, "Неверный пароль.")
                except Worker.DoesNotExist:
                    messages.error(request, "Работник с таким идентификатором не найден.")
        else:
            form = WorkerLoginForm()

        return render(request, 'workers/login.html', {'form': form})
