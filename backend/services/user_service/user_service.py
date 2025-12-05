"""Сервіс для роботи з користувачами та їх профілями."""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from ...api.models import Customer
from ..auth_service.auth_service import AuthorizationService
from ...api.data_access import DataAccessLayer


class UserService:
    """Сервіс користувачів згідно з архітектурною діаграмою"""

    @staticmethod
    def _format_password_validation_errors(validation_error):
        """Форматування помилок валідації пароля"""
        error_messages = []
        for error in validation_error.error_list:
            error_str = str(error).lower()
            if 'too common' in error_str:
                error_messages.append(
                    'Пароль занадто простий або часто використовується')
            elif 'too short' in error_str:
                error_messages.append('Пароль занадто короткий')
            elif 'too similar' in error_str:
                error_messages.append(
                    'Пароль занадто схожий на ваші особисті дані')
            elif 'numeric' in error_str:
                error_messages.append(
                    'Пароль не може складатися тільки з цифр')
            else:
                error_messages.append(str(error))
        return error_messages

    @staticmethod
    def get_user_profile(user):
        """Отримання профілю користувача"""
        customer = DataAccessLayer.get_customer_by_user(user)
        if customer:
            # Отримуємо кількість завершених записів
            from ...api.models import Appointment  # pylint: disable=import-outside-toplevel
            completed_appointments_count = Appointment.objects.filter(  # pylint: disable=no-member
                customer=customer,
                status='completed'
            ).count()

            return {
                'id': customer.id,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                },
                'address': customer.address,
                'avatar': customer.avatar.url if customer.avatar else None,
                'loyalty_points': customer.loyalty_points,
                'is_blocked': customer.is_blocked,
                'completed_appointments_count': completed_appointments_count,
                'created_at': customer.created_at
            }
        return None

    @staticmethod
    def update_user_profile(user, data):
        """Оновлення профілю користувача"""
        customer = DataAccessLayer.get_customer_by_user(user)
        if customer:
            # Перевірка унікальності email
            if 'email' in data and data['email'] != user.email:
                if User.objects.filter(  # pylint: disable=no-member
                        email=data['email']).exclude(id=user.id).exists():
                    return None  # Email вже використовується

            # Оновлюємо дані користувача
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                user.email = data['email']

            # Обробка зміни пароля
            if 'password' in data and data['password']:
                try:
                    # Валідація пароля
                    validate_password(data['password'], user)
                    user.set_password(data['password'])
                except ValidationError as e:
                    # Обробляємо помилки валідації
                    error_messages = UserService._format_password_validation_errors(
                        e)
                    return {
                        'error': 'Помилка валідації пароля: ' +
                        '; '.join(error_messages)
                    }

            user.save()

            # Оновлюємо дані клієнта
            update_data = {}
            if 'address' in data:
                update_data['address'] = data['address']
            if 'avatar' in data:
                update_data['avatar'] = data['avatar']

            if update_data:
                DataAccessLayer.update_customer(customer, **update_data)

            return UserService.get_user_profile(user)
        return None

    @staticmethod
    def get_all_customers():
        """Отримання всіх клієнтів (для адміністраторів)"""
        customers = DataAccessLayer.get_all_customers()
        return [
            {
                'id': customer.id,
                'user': {
                    'id': customer.user.id,
                    'username': customer.user.username,
                    'email': customer.user.email,
                    'first_name': customer.user.first_name,
                    'last_name': customer.user.last_name,
                    'is_staff': customer.user.is_staff,
                    'is_superuser': customer.user.is_superuser
                },
                'loyalty_points': customer.loyalty_points,
                'is_blocked': customer.is_blocked,
                'created_at': customer.created_at
            }
            for customer in customers
        ]

    @staticmethod
    def block_customer(customer_id):
        """Блокування клієнта"""
        try:
            customer = Customer.objects.get(
                id=customer_id)  # pylint: disable=no-member
            DataAccessLayer.update_customer(customer, is_blocked=True)
            return True
        except Customer.DoesNotExist:  # pylint: disable=no-member
            return False

    @staticmethod
    def unblock_customer(customer_id):
        """Розблокування клієнта"""
        try:
            customer = Customer.objects.get(
                id=customer_id)  # pylint: disable=no-member
            DataAccessLayer.update_customer(customer, is_blocked=False)
            return True
        except Customer.DoesNotExist:  # pylint: disable=no-member
            return False

    @staticmethod
    def check_user_permissions(user, required_permission=None):
        """Перевірка прав користувача"""
        return AuthorizationService.check_permissions(
            user, required_permission)
