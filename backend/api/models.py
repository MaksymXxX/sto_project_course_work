from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import json


class ServiceCategory(models.Model):
    """Модель категорії послуг"""
    name = models.CharField(max_length=100, verbose_name='Назва категорії')
    name_en = models.CharField(max_length=100, verbose_name='Назва категорії (англ.)', blank=True)
    description = models.TextField(blank=True, verbose_name='Опис категорії')
    description_en = models.TextField(blank=True, verbose_name='Опис категорії (англ.)')
    order = models.IntegerField(default=0, verbose_name='Порядок відображення')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Категорія послуг'
        verbose_name_plural = 'Категорії послуг'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_name(self, language='uk'):
        """Отримання назви категорії за мовою"""
        if language == 'en':
            return self.name_en if self.name_en else self.name
        else:
            return self.name if self.name else self.name_en

    def get_description(self, language='uk'):
        """Отримання опису категорії за мовою"""
        if language == 'en':
            return self.description_en if self.description_en else self.description
        else:
            return self.description if self.description else self.description_en


class Box(models.Model):
    """Модель боксу (парковочного місця)"""
    name = models.CharField(max_length=100, verbose_name='Назва боксу')
    name_en = models.CharField(max_length=100, verbose_name='Назва боксу (англ.)', blank=True)
    description = models.TextField(blank=True, verbose_name='Опис боксу')
    description_en = models.TextField(blank=True, verbose_name='Опис боксу (англ.)')
    is_active = models.BooleanField(default=True, verbose_name='Активний')
    working_hours = models.JSONField(
        verbose_name='Графік роботи',
        default=dict,
        help_text='Графік роботи у форматі JSON: {"monday": {"start": "08:00", "end": "18:00"}, ...}'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Бокс'
        verbose_name_plural = 'Бокси'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_name(self, language='uk'):
        """Отримання назви боксу за мовою"""
        if language == 'en':
            return self.name_en if self.name_en else self.name
        else:
            return self.name if self.name else self.name_en

    def get_description(self, language='uk'):
        """Отримання опису боксу за мовою"""
        if language == 'en':
            return self.description_en if self.description_en else self.description
        else:
            return self.description if self.description else self.description_en

    def get_working_hours_for_day(self, day_name):
        """Отримання графіку роботи для конкретного дня"""
        if isinstance(self.working_hours, str):
            try:
                working_hours = json.loads(self.working_hours)
            except json.JSONDecodeError:
                return None
        else:
            working_hours = self.working_hours
        
        return working_hours.get(day_name.lower())

    def is_available_at_time(self, date, time):
        """Перевірка чи бокс вільний в заданий час"""
        from datetime import datetime
        import calendar
        
        # Отримуємо день тижня
        day_name = calendar.day_name[date.weekday()].lower()
        working_hours = self.get_working_hours_for_day(day_name)
        
        if not working_hours:
            return False
        
        # Перевіряємо чи бокс працює в цей день (не 00:00-00:00)
        start_time = working_hours.get('start', '00:00')
        end_time = working_hours.get('end', '23:59')
        
        if start_time == '00:00' and end_time == '00:00':
            return False
        
        # Перевіряємо чи час в межах робочого графіку
        time_str = time.strftime('%H:%M')
        return start_time <= time_str <= end_time


class Service(models.Model):
    """Модель послуги СТО"""
    name = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200, verbose_name='Назва послуги (англ.)', blank=True)
    description = models.TextField(blank=True)
    description_en = models.TextField(blank=True, verbose_name='Опис послуги (англ.)')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    duration_minutes = models.IntegerField(default=60, help_text="Тривалість послуги в хвилинах")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, verbose_name='Основна послуга')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Послуга'
        verbose_name_plural = 'Послуги'
        ordering = ['category__order', 'category__name', 'name']

    def __str__(self):
        return self.name

    def get_name(self, language='uk'):
        """Отримання назви послуги за мовою"""
        if language == 'en':
            return self.name_en if self.name_en else self.name
        else:
            return self.name if self.name else self.name_en

    def get_description(self, language='uk'):
        """Отримання опису послуги за мовою"""
        if language == 'en':
            return self.description_en if self.description_en else self.description
        else:
            return self.description if self.description else self.description_en


