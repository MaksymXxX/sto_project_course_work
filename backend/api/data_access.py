from django.contrib.auth.models import User
from .models import Customer, Service, Appointment, ServiceHistory, LoyaltyTransaction, STOInfo


class DataAccessLayer:
    """Шар доступу до даних згідно з архітектурною діаграмою"""
    
    # Методи для роботи з користувачами
    @staticmethod
    def get_customer_by_user(user):
        """Отримання клієнта за користувачем"""
        try:
            return Customer.objects.get(user=user)
        except Customer.DoesNotExist:
            return None
    
    @staticmethod
    def get_all_customers():
        """Отримання всіх клієнтів"""
        return Customer.objects.all()
    
    @staticmethod
    def create_customer(user, address=''):
        """Створення клієнта"""
        return Customer.objects.create(
            user=user,
            address=address
        )
    
    @staticmethod
    def update_customer(customer, **kwargs):
        """Оновлення клієнта"""
        for key, value in kwargs.items():
            setattr(customer, key, value)
        customer.save()
        return customer
    
    # Методи для роботи з послугами
    @staticmethod
    def get_all_services():
        """Отримання всіх активних послуг"""
        return Service.objects.filter(is_active=True)
    
    @staticmethod
    def get_service_by_id(service_id):
        """Отримання послуги за ID"""
        try:
            return Service.objects.get(id=service_id, is_active=True)
        except Service.DoesNotExist:
            return None
    
    @staticmethod
    def create_service(**kwargs):
        """Створення послуги"""
        return Service.objects.create(**kwargs)
    
    @staticmethod
    def update_service(service, **kwargs):
        """Оновлення послуги"""
        for key, value in kwargs.items():
            setattr(service, key, value)
        service.save()
        return service
    
    # Методи для роботи з записами
    @staticmethod
    def get_appointments_by_user(user):
        """Отримання записів користувача"""
        # Для всіх користувачів (включаючи адміністраторів) показуємо тільки їх власні записи
        return Appointment.objects.filter(customer__user=user)
    
    @staticmethod
    def get_appointment_by_id(appointment_id, user=None):
        """Отримання запису за ID"""
        try:
            if user and user.is_staff:
                appointment = Appointment.objects.get(id=appointment_id)
            elif user:
                appointment = Appointment.objects.get(id=appointment_id, customer__user=user)
            else:
                appointment = Appointment.objects.get(id=appointment_id, customer__isnull=True)
            
            return appointment
        except Appointment.DoesNotExist:
            return None
    
    @staticmethod
    def create_appointment(**kwargs):
        """Створення запису"""
        return Appointment.objects.create(**kwargs)
    
    @staticmethod
    def update_appointment(appointment, **kwargs):
        """Оновлення запису"""
        for key, value in kwargs.items():
            setattr(appointment, key, value)
        appointment.save()
        return appointment
    
    @staticmethod
    def update_appointment_by_id(appointment_id, **kwargs):
        """Оновлення запису за ID"""
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            for key, value in kwargs.items():
                setattr(appointment, key, value)
            appointment.save()
            return appointment
        except Appointment.DoesNotExist:
            return None
    
    # Методи для роботи з історією обслуговування
    @staticmethod
    def get_service_history_by_user(user):
        """Отримання історії обслуговування користувача"""
        # Для всіх користувачів (включаючи адміністраторів) показуємо тільки їх власну історію
        return ServiceHistory.objects.filter(appointment__customer__user=user)
    
    @staticmethod
    def create_service_history(**kwargs):
        """Створення запису в історії"""
        return ServiceHistory.objects.create(**kwargs)
    
    # Методи для роботи з транзакціями лояльності
    @staticmethod
    def get_loyalty_transactions_by_user(user):
        """Отримання транзакцій лояльності користувача"""
        # Для всіх користувачів (включаючи адміністраторів) показуємо тільки їх власні транзакції
        return LoyaltyTransaction.objects.filter(customer__user=user)
    
    @staticmethod
    def create_loyalty_transaction(**kwargs):
        """Створення транзакції лояльності"""
        return LoyaltyTransaction.objects.create(**kwargs)
    
    # Методи для роботи з інформацією про СТО
    @staticmethod
    def get_sto_info():
        """Отримання інформації про СТО"""
        try:
            sto_info = STOInfo.objects.filter(is_active=True).first()
            if not sto_info:
                # Створюємо запис за замовчуванням
                sto_info = STOInfo.objects.create(
                    name='СТО "Автосервіс"',
                    description='Професійне обслуговування автомобілів',
                    motto='Якість та надійність',
                    welcome_text='Ласкаво просимо до нашого автосервісу!',
                    what_you_can_title='У нас ви можете:',
                    what_you_can_items=['Ознайомитися з переліком послуг та цінами', 'Записатися на обслуговування онлайн'],
                    address='м. Київ, вул. Автосервісна, 1',
                    phone='+380441234567',
                    email='info@autoservice.ua',
                    working_hours='Пн-Пт: 8:00-18:00, Сб: 9:00-15:00',
                    is_active=True
                )
            return sto_info
        except Exception as e:
            print(f"Error in get_sto_info: {str(e)}")
            return None
    
    @staticmethod
    def create_or_update_sto_info(**kwargs):
        """Створення або оновлення інформації про СТО"""
        try:
            sto_info, created = STOInfo.objects.get_or_create(
                is_active=True,
                defaults=kwargs
            )
            
            if not created:
                # Оновлюємо існуючий запис
                for key, value in kwargs.items():
                    if key == 'what_you_can_items' and isinstance(value, list):
                        # Фільтруємо порожні елементи
                        filtered_items = [item for item in value if item and item.strip()]
                        setattr(sto_info, key, filtered_items)
                    else:
                        setattr(sto_info, key, value)
                sto_info.save()
            
            return sto_info
        except Exception as e:
            print(f"Error in create_or_update_sto_info: {str(e)}")
            return None
    
    # Статистичні методи
    @staticmethod
    def get_appointments_count():
        """Отримання кількості записів"""
        return Appointment.objects.count()
    
    @staticmethod
    def get_appointments_by_status(status):
        """Отримання записів за статусом"""
        return Appointment.objects.filter(status=status)
    
    @staticmethod
    def get_customers_count():
        """Отримання кількості клієнтів"""
        return Customer.objects.count()
    
    @staticmethod
    def get_blocked_customers_count():
        """Отримання кількості заблокованих клієнтів"""
        return Customer.objects.filter(is_blocked=True).count()
    
    @staticmethod
    def get_services_count():
        """Отримання кількості активних послуг"""
        return Service.objects.filter(is_active=True).count()
    
    @staticmethod
    def get_total_revenue():
        """Отримання загального доходу"""
        completed_appointments = Appointment.objects.filter(status='completed')
        return sum(appointment.total_price for appointment in completed_appointments) 