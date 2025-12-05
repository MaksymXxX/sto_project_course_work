"""
Конфігурація для тестування.
Налаштування тестового середовища та фікстур.
"""

from django.test import TestCase
from django.conf import settings

# Перевірка що використовується тестова база даних
if not settings.DEBUG:
    # У production не запускаємо тести
    pass

# Налаштування для швидких тестів
# Використовуємо in-memory SQLite для тестів (якщо не PostgreSQL)
TEST_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

