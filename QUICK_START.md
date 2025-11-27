# Швидкий запуск СТО проекту

## Системні вимоги
- Python 3.12+
- Node.js 18+
- PostgreSQL 12+

## Швидкий запуск (5 хвилин)

### 1. Клонування та налаштування
```bash
git clone <repository-url>
cd sto-project
```

### 2. Backend (Django)
```bash
# Створення віртуального середовища
python -m venv venv

# Активування (Windows)
venv\Scripts\activate
# АБО (Linux/Mac)
source venv/bin/activate

# Встановлення залежностей
pip install -r requirements.txt

# Налаштування бази даних
# Створіть базу PostgreSQL та налаштуйте .env файл

# Міграції
python manage.py makemigrations
python manage.py migrate

# Завантаження базових даних
python manage.py load_initial_data

# Запуск сервера
python manage.py runserver
```

### 3. Frontend (React)
```bash
cd frontend
npm install
npm start
```

## Доступ до системи

### Адміністратор
- **URL:** http://localhost:3000/admin
- **Email:** admin@sto.com
- **Пароль:** admin123

### Тестовий клієнт
- **URL:** http://localhost:3000
- **Email:** test@example.com
- **Пароль:** test123

## Основні URL

- **Головна сторінка:** http://localhost:3000
- **Адмін панель:** http://localhost:3000/admin
- **Особистий кабінет:** http://localhost:3000/dashboard
- **Послуги:** http://localhost:3000/services
- **Запис на сервіс:** http://localhost:3000/appointment

## Що створюється автоматично

### Категорії послуг (6 шт.)
- Технічне обслуговування
- Діагностика
- Ремонт ходової частини
- Заміна мастил
- Шиномонтаж
- Електрика

### Послуги (8 шт.)
- Повне ТО (1500 грн)
- Заміна масла (800 грн)
- Комп'ютерна діагностика (500 грн)
- Заміна гальмівних колодок (1200 грн)
- Заміна амортизаторів (2000 грн)
- Шиномонтаж (600 грн)
- Заміна свічок запалювання (400 грн)
- Заміна повітряного фільтра (200 грн)

### Бокси (3 шт.)
- Бокс 1 (ТО та ремонт)
- Бокс 2 (діагностика та електрика)
- Шиномонтаж

### Користувачі
- Адміністратор (admin@sto.com)
- Тестовий клієнт (test@example.com)

## Проблеми та рішення

### Помилка підключення до бази даних
```bash
# Перевірте налаштування в .env файлі
DATABASE_URL=postgresql://username:password@localhost:5432/sto_db
```

### Помилка портів
```bash
# Backend займає порт 8000
# Frontend займає порт 3000
# Переконайтеся, що порти вільні
```

### Помилка міграцій
```bash
# Видаліть всі файли міграцій (крім __init__.py)
# Створіть нові міграції
python manage.py makemigrations
python manage.py migrate
```

## Корисні команди

```bash
# Створення суперкористувача
python manage.py createsuperuser

# Запуск тестів
python manage.py test

# Збірка фронтенду
cd frontend && npm run build

# Перегляд логів
python manage.py runserver --verbosity=2
```

## Підтримка

При виникненні проблем:
1. Перевірте версії Python та Node.js
2. Переконайтеся, що всі залежності встановлені
3. Перевірте налаштування бази даних
4. Дивіться детальний README.md
