from typing import Dict 

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import Order


class OrderForm(forms.ModelForm):
    """
    Форма для создания и редактирования заказа.
    """
    class Meta:
        model = Order
        fields = ['table_number', 'status']  # Включаем table_number

    def __init__(self, *args, **kwargs)-> None:
        super().__init__(*args, **kwargs)
        # Скрываем поле table_number при редактировании
        if self.instance.pk:  # Если заказ уже существует (редактирование)
            self.fields['table_number'].widget = forms.HiddenInput()

    def clean_table_number(self)-> int:
        table_number = self.cleaned_data.get('table_number')
        if table_number <= 0:
            raise ValidationError("Номер стола должен быть больше нуля.")
        return table_number        


class OrderSearchForm(forms.Form):
    """
    Форма для поиска заказов.
    """
    query = forms.CharField(
        label="Поиск заказов",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Введите номер стола, ID заказа или статус'})
    )
    
    def filter_queryset(self, queryset) -> Q:
        query = self.cleaned_data.get('query', '').strip()
        if not query:
            return queryset  # Если запрос пустой, возвращаем весь queryset

        q_objects = Q()  # Создаём пустой Q-объект

        # Проверяем, является ли запрос числом
        if query.isdigit():
            # Если число, ищем по table_number и id
            q_objects |= Q(table_number=int(query))  # Поиск по номеру стола
            q_objects |= Q(id=int(query))  # Поиск по ID заказа
        else:
            # Если строка, ищем по статусу (переводим русский запрос в английский статус)
            status_mapping: Dict[str, str] = {
                'в ожидании': 'waiting',
                'готов': 'ready',
                'оплачено': 'paid',
            }
            query_lower = query.lower()
            # Преобразуем русский запрос в английский статус
            status = status_mapping.get(query_lower, query_lower)
            q_objects |= Q(status__iexact=status)  # Поиск по статусу (без учёта регистра)

        # Фильтруем queryset
        return queryset.filter(q_objects)