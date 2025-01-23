document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('order-form'); // Убедитесь, что у формы есть id
    const dishesDiv = document.getElementById('dishes');

    // Проверка, что элементы существуют
    if (!form || !dishesDiv) {
        console.error('Элементы form или dishesDiv не найдены!');
        return;
    }

    // Проверка, что это страница редактирования
    const isEditPage = window.location.pathname.includes('edit');

    // Добавление нового блюда
    document.getElementById('add-dish').addEventListener('click', function () {
        const dishCount = dishesDiv.querySelectorAll('.dish').length;
        const newDish = document.createElement('div');
        newDish.className = 'dish';
        newDish.innerHTML = `
            <label for="id_dish_name_${dishCount}">Название блюда ${dishCount + 1}:</label>
            <input type="text" name="dish_name_${dishCount}" id="id_dish_name_${dishCount}" placeholder="Введите название блюда" required>
            <label for="id_dish_price_${dishCount}">Цена ${dishCount + 1}:</label>
            <input type="number" name="dish_price_${dishCount}" id="id_dish_price_${dishCount}" step="0.01" placeholder="Введите цену" required>
            <button type="button" class="remove-dish" data-index="${dishCount}">×</button>
            <input type="hidden" name="dish_id_${dishCount}" value="${dishCount}"> <!-- Скрытое поле для идентификации блюда -->
        `;
        dishesDiv.appendChild(newDish);
    });

    // Удаление блюда
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('remove-dish')) {
            const dishDiv = event.target.closest('.dish');
            const dishCount = dishesDiv.querySelectorAll('.dish').length;

            if (dishCount <= 1 && !isEditPage) {
                alert('Заказ должен содержать хотя бы одну позицию.');
                return;
            }

            dishDiv.remove();
        }
    });

    // Валидация формы перед отправкой
    form.addEventListener('submit', function (event) {
        let isValid = true;
        const errors = [];

        // Проверяем все поля ввода
        const inputs = dishesDiv.querySelectorAll('input[required]');
        const existingDishes = dishesDiv.querySelectorAll('.dish'); // Учитываем уже существующие блюда

        // Проверка на минимальное количество блюд
        if (existingDishes.length === 0) {
            isValid = false;
            errors.push('Заказ должен содержать хотя бы одну позицию.');
        }

        inputs.forEach(input => {
            const value = input.value.trim();

            // Проверка на пустое поле
            if (!value) {
                isValid = false;
                input.classList.add('error');
                errors.push(`Поле "${input.previousElementSibling.textContent}" не может быть пустым.`);
                return;
            }

            // Проверка типа данных
            if (input.type === 'text') {
                // Проверка, что поле "Название блюда" содержит только буквы и пробелы
                if (!/^[a-zA-Zа-яА-Я\s]+$/.test(value)) {
                    isValid = false;
                    input.classList.add('error');
                    errors.push(`Поле "${input.previousElementSibling.textContent}" должно содержать только буквы.`);
                }
                
            } else if (input.type === 'number') {
                // Проверка, что поле "Цена" является числом с плавающей точкой
                const price = parseFloat(value);
                if (isNaN(price)) {
                    isValid = false;
                    input.classList.add('error');
                    errors.push(`Поле "${input.previousElementSibling.textContent}" должно быть числом.`);
                } else if (price <= 0) {
                    isValid = false;
                    input.classList.add('error');
                    errors.push(`Поле "${input.previousElementSibling.textContent}" должно быть положительным числом.`);
                }
            }
        });

        if (!isValid) {
            event.preventDefault(); // Отменяем отправку формы
            alert(errors.join('\n')); // Показываем все ошибки
        }
    });
});