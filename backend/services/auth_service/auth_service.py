from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from ...api.models import Customer


class AuthorizationService:
    """Окремий сервіс авторизації згідно з архітектурною діаграмою"""
    
    @staticmethod
    def authenticate_user(username, password):
        """Аутентифікація користувача"""
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return {
                'success': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                }
            }
        return {
            'success': False,
            'error': 'Невірні облікові дані'
        }
    
    @staticmethod
    def register_user(user_data):
        """Реєстрація нового користувача"""
        try:
            # Використовуємо email як username
            username = user_data.get('username', user_data.get('email'))
            email = user_data.get('email')
            password = user_data.get('password')
            
            # Перевірка обов'язкових полів
            if not username or not email or not password:
                return {
                    'success': False,
                    'error': 'Відсутні обов\'язкові поля'
                }
            
            # Перевірка валідності email
            if not email or '@' not in email:
                return {
                    'success': False,
                    'error': 'Введіть коректну email адресу'
                }
            
            # Перевірка довжини пароля
            if len(password) < 6:
                return {
                    'success': False,
                    'error': 'Пароль повинен містити мінімум 6 символів'
                }
            
            # Перевірка чи користувач вже існує за email
            if User.objects.filter(email=email).exists():
                return {
                    'success': False,
                    'error': 'Користувач з такою email адресою вже існує'
                }
            
            # Перевірка чи користувач вже існує за username
            if User.objects.filter(username=username).exists():
                return {
                    'success': False,
                    'error': 'Користувач з такою email адресою вже існує'
                }
            
            # Створення користувача
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', '')
            )
            
            # Створення профілю клієнта
            Customer.objects.create(
                user=user
            )
            
            # Генерація токенів
            refresh = RefreshToken.for_user(user)
            return {
                'success': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Помилка реєстрації: {str(e)}'
            }
    
    @staticmethod
    def verify_token(token):
        """Перевірка JWT токена"""
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Недійсний токен'
            }
    
    @staticmethod
    def check_permissions(user, required_permission=None):
        """Перевірка прав доступу"""
        if not user.is_authenticated:
            return False
        
        if required_permission == 'admin' and not user.is_staff:
            return False
        
        return True 

    @staticmethod
    def login_user(user_data):
        """Вхід користувача"""
        try:
            email = user_data.get('email')
            password = user_data.get('password')
            
            if not email or not password:
                return {
                    'success': False,
                    'error': 'Введіть email та пароль'
                }
            
            # Перевірка валідності email
            if not email or '@' not in email:
                return {
                    'success': False,
                    'error': 'Введіть коректну email адресу'
                }
            
            # Спробуємо знайти користувача за email
            try:
                user = User.objects.get(email=email)
                username = user.username
            except User.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Користувача з такою email адресою не знайдено'
                }
            
            # Аутентифікація
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return {
                    'success': True,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Невірний пароль'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Помилка входу: {str(e)}'
            } 