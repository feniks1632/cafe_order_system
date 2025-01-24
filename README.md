# Система управления заказами для кафе 🍽️

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![JavaScript](https://img.shields.io/badge/-JavaScript-464646?style=flat-square&logo=JavaScript)](https://learn.javascript.ru/)
[![Bootstrap](https://img.shields.io/badge/-Bootstrap-464646?style=flat-square&logo=Bootstrap)](https://getbootstrap.com/)

Приложение для управления заказами в кафе, позволяющее эффективно отслеживать и управлять заказами. Система предоставляет удобный интерфейс для создания, редактирования и удаления заказов, а также мощные инструменты для поиска и анализа данных.

## Основные функции 🌟

- **Создание заказа**: Легко создавайте новые заказы, указывая номер стола и добавляя блюда.
- **Редактирование заказа**: Добавляйте новые блюда или удалите заказ.
- **Удаление заказа**: Удаляйте заказы, которые больше не нужны.
- **Поиск заказов**: Ищите заказы по ID, номеру стола или статусу.
- **Расчет выручки**: Отдельная страница для расчета выручки по заказам со статусом "Оплачено".
- **API**: Интеграция с внешними системами через REST API.

## Использованные технологии 🛠️

- **Backend**: Python, Django, djangorestframework
- **Frontend**: Bootstrap, JavaScript
- **Тестирование**: Написаны unit-тесты для проверки функциональности приложения.

  ### Для локального запуска проекта вам понадобится:
  - Склонировать репозиторий:

```bash
   git clone <название репозитория>
```

```bash
   cd <название репозитория> 
```

Cоздать и активировать виртуальное окружение:

Команда для установки виртуального окружения:
Команда для Linux
```bash
   python3 -m venv env
   source env/bin/activate
```

Команда для Windows:

```bash
   python -m venv venv
   source venv/Scripts/activate
```

- Перейти в директорию cafe_order_system:

```bash
   cd cafe_order_system
```

- Создать файл .env по образцу(находится в корне репазитория env.example(в нем все переменные окружения):


Установить зависимости из файла requirements.txt:(в папке с manage.py)

```bash
   cd ..
   pip install -r requirements.txt
```
- Выполнить миграции:
```bash
   python manage.py migrate
```
Запустить сервер разработки

```bash
   python manage.py runserver
```

 Перейти по адресу  - http://localhost:8000/ или http://127.0.0.1:8000/
 
API Documentation 📚
API документация доступна по следующим адресам:

Swagger: http://localhost:8000/swagger/

Redoc: http://localhost:8000/redoc/

Основные эндпоинты API:
Список заказов: GET /api/orders/

Детали заказа: GET /api/orders/<id>

Создание заказа: POST /api/orders/

Обновление заказа: PUT /api/orders/<id>

Удаление заказа: DELETE /api/orders/<id>

Тестирование 🧪

Для обеспечения качества кода написаны тесты, покрывающие основные функции приложения. Запустите тесты с помощью команды:(из корневой директории где файл manage.py)

bash
```
pytest
```
Разработано с ❤️ для эффективного управления заказами в кафе. Если у вас есть вопросы или предложения, не стесняйтесь связаться со мной!


Мой telegram = @HovardLarson

Мой vk = https://vk.com/feniks1632

