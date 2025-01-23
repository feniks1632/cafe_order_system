from django.test import TestCase
from rest_framework import serializers

from orders.models import Order
from orders.services import OrderService


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['total_price']  # total_price вычисляется на бэкенде

    def get_fields(self):
        fields = super().get_fields()
        
        # Если это PUT или PATCH запрос, удаляем table_number и total_price из полей
        if self.context['request'].method in ['PUT', 'PATCH']:
            fields.pop('table_number', None)
            fields.pop('total_price', None)
        
        return fields

    def create(self, validated_data):
        # Вычисляем total_price на основе items
        items = validated_data.get('items', [])
        total_price = sum(float(item.get('price', 0)) for item in items)
        validated_data['total_price'] = total_price
        
        # Создаем заказ
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Удаляем table_number и total_price, если они есть
        validated_data.pop('table_number', None)
        validated_data.pop('total_price', None)

        # Получаем текущие блюда
        existing_items = instance.items

        # Получаем новые блюда
        new_items = validated_data.get('items', [])

        # Добавляем новые блюда к существующим
        updated_items = existing_items + new_items

        # Обновляем validated_data
        validated_data['items'] = updated_items

        # Пересчитываем total_price
        total_price = sum(float(item.get('price', 0)) for item in updated_items)
        instance.total_price = total_price

        # Сохраняем обновленные данные
        return super().update(instance, validated_data)

    def validate_table_number(self, value):
        """
        Проверка, что выбранный стол не занят.
        """
        occupied_tables = OrderService.get_occupied_tables()
        if value in occupied_tables:
            raise serializers.ValidationError("Стол уже занят.")
        return value

    def validate_status(self, value):
        """
        Проверка корректности статуса.
        """
        valid_statuses = ["waiting", "ready", "paid"]
        if value not in valid_statuses:
            raise serializers.ValidationError("Неверный статус заказа.")
        return value

    def validate_items(self, value):
        """
        Проверка, что список блюд не пустой.
        """
        if not value:
            raise serializers.ValidationError("Список блюд с ценами не может быть пустым.")
        
        for item in value:
            if not isinstance(item.get('name'), str):
                raise serializers.ValidationError("Название блюда должно быть строкой.")
            try:
                price = float(item.get('price'))
                if price <= 0:
                    raise serializers.ValidationError("Цена блюда должна быть положительной.")
            except (TypeError, ValueError):
                raise serializers.ValidationError("Цена блюда должна быть числом.")
        
        return value
    

"""Тесты для Сериализатора"""


class OrderSerializerTest(TestCase):
    def setUp(self):
        # Создаем заказ, чтобы стол был занят
        Order.objects.create(
            table_number=1,
            items=[{"name": "Coffee", "price": 5.00}],
            total_price=5.00,
            status='waiting'
        )

    def test_table_number_validation(self):
        # Данные для создания заказа с занятым столом
        data = {
            'table_number': 1,  # Стол уже занят
            'items': [{"name": "Tea", "price": 3.00}],
            'status': 'waiting'
        }

        # Создаем сериализатор
        serializer = OrderSerializer(data=data)

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
            'status': 'invalid_status'  # Неверный статус
        }

        # Создаем сериализатор
        serializer = OrderSerializer(data=data)

        # Проверяем, что сериализатор невалиден
        self.assertFalse(serializer.is_valid())

        # Проверяем, что ошибка связана со статусом
        self.assertIn('status', serializer.errors)
        self.assertEqual(serializer.errors['status'][0], "Неверный статус заказа.")

    def test_items_validation(self):
    # Данные для создания заказа с пустым списком блюд
        data = {
            'table_number': 2,
            'items': [],  # Пустой список блюд
            'status': 'waiting'
        }

        # Создаем сериализатор
        serializer = OrderSerializer(data=data)

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

        # Создаем сериализатор
        serializer = OrderSerializer(data=data)

        # Проверяем, что сериализатор невалиден
        self.assertFalse(serializer.is_valid())

        # Проверяем, что ошибки связаны с названиями и ценами блюд
        self.assertIn('items', serializer.errors)
        self.assertEqual(serializer.errors['items'][0], "Название блюда должно быть строкой.")
        self.assertEqual(serializer.errors['items'][1], "Цена блюда не может быть отрицательной или равной нулю.")
        self.assertEqual(serializer.errors['items'][2], "Цена блюда должна быть числом.")

    def test_successful_order_creation(self):
    # Валидные данные для создания заказа
        data = {
            'table_number': 2,
            'items': [{"name": "Tea", "price": 3.00}],
            'status': 'waiting'
        }

        # Создаем сериализатор
        serializer = OrderSerializer(data=data)

        # Проверяем, что сериализатор валиден
        self.assertTrue(serializer.is_valid())

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

        # Новые данные для обновления заказа
        updated_data = {
            'table_number': 2,
            'items': [{"name": "Tea", "price": 3.00}],
            'status': 'ready'
        }

        # Создаем сериализатор с существующим заказом
        serializer = OrderSerializer(instance=order, data=updated_data)

        # Проверяем, что сериализатор валиден
        self.assertTrue(serializer.is_valid())

        # Сохраняем обновленный заказ
        updated_order = serializer.save()

        # Проверяем, что заказ был обновлен
        self.assertEqual(updated_order.table_number, 2)
        self.assertEqual(updated_order.items, [{"name": "Tea", "price": 3.00}])
        self.assertEqual(updated_order.total_price, 3.00)
        self.assertEqual(updated_order.status, 'ready')