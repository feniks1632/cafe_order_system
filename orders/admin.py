from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_number', 'status', 'total_price', 'get_items_count')
    list_filter = ('status','table_number')
    search_fields = ('table_number', 'status')
    readonly_fields = ('total_price',)

    # Метод для отображения количества блюд в заказе
    def get_items_count(self, obj) -> int:
        return len(obj.items)
    get_items_count.short_description = 'Количество блюд'

    # Группировка полей
    fieldsets = (
        (None, {
            'fields': ('table_number', 'status')
        }),
        ('Детали заказа', {
            'fields': ('items', 'total_price'),
            'description': 'Информация о блюдах и общей стоимости заказа.'
        }),
    )