class Customer(models.Model):
    """Модель клієнта"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Користувач')
    address = models.TextField(verbose_name='Адреса', blank=True)
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Фото профілю', blank=True, null=True)
    loyalty_points = models.IntegerField(default=0, verbose_name='Бали лояльності')
    is_blocked = models.BooleanField(default=False, verbose_name='Заблокований')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Клієнт'
        verbose_name_plural = 'Клієнти'

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def calculate_discount_percentage(self):
        """Розрахунок відсотка знижки на основі кількості завершених записів"""
        from .models import Appointment
        
        # Отримуємо кількість завершених записів для цього клієнта
        completed_appointments = Appointment.objects.filter(
            customer=self,
            status='completed'
        ).count()
        
        # Розраховуємо знижку: 0.5% за кожне відвідування, максимум 10%
        discount = min(completed_appointments * 0.5, 10)
        return discount

    def apply_discount_to_price(self, original_price):
        """Застосування знижки до ціни"""
        from decimal import Decimal
        
        discount_percentage = self.calculate_discount_percentage()
        discount_amount = original_price * Decimal(discount_percentage) / Decimal(100)
        final_price = original_price - discount_amount
        
        return final_price


class Appointment(models.Model):
    """Модель запису на обслуговування"""
    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('in_progress', 'В роботі'),
        ('completed', 'Завершено'),
        ('cancelled', 'Скасовано клієнтом'),
        ('cancelled_by_admin', 'Скасовано адміністратором'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name='Клієнт',
        null=True,
        blank=True
    )
    guest_name = models.CharField(max_length=100, verbose_name='Ім\'я гостя', blank=True)
    guest_phone = models.CharField(max_length=20, verbose_name='Телефон гостя', blank=True)
    guest_email = models.EmailField(verbose_name='Email гостя', blank=True)

    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Послуга')
    box = models.ForeignKey(
        Box,
        on_delete=models.CASCADE,
        verbose_name='Бокс',
        null=True,
        blank=True
    )
    appointment_date = models.DateField(verbose_name='Дата запису')
    appointment_time = models.TimeField(verbose_name='Час запису')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    notes = models.TextField(blank=True, verbose_name='Примітки')
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Загальна вартість'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Запис'
        verbose_name_plural = 'Записи'
        ordering = ['-appointment_date', '-appointment_time']

    def __str__(self):
        customer_name = self.customer.user.get_full_name() if self.customer else self.guest_name
        return f"{customer_name} - {self.service.name} ({self.appointment_date})"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.service.price
        super().save(*args, **kwargs)


class ServiceHistory(models.Model):
    """Модель історії обслуговування"""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, verbose_name='Запис')
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата завершення')
    mechanic_notes = models.TextField(blank=True, verbose_name='Примітки механіка')
    actual_duration = models.IntegerField(verbose_name='Фактична тривалість (хвилини)')
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Фінальна вартість'
    )

    class Meta:
        verbose_name = 'Історія обслуговування'
        verbose_name_plural = 'Історія обслуговування'

    def __str__(self):
        return f"{self.appointment} - {self.completed_at}"


class LoyaltyTransaction(models.Model):
    """Модель транзакції лояльності"""
    TRANSACTION_TYPES = [
        ('earned', 'Зароблено'),
        ('spent', 'Витрачено'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Клієнт')
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        verbose_name='Тип транзакції'
    )
    points = models.IntegerField(verbose_name='Кількість балів')
    description = models.CharField(max_length=200, verbose_name='Опис')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Транзакція лояльності'
        verbose_name_plural = 'Транзакції лояльності'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer} - {self.get_transaction_type_display()} {self.points} балів"


class STOInfo(models.Model):
    """Модель інформації про СТО"""
    name = models.CharField(max_length=200, verbose_name='Назва СТО')
    name_en = models.CharField(max_length=200, verbose_name='Назва СТО (англ.)', blank=True)
    description = models.TextField(verbose_name='Опис')
    description_en = models.TextField(blank=True, verbose_name='Опис (англ.)')
    motto = models.CharField(max_length=200, verbose_name='Девіз')
    motto_en = models.CharField(max_length=200, verbose_name='Девіз (англ.)', blank=True)
    welcome_text = models.TextField(verbose_name='Привітальний текст')
    welcome_text_en = models.TextField(blank=True, verbose_name='Привітальний текст (англ.)')
    what_you_can_title = models.CharField(max_length=200, verbose_name='Заголовок розділу "Що ви можете"', default='У нас ви можете:')
    what_you_can_title_en = models.CharField(max_length=200, verbose_name='Заголовок розділу "Що ви можете" (англ.)', blank=True)
    what_you_can_items = models.JSONField(
        verbose_name='Пункти "Що ви можете"',
        default=list,
        help_text='Список пунктів у форматі JSON'
    )
    what_you_can_items_en = models.JSONField(
        verbose_name='Пункти "Що ви можете" (англ.)',
        default=list,
        blank=True,
        help_text='Список пунктів англійською у форматі JSON'
    )
    address = models.TextField(verbose_name='Адреса')
    address_en = models.TextField(blank=True, verbose_name='Адреса (англ.)')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    phone_en = models.CharField(max_length=20, verbose_name='Телефон (англ.)', blank=True)
    email = models.EmailField(verbose_name='Email')
    email_en = models.EmailField(blank=True, verbose_name='Email (англ.)')
    working_hours = models.CharField(max_length=100, verbose_name='Робочі години')
    working_hours_en = models.CharField(max_length=100, verbose_name='Робочі години (англ.)', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Інформація про СТО'
        verbose_name_plural = 'Інформація про СТО'

    def __str__(self):
        return self.name

    def get_name(self, language='uk'):
        """Отримання назви СТО за мовою"""
        if language == 'en' and self.name_en:
            return self.name_en
        return self.name

    def get_description(self, language='uk'):
        """Отримання опису СТО за мовою"""
        if language == 'en' and self.description_en:
            return self.description_en
        return self.description

    def get_motto(self, language='uk'):
        """Отримання девізу за мовою"""
        if language == 'en' and self.motto_en:
            return self.motto_en
        return self.motto

    def get_welcome_text(self, language='uk'):
        """Отримання привітального тексту за мовою"""
        if language == 'en' and self.welcome_text_en:
            return self.welcome_text_en
        return self.welcome_text

    def get_what_you_can_title(self, language='uk'):
        """Отримання заголовку розділу за мовою"""
        if language == 'en' and self.what_you_can_title_en:
            return self.what_you_can_title_en
        return self.what_you_can_title

    def get_what_you_can_items_list(self, language='uk'):
        """Повертає список пунктів як Python список за мовою"""
        if language == 'en':
            items = self.what_you_can_items_en
        else:
            items = self.what_you_can_items
            
        if isinstance(items, str):
            try:
                return json.loads(items)
            except json.JSONDecodeError:
                return []
        return items or []

    def set_what_you_can_items_list(self, items_list, language='uk'):
        """Встановлює список пунктів за мовою"""
        if language == 'en':
            if isinstance(items_list, list):
                self.what_you_can_items_en = items_list
            else:
                self.what_you_can_items_en = []
        else:
            if isinstance(items_list, list):
                self.what_you_can_items = items_list
            else:
                self.what_you_can_items = [] 