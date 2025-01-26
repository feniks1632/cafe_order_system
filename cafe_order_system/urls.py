from django.conf.urls import include
from django.contrib import admin
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, include


# Swagger(API) Документация
schema_view = get_schema_view(
    openapi.Info(
        title="Cafe Order API",
        default_version='v1',
        description="API для управления заказами в кафе",
    ),
    public=True,
    
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('orders.urls')),
    path('api/', include('api.urls')),  # Подключение API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
]
