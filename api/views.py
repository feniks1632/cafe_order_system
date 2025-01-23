from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from orders.models import Order

from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    API для работы с заказами.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['table_number', 'status']
    search_fields = ['table_number', 'status']

    def get_serializer_context(self):
        """
        Передаем контекст запроса в сериализатор.
        """
        context = super().get_serializer_context()
        context['request'] = self.request  # Добавляем запрос в контекст
        return context