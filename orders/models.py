from django.db import models
from django.core.validators import MinValueValidator
        
class Order(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'В ожидании'),
        ('ready', 'Готов'),
        ('paid', 'Оплачено') 
    ]

    table_number = models.IntegerField(
        verbose_name="Номер стола",
        validators=[
            MinValueValidator(
                limit_value=1,
                message="Номер стола должен быть больше или равен 1"
            )
        ]
    )

    items = models.JSONField(verbose_name="Список блюд с ценами", default=list)
    
    total_price = models.DecimalField(
        verbose_name="Общая стоимость заказа",
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=0
    )

    status = models.CharField(
        verbose_name="Статус заказа",
        max_length=10,
        choices=STATUS_CHOICES,
        default='waiting'
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self) -> str:
        return f"Order {self.id} - Table {self.table_number}"
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"