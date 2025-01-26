from django.contrib.messages.storage.fallback import FallbackStorage
from unittest.mock import patch
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
import pytest

from api.serializers import OrderSerializer
from orders.services import OrderService, WorkerOrderService
from .models import Order, Worker


"""Тесты для Модели"""

class OrderModelTest(TestCase):

    def tearDown(self):
        # Удаляем все заказы после теста
        Order.objects.all().delete()

    def test_create_order(self):
        """
        Тест создания заказа.
        """
        order = Order.objects.create(
            table_number=1,
            items=[{"name": "Coffee", "price": 5.00}],
            total_price=5.00,
            status='waiting'
        )
        self.assertEqual(order.table_number, 1)
        self.assertEqual(order.status, 'waiting')

    def test_update_order(self):
        """
        Тест изменения заказа.
        """
        # Создаем заказ
        order = Order.objects.create(
            table_number=1,
            items=[{"name": "Coffee", "price": 5.00}],
            total_price=5.00,
            status='waiting'
        )

        # Изменяем заказ
        order.table_number = 2
        order.items = [{"name": "Tea", "price": 3.00}]
        order.total_price = 3.00
        order.status = 'ready'
        order.save()

        # Получаем обновленный заказ из базы данных
        updated_order = Order.objects.get(pk=order.pk)

        # Проверяем, что изменения сохранились
        self.assertEqual(updated_order.table_number, 2)
        self.assertEqual(updated_order.items, [{"name": "Tea", "price": 3.00}])
        self.assertEqual(updated_order.total_price, 3.00)
        self.assertEqual(updated_order.status, 'ready')

    def test_delete_order(self):
        """
        Тест удаления заказа.
        """
        # Создаем заказ
        order = Order.objects.create(
            table_number=1,
            items=[{"name": "Coffee", "price": 5.00}],
            total_price=5.00,
            status='waiting'
        )
        order_pk = order.pk  # Сохраняем ID заказа

        # Удаляем заказ
        order.delete()

        # Проверяем, что заказ больше не существует в базе данных
        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(pk=order_pk)



"""Тесты для сервисного слоя"""

class OrderCreateTest(TestCase):
    def setUp(self):
        # Создаем mock-объект request
        self.factory = RequestFactory()

    def tearDown(self):
        # Удаляем все заказы после теста
        Order.objects.all().delete()

    def test_order_creation(self):
        # Данные для создания заказа
        data = {
            'table_number': 1,
            'items': [{"name": "Coffee", "price": 5.00}],
            'status': 'waiting'
        }

        # Создаем mock-запрос с POST-данными
        request = self.factory.post('/fake-url/', data={
            'table_number': 1,
            'dish_name_0': 'Coffee',
            'dish_price_0': '5.00',
            'status': 'waiting'
        })

        # Создаем заказ через сервисный слой
        order = OrderService.create_order_from_request(
            request=request,
            cleaned_data=data
        )

        # Проверяем, что заказ был создан
        self.assertIsNotNone(order)
        self.assertEqual(Order.objects.count(), 1)

        # Проверяем, что данные заказа соответствуют ожидаемым
        self.assertEqual(order.table_number, 1)
        self.assertEqual(order.items, [{"name": "Coffee", "price": 5.00}])
        self.assertEqual(order.total_price, 5.00)
        self.assertEqual(order.status, 'waiting')


class OrderListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.order = Order.objects.create(
            table_number=1,
            items=[{"name": "Coffee", "price": 5.00}],
            total_price=5.00,
            status='waiting'
        )

    def test_order_list_view(self):
        response = self.client.get(reverse('orders:order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coffee")  # Проверяем, что заказ отображается


class OrderUpdateTest(TestCase):
    def setUp(self):
        # Создаем mock-объект request
        self.factory = RequestFactory()

        # Создаем заказ для обновления
        self.order = Order.objects.create(
            table_number=1,
            items=[{"name": "Coffee", "price": 5.00}],
            total_price=5.00,
            status='ready'
        )

    def tearDown(self):
        # Удаляем все заказы после теста
        Order.objects.all().delete()

    def test_order_update(self):
        # Новые данные для обновления заказа
        updated_data = {
            'table_number': 2,
            'items': [{"name": "Tea", "price": 3.00}],
            'status': 'ready'
        }

        # Создаем mock-запрос с POST-данными
        request = self.factory.post('/fake-url/', data={
            'table_number': 2,
            'dish_name_0': 'Tea',
            'dish_price_0': '3.00',
            'status': 'ready'
        })

        # Обновляем заказ через сервисный слой
        updated_order = OrderService.update_order_from_request(
            request=request,
            order=self.order,
            cleaned_data=updated_data
        )

        # Проверяем, что заказ был обновлен
        self.assertIsNotNone(updated_order)
        self.assertEqual(Order.objects.count(), 1)

        # Проверяем, что данные заказа соответствуют новым значениям
        self.assertEqual(updated_order.table_number, 2)
        self.assertEqual(updated_order.items, [{'name': 'Coffee', 'price': 5.0}, {"name": "Tea", "price": 3.00}])
        self.assertEqual(updated_order.total_price, 8.00)
        self.assertEqual(updated_order.status, 'ready')


class OrderDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.order = Order.objects.create(
            table_number=1,
            items=[{"name": "Coffee", "price": 5.00}],
            total_price=5.00,
            status='waiting'
        )

    def test_order_detail_view(self):
        response = self.client.get(reverse('orders:order_detail', args=[self.order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coffee")  # Проверяем, что заказ отображается


class RevenueViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаем оплаченные заказы для расчета выручки
        Order.objects.create(
            table_number=1,
            items=[{"name": "Coffee", "price": 5.00}],
            total_price=5.00,
            status='paid'
        )
        Order.objects.create(
            table_number=2,
            items=[{"name": "Tea", "price": 3.00}],
            total_price=3.00,
            status='paid'
        )

    def tearDown(self):
        # Удаляем все заказы после теста
        Order.objects.all().delete()

    def test_revenue_view(self):
        response = self.client.get(reverse('orders:revenue'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 8)  # Проверяем, что выручка корректна


class OrderDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.order = Order.objects.create(
            table_number=1,
            items=[{"name": "Coffee", "price": 5.00}],
            total_price=5.00,
            status='waiting'
        )

    def test_order_delete(self):
        response = self.client.post(reverse('orders:order_delete', args=[self.order.pk]))
        self.assertEqual(response.status_code, 302)  # Проверяем редирект
        self.assertEqual(Order.objects.count(), 0)  # Проверяем, что заказ удален



"""Тесты для Сериализатора"""

class OrderSerializerTest(TestCase):
    def setUp(self):
        # Создаем фабрику запросов
        self.factory = RequestFactory()

        # Создаем заказ, чтобы стол был занят
        Order.objects.create(
            table_number=1,
            items=[{"name": "Coffee", "price": 5.00}],
            total_price=5.00,
            status='waiting'
        )

    def tearDown(self):
        # Удаляем все заказы после теста
        Order.objects.all().delete()

    def test_table_number_validation(self):
        # Данные для создания заказа с занятым столом
        data = {
            'table_number': 1,  # Стол уже занят
            'items': [{"name": "Tea", "price": 3.00}],
            'status': 'waiting'
        }

        # Создаем объект запроса с методом POST
        request = self.factory.post('/fake-url/', data=data, content_type='application/json')

        # Создаем сериализатор с контекстом запроса
        serializer = OrderSerializer(data=data, context={'request': request})

        # Проверяем, что сериализатор невалиден
        self.assertFalse(serializer.is_valid())

        # Проверяем, что ошибка связана с номером стола
        self.assertIn('table_number', serializer.errors)
        self.assertEqual(serializer.errors['table_number'][0], "Стол уже занят.")

    def test_status_validation(self):
        # Данные для создания заказа с неверным статусом
        data = {
            'table_number': 2,
            'items': [{"name": "Tea", "price": 3.00}],
            'status': 'invalid'  # Неверный статус
        }

        # Создаем объект запроса с методом POST
        request = self.factory.post('/fake-url/', data=data, content_type='application/json')

        # Создаем сериализатор с контекстом запроса
        serializer = OrderSerializer(data=data, context={'request': request})

        # Проверяем, что сериализатор невалиден
        self.assertFalse(serializer.is_valid())

        # Выводим ошибки для отладки
        print(serializer.errors)  # Добавьте эту строку

        # Проверяем, что ошибка связана со статусом
        self.assertIn('status', serializer.errors)
        
        # Ожидаемое стандартное сообщение Django
        expected_error_message = f"Значения {data['status']} нет среди допустимых вариантов."
        self.assertEqual(serializer.errors['status'][0], expected_error_message)

    def test_items_validation(self):
        # Данные для создания заказа с пустым списком блюд
        data = {
            'table_number': 2,
            'items': [],  # Пустой список блюд
            'status': 'waiting'
        }

        # Создаем объект запроса с методом POST
        request = self.factory.post('/fake-url/', data=data, content_type='application/json')

        # Создаем сериализатор с контекстом запроса
        serializer = OrderSerializer(data=data, context={'request': request})

        # Проверяем, что сериализатор невалиден
        self.assertFalse(serializer.is_valid())

        # Проверяем, что ошибка связана со списком блюд
        self.assertIn('items', serializer.errors)
        self.assertEqual(serializer.errors['items'][0], "Список блюд с ценами не может быть пустым.")

    def test_items_name_and_price_validation(self):
        # Данные для создания заказа с некорректными названиями и ценами блюд
        data = {
            'table_number': 2,
            'items': [
                {"name": 123, "price": 5.00},  # Название не является строкой
                {"name": "Tea", "price": -1.00},  # Отрицательная цена
                {"name": "Coffee", "price": "invalid_price"}  # Цена не является числом
            ],
            'status': 'waiting'
        }

        # Создаем объект запроса с методом POST
        request = self.factory.post('/fake-url/', data=data, content_type='application/json')

        # Создаем сериализатор с контекстом запроса
        serializer = OrderSerializer(data=data, context={'request': request})

        # Проверяем, что сериализатор невалиден
        self.assertFalse(serializer.is_valid())

        # Проверяем, что ошибки связаны с названиями и ценами блюд
        errors = serializer.errors.get('items', [])

        # Ошибки для items возвращаются в виде списка, где каждый элемент — это ошибка для конкретного блюда
        # Например: [{"name": ["Название блюда должно быть строкой."]}, {"price": ["Цена блюда должна быть числом."]}]

        # Проверяем наличие каждой ошибки в списке
        for error in errors:
            if "name" in error:
                self.assertIn("Название блюда должно быть строкой.", error["name"][0])
            if "price" in error:
                if "invalid_price" in str(error["price"]):
                    self.assertIn("Цена блюда должна быть числом.", error["price"][0])
                elif "-1.00" in str(error["price"]):
                    self.assertIn("Цена блюда не может быть отрицательной или равной нулю.", error["price"][0])

    def test_successful_order_creation(self):
        # Валидные данные для создания заказа
        data = {
            'table_number': 2,
            'items': [{"name": "Tea", "price": 3.00}],
            'status': 'waiting'
        }

        # Создаем объект запроса с методом POST
        request = self.factory.post('/fake-url/', data=data, content_type='application/json')

        # Создаем сериализатор с контекстом запроса
        serializer = OrderSerializer(data=data, context={'request': request})

        # Проверяем, что сериализатор валиден
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # Сохраняем заказ
        order = serializer.save()

        # Проверяем, что заказ был создан
        self.assertIsNotNone(order)
        self.assertEqual(order.table_number, 2)
        self.assertEqual(order.items, [{"name": "Tea", "price": 3.00}])
        self.assertEqual(order.total_price, 3.00)
        self.assertEqual(order.status, 'waiting')

    def test_order_update(self):
        # Создаем заказ для обновления
        order = Order.objects.create(
            table_number=1,
            items=[{"name": "Coffee", "price": 5.00}],
            total_price=5.00,
            status='waiting'
        )

        # Замокаем метод get_occupied_tables, чтобы он возвращал пустой список
        with patch('orders.services.OrderService.get_occupied_tables', return_value=[]):
            # Новые данные для обновления заказа
            updated_data = {
                'items': [{"name": "Tea", "price": 3.00}],
                'status': 'ready'
            }

            # Создаем объект запроса с методом PUT
            request = self.factory.put('/fake-url/', data=updated_data, content_type='application/json')

            # Создаем сериализатор с существующим заказом и передаем контекст запроса
            serializer = OrderSerializer(
                instance=order,
                data=updated_data,
                context={'request': request}  # Передаем объект запроса
            )

            # Проверяем, что сериализатор валиден
            self.assertTrue(serializer.is_valid(), serializer.errors)

            # Сохраняем обновленный заказ
            updated_order = serializer.save()

            # Проверяем, что заказ был обновлен
            self.assertEqual(updated_order.table_number, 1)  # table_number не должен измениться
            self.assertEqual(updated_order.items, [{"name": "Coffee", "price": 5.00}, {"name": "Tea", "price": 3.00}])  # Новое блюдо добавлено
            self.assertEqual(updated_order.total_price, 8.00)  # total_price пересчитан
            self.assertEqual(updated_order.status, 'ready')  # Статус обновлен


