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