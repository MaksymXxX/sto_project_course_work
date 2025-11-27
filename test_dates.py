#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.api.models import Box

print("=== Тест доступних дат ===")

# Перевіряємо бокси
print("\n1. Бокси:")
boxes = Box.objects.filter(is_active=True)
for box in boxes:
    print(f"  - {box.name}: {box.working_hours}")

# Тестуємо отримання доступних дат
print("\n2. Доступні дати на наступні 7 днів:")
today = datetime.now().date()

for i in range(7):
    check_date = today + timedelta(days=i)
    day_name = check_date.strftime('%A').lower()
    print(f"  {check_date.strftime('%Y-%m-%d')} ({day_name}): ", end="")
    
    # Перевіряємо чи є хоча б один активний бокс на цю дату
    has_working_box = False
    for box in boxes:
        working_hours = box.get_working_hours_for_day(day_name)
        if working_hours and working_hours.get('start') != '00:00' and working_hours.get('end') != '00:00':
            has_working_box = True
            print(f"Працює ({box.name}: {working_hours})")
            break
    
    if not has_working_box:
        print("Не працює")

print("\n=== Тест завершено ===") 