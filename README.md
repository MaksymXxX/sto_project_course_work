# СТО Веб-застосунок

Веб-застосунок для управління роботою СТО з Django бекендом та React фронтендом. **Повністю підтримує багатомовність (українська та англійська мови).**

## Функціональність

### Для незареєстрованого користувача (гостя):
- Перегляд загальної інформації про СТО
- Перегляд доступних послуг та цін СТО
- Можливість записатися на сервіс без реєстрації
- Аутентифікація (реєстрація або вхід у систему)
- **Перегляд контенту українською або англійською мовою**

### Для авторизованого користувача:
- Доступ до системи лояльності (знижки за кількість завершених записів)
- Перегляд та зміна власних записів (з обмеженням: не менше 2 годин до запису)
- Скасування власних записів
- Виведення повідомлень про успішне виконання дії або помилки
- Можливість оновлення персональних даних в особистому кабінеті
- Перегляд історії записів на обслуговування та отриманих послуг
- Перегляд транзакцій лояльності
- **Повна підтримка багатомовності в особистому кабінеті**

### Для адміністратора системи:
- **Управління клієнтами:**
  - Перегляд списку всіх клієнтів
  - Редагування даних клієнтів (ім'я, прізвище, email, пароль)
  - Блокування/розблокування клієнтів
  - Перегляд статусу клієнтів

- **Управління записами:**
  - Перегляд всіх записів з фільтрами (дата, бокс, тип послуги, статус)
  - Підтвердження записів клієнтів
  - Завершення обслуговування
  - Скасування записів адміністратором
  - Перегляд деталей записів
  - Візуалізація тижневого розкладу по днях та боксах

- **Управління послугами:**
  - Створення, редагування, видалення послуг (українська + англійська)
  - Управління цінами на послуги
  - Зміна статусу послуг (активна/неактивна)
  - Управління рекомендованими послугами

- **Управління категоріями:**
  - Створення, редагування, видалення категорій послуг (українська + англійська)
  - Управління порядком відображення категорій

- **Управління боксами:**
  - Створення, редагування, видалення боксів (українська + англійська)
  - Налаштування робочих годин для кожного боксу
  - Зміна статусу боксів (активний/неактивний)

- **Управління головною сторінкою:**
  - Редагування інформації про СТО (українська + англійська)
  - Налаштування контактної інформації
  - Управління списком "У нас ви можете"
  - Управління рекомендованими послугами

- **Статистика:**
  - Загальна статистика по записах, клієнтах і завантаженості
  - Тижневий розклад з візуалізацією

- **Багатомовність:**
  - Повна підтримка української та англійської мов в адмін-панелі
  - Двоязичні форми створення та редагування
  - Автоматичне перемикання мови без перезавантаження

## Технології

### Backend:
- **Python 3.12+**
- **Django 4.2.7** - веб-фреймворк
- **Django REST Framework** - API фреймворк
- **PostgreSQL** - база даних з підтримкою багатомовності
- **JWT Authentication** - аутентифікація
- **Django CORS Headers** - обробка CORS
- **Pillow** - обробка зображень

### Frontend:
- **Node.js 18+**
- **React 18** - UI бібліотека з підтримкою багатомовності
- **React Router** - маршрутизація
- **Axios** - HTTP клієнт
- **React Hook Form** - управління формами
- **React Toastify** - сповіщення
- **React DatePicker** - вибір дати
- **React Context API** - управління станом мови

## Швидкий запуск

Для швидкого запуску проекту дивіться файл `QUICK_START.md` з покроковими інструкціями.

### Мінімальний набір команд:
```bash
# Backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py load_initial_data
python manage.py runserver

# Frontend (в новому терміналі)
cd frontend
npm install
npm start
```

## Встановлення та налаштування

### 1. Системні вимоги
- **Python 3.12 або новіше**
- **Node.js 18 або новіше**
- **PostgreSQL 12 або новіше**

### 2. Клонування репозиторію
```bash
git clone <repository-url>
cd sto-project
```

### 3. Налаштування Backend

#### Створення віртуального середовища:
```bash
python -m venv venv
```

#### Активування віртуального середовища:
```bash
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

#### Встановлення Python залежностей:
```bash
pip install -r requirements.txt
```

#### Налаштування бази даних:
1. Створіть базу даних PostgreSQL
2. Скопіюйте `env.example` в `.env` та налаштуйте змінні середовища:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/sto_db
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### Виконання міграцій:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Завантаження базових даних:
```bash
# Використання Django management команди (рекомендовано)
python manage.py load_initial_data

# АБО запуск окремого скрипта
python load_initial_data.py
```

**Що створюється автоматично (з підтримкою двох мов):**
- Суперкористувач (admin@sto.com / admin123)
- 6 категорій послуг (Технічне обслуговування, Діагностика, тощо) - українська + англійська
- 8 послуг з цінами (Повне ТО - 1500 грн, Заміна масла - 800 грн, тощо) - українська + англійська
- 3 бокси з робочими годинами - українська + англійська
- Інформація про СТО (назва, опис, контакти) - українська + англійська
- Тестовий клієнт (test@example.com / test123)

#### Створення суперкористувача (опціонально):
```bash
python manage.py createsuperuser
```

#### Запуск сервера розробки:
```bash
# Запуск на порту 8000 (за замовчуванням)
python manage.py runserver

# Запуск на конкретному порту
python manage.py runserver 8000

# Запуск з додатковими опціями
python manage.py runserver --verbosity=2

# Запуск для всіх інтерфейсів
python manage.py runserver 0.0.0.0:8000
```

### 4. Налаштування Frontend

#### Перехід в папку frontend:
```bash
cd frontend
```

#### Встановлення Node.js залежностей:
```bash
npm install
```

#### Запуск сервера розробки:
```bash
# Запуск на порту 3000 (за замовчуванням)
npm start

# Запуск з додатковими опціями
npm start -- --port 3001

# Запуск в production режимі
npm run build
npx serve -s build

# Запуск з HTTPS
HTTPS=true npm start
```

## Доступ до системи

### Адміністратор (створюється автоматично):
- **Email/Username:** admin@sto.com
- **Пароль:** admin123

### Звичайний користувач:
- Зареєструйтесь через форму реєстрації на сайті
- Email адреса використовується як username для входу в систему

## Структура проекту

```
sto-project/
├── backend/                 # Django проект
│   ├── settings.py         # Налаштування Django
│   ├── urls.py             # Головні URL
│   ├── wsgi.py             # WSGI конфігурація
│   ├── api/                # Django додаток
│   │   ├── models.py       # Моделі даних
│   │   ├── views.py        # API контролери
│   │   ├── serializers.py  # REST serializers
│   │   ├── data_access.py  # Шар доступу до даних
│   │   ├── urls.py         # URL конфігурація
│   │   └── admin.py        # Адміністративна панель
│   └── services/           # Сервісний шар
│       ├── auth_service/   # Сервіс авторизації
│       ├── user_service/   # Сервіс користувачів
│       ├── appointment_service/ # Сервіс записів
│       └── service_catalog/ # Каталог послуг
├── frontend/               # React застосунок
│   ├── src/
│   │   ├── components/     # React компоненти
│   │   ├── contexts/       # React контексти
│   │   ├── utils/          # Утиліти
│   │   ├── assets/         # Статичні файли
│   │   └── App.js          # Головний компонент
│   └── package.json
├── requirements.txt        # Python залежності
├── manage.py              # Django management
├── load_initial_data.py   # Скрипт завантаження даних
├── QUICK_START.md         # Швидкий старт
└── README.md
```

## Файли завантаження даних

### `load_initial_data.py`
Django management команда для завантаження даних з підтримкою багатомовності. Рекомендований спосіб:
```bash
python manage.py load_initial_data
```

### Що створюється автоматично (з підтримкою двох мов):
- **Користувачі:**
  - Адміністратор: `admin@sto.com` / `admin123` (email використовується як username)
  - Тестовий клієнт: `test@example.com` / `test123` (email використовується як username)

- **Категорії послуг (6 шт.) - українська + англійська:**
  - Технічне обслуговування / Technical Maintenance
  - Діагностика / Diagnostics
  - Ремонт ходової частини / Chassis Repair
  - Заміна мастил / Oil Change
  - Шиномонтаж / Tire Service
  - Електрика / Electrical

- **Послуги (8 шт.) - українська + англійська:**
  - Повне ТО / Full Technical Maintenance (1500 грн, 120 хв)
  - Заміна масла / Oil Change (800 грн, 60 хв)
  - Комп'ютерна діагностика / Computer Diagnostics (500 грн, 45 хв)
  - Заміна гальмівних колодок / Brake Pad Replacement (1200 грн, 90 хв)
  - Заміна амортизаторів / Shock Absorber Replacement (2000 грн, 120 хв)
  - Шиномонтаж (4 колеса) / Tire Service (4 wheels) (600 грн, 60 хв)
  - Заміна свічок запалювання / Spark Plug Replacement (400 грн, 30 хв)
  - Заміна повітряного фільтра / Air Filter Replacement (200 грн, 20 хв)

- **Бокси (3 шт.) - українська + англійська:**
  - Бокс 1 / Box 1 (ТО та ремонт)
  - Бокс 2 / Box 2 (діагностика та електрика)
  - Шиномонтаж / Tire Service (спеціалізований)

- **Інформація про СТО - українська + англійська:**
  - Назва: "СТО AutoServis" / "Auto Service AutoServis"
  - Контакти та робочі години
  - Опис послуг та привітальний текст

## API Endpoints

### Аутентифікація:
- `POST /api/auth/login/` - Вхід в систему
- `POST /api/auth/register/` - Реєстрація

### Послуги:
- `GET /api/services/` - Список послуг
- `GET /api/service-categories/` - Категорії послуг

### Записи:
- `GET /api/appointments/my_appointments/` - Мої записи
- `POST /api/appointments/` - Створення запису
- `PUT /api/appointments/{id}/` - Оновлення запису
- `POST /api/appointments/{id}/cancel/` - Скасування запису
- `POST /api/guest-appointments/` - Створення запису гостя

### Клієнти:
- `GET /api/customers/profile/` - Профіль користувача
- `PUT /api/customers/update_profile/` - Оновлення профілю

### Історія та лояльність:
- `GET /api/service-history/` - Історія обслуговування
- `GET /api/loyalty-transactions/` - Транзакції лояльності

### Адміністративні функції:
- `GET /api/admin/statistics/` - Статистика
- `GET /api/admin/weekly_schedule/` - Тижневий розклад
- `GET /api/admin/customer_management/` - Управління клієнтами
- `POST /api/admin/{id}/block_customer/` - Блокування клієнта
- `POST /api/admin/{id}/unblock_customer/` - Розблокування клієнта
- `PUT /api/admin/{id}/update_customer/` - Оновлення клієнта
- `GET /api/admin/services_management/` - Управління послугами
- `POST /api/admin/create_service/` - Створення послуги
- `PATCH /api/admin/{id}/update_service/` - Оновлення послуги
- `DELETE /api/admin/{id}/delete_service/` - Видалення послуги
- `POST /api/admin/{id}/toggle_service_status/` - Зміна статусу послуги
- `POST /api/admin/{id}/toggle_featured_service/` - Зміна статусу "основна"
- `GET /api/admin/categories_management/` - Управління категоріями
- `POST /api/admin/create_category/` - Створення категорії
- `PATCH /api/admin/{id}/update_category/` - Оновлення категорії
- `DELETE /api/admin/{id}/delete_category/` - Видалення категорії
- `GET /api/admin/boxes_management/` - Управління боксами
- `POST /api/admin/create_box/` - Створення боксу
- `PATCH /api/admin/{id}/update_box/` - Оновлення боксу
- `DELETE /api/admin/{id}/delete_box/` - Видалення боксу
- `POST /api/admin/{id}/toggle_box_status/` - Зміна статусу боксу
- `GET /api/admin/home_page_management/` - Інформація про СТО
- `POST /api/admin/update_home_page/` - Оновлення інформації про СТО
- `GET /api/admin/appointments/` - Список всіх записів з фільтрами
- `POST /api/admin/{id}/confirm/` - Підтвердження запису
- `POST /api/admin/{id}/complete/` - Завершення запису
- `POST /api/admin/{id}/cancel_appointment/` - Скасування запису адміном
- `GET /api/admin/{id}/appointment_details/` - Деталі запису

### Бокси та доступність:
- `GET /api/boxes/available_boxes/` - Доступні бокси
- `GET /api/boxes/available_dates/` - Доступні дати
- `GET /api/boxes/available_times/` - Доступні часи

## Розробка

### Backend розробка:
1. Активуйте віртуальне середовище
2. Встановіть залежності: `pip install -r requirements.txt`
3. Налаштуйте базу даних та змінні середовища
4. Запустіть сервер: `python manage.py runserver`

### Frontend розробка:
1. Перейдіть в папку frontend: `cd frontend`
2. Встановіть залежності: `npm install`
3. Запустіть сервер розробки: `npm start`

### Повний процес запуску:
```bash
# Термінал 1 - Backend
cd sto-project
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py load_initial_data
python manage.py runserver

# Термінал 2 - Frontend
cd sto-project/frontend
npm install
npm start
```

### Корисні команди:

#### Backend команди:
```bash
# Міграції
python manage.py makemigrations
python manage.py migrate

# Завантаження даних
python manage.py load_initial_data

# Користувачі
python manage.py createsuperuser
python manage.py changepassword

# Тестування та діагностика
python manage.py test
python manage.py check
python manage.py runserver --verbosity=2

# Shell для роботи з базою даних
python manage.py shell
```

#### Frontend команди:
```bash
# Розробка
npm start
npm test
npm run build

# Додаткові опції
npm start -- --port 3001
HTTPS=true npm start

# Production
npm run build
npx serve -s build
```

#### Системні команди:
```bash
# Перевірка версій
python --version
node --version
npm --version

# Очищення кешу
npm cache clean --force
pip cache purge
```

## Особливості системи

### Багатомовність:
- **Підтримувані мови:** українська (uk) та англійська (en)
- **Автоматичне перемикання:** без перезавантаження сторінки
- **Збереження вибраної мови:** в localStorage браузера
- **Двоязичні дані:** всі моделі мають поля з суфіксом `_en`
- **Переклади UI:** централізовані в `frontend/src/translations/translations.js`
- **API підтримка:** всі endpoints повертають дані відповідною мовою

### Система лояльності:
- За кожен завершений запис клієнт отримує знижку 0.5%
- Максимальна знижка - 10%
- Знижка застосовується автоматично при створенні/редагуванні записів

### Обмеження редагування:
- Клієнти можуть редагувати записи тільки за 2+ години до початку
- Адміністратори можуть редагувати записи в будь-який час

### Статуси записів:
- `pending` - Очікує підтвердження
- `confirmed` - Підтверджено
- `completed` - Завершено
- `cancelled` - Скасовано клієнтом
- `cancelled_by_admin` - Скасовано адміністратором

## Ліцензія

Цей проект розроблений для навчальних цілей. 