"""API views для СТО системи."""

from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Max, Q, Sum
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import (
    ServiceCategory,
    Service,
    Customer,
    Appointment,
    ServiceHistory,
    LoyaltyTransaction,
    Box,
)
from .serializers import (
    ServiceCategorySerializer,
    ServiceSerializer,
    ServiceListSerializer,
    CustomerSerializer,
    AppointmentSerializer,
    ServiceHistorySerializer,
    LoyaltyTransactionSerializer,
    STOInfoSerializer,
    GuestAppointmentSerializer,
    BoxSerializer,
)
from ..services.auth_service.auth_service import AuthorizationService
from ..services.user_service.user_service import UserService
from ..services.appointment_service.appointment_service import (
    AppointmentService)
from ..services.service_catalog.service_catalog import ServiceCatalog


def get_language_from_request(request):
    """Отримання мови з запиту"""
    # Спочатку перевіряємо параметр language в URL (пріоритет вище)
    language = request.query_params.get('language', 'uk')
    if language in ['uk', 'en']:
        return language

    # Потім перевіряємо заголовок Accept-Language (тільки якщо немає параметра)
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    if 'en' in accept_language.lower():
        return 'en'

    # За замовчуванням українська
    return 'uk'


class NoPagination(PageNumberPagination):
    page_size = None


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API для категорій послуг"""
    queryset = ServiceCategory.objects.all().order_by(
        'order', 'name')  # pylint: disable=no-member
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        """Додаємо мову в контекст серіалізатора"""
        context = super().get_serializer_context()
        context['language'] = get_language_from_request(self.request)
        return context


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """API для послуг СТО"""

    def get_queryset(self):
        return Service.objects.filter(
            is_active=True
        ).select_related('category').order_by(
            'category__order', 'category__name', 'name'
        )
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = NoPagination

    def get_serializer_context(self):
        """Додаємо мову в контекст серіалізатора"""
        context = super().get_serializer_context()
        context['language'] = get_language_from_request(self.request)
        return context

    @action(detail=False, methods=['get'])
    def featured(self, _request):
        """Отримання рекомендованих послуг для головної сторінки"""
        featured_services = Service.objects.filter(  # pylint: disable=no-member
            is_featured=True, is_active=True
        ).select_related('category').order_by(
            'category__order', 'category__name', 'name')
        serializer = self.get_serializer(featured_services, many=True)
        return Response(serializer.data)


class STOInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """API для інформації про СТО"""

    def get_queryset(self):
        sto_info = ServiceCatalog.get_sto_info()
        return [sto_info] if sto_info else []
    serializer_class = STOInfoSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        """Додаємо мову в контекст серіалізатора"""
        context = super().get_serializer_context()
        context['language'] = get_language_from_request(self.request)
        return context

    def list(self, request, *args, **kwargs):
        """Отримання інформації про СТО з підтримкою кешування"""
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(queryset[0])
            return Response(serializer.data)
        return Response(
            {'error': 'Інформацію про СТО не знайдено'},
            status=status.HTTP_404_NOT_FOUND)


class GuestAppointmentViewSet(viewsets.ModelViewSet):
    """API для записів гостей"""
    serializer_class = GuestAppointmentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Appointment.objects.filter(customer__isnull=True)  # pylint: disable=no-member

    def create(self, request, *args, **kwargs):
        """Створення запису гостя"""
        # Перевіряємо чи авторизований користувач заблокований
        if request.user.is_authenticated:
            try:
                customer = Customer.objects.get(user=request.user)
                if customer.is_blocked:
                    error_msg = (
                        'Ваш акаунт заблокований. Ви не можете створювати '
                        'записи. Зверніться до адміністратора для '
                        'розблокування.'
                    )
                    return Response(
                        {'error': error_msg},
                        status=status.HTTP_403_FORBIDDEN)
            except Customer.DoesNotExist:
                # Якщо користувач не має профілю клієнта, створюємо його
                customer = Customer.objects.create(user=request.user)
                # Після створення профілю перевіряємо чи він не заблокований
                if customer.is_blocked:
                    error_msg = (
                        'Ваш акаунт заблокований. Ви не можете створювати '
                        'записи. Зверніться до адміністратора для '
                        'розблокування.'
                    )
                    return Response(
                        {'error': error_msg},
                        status=status.HTTP_403_FORBIDDEN)

        result = AppointmentService.create_appointment(request.data)
        if result['success']:
            serializer = self.get_serializer(result['appointment'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'error': result['error']},
            status=status.HTTP_400_BAD_REQUEST)


class CustomerViewSet(viewsets.ModelViewSet):
    """API для клієнтів"""
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Customer.objects.all()

        # Переконуємось, що у користувача є профіль клієнта
        Customer.objects.get_or_create(user=self.request.user)

        return Customer.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Отримання профілю поточного користувача"""
        # Перевіряємо чи користувач заблокований
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            # Якщо профіль клієнта не знайдено, створюємо його
            customer = Customer.objects.create(user=request.user)

        profile_data = UserService.get_user_profile(request.user)
        if profile_data:
            # Додаємо інформацію про блокування до профілю
            if customer.is_blocked:
                profile_data['is_blocked'] = True
                profile_data['block_message'] = (
                    'Ваш акаунт заблокований. Зверніться до адміністратора '
                    'для розблокування.'
                )
            else:
                profile_data['is_blocked'] = False
            return Response(profile_data)
        return Response(
            {'error': 'Профіль не знайдено'},
            status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Оновлення профілю користувача"""
        # Перевіряємо чи користувач заблокований
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.is_blocked:
                error_msg = (
                    'Ваш акаунт заблокований. Ви не можете оновлювати '
                    'профіль. Зверніться до адміністратора для '
                    'розблокування.'
                )
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_403_FORBIDDEN)
        except Customer.DoesNotExist:
            # Якщо профіль клієнта не знайдено, створюємо його
            customer = Customer.objects.create(user=request.user)
            # Після створення профілю перевіряємо чи він не заблокований
            if customer.is_blocked:
                error_msg = (
                    'Ваш акаунт заблокований. Ви не можете оновлювати '
                    'профіль. Зверніться до адміністратора для '
                    'розблокування.'
                )
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_403_FORBIDDEN)

        # Обробляємо файли
        data = request.data.copy()
        if 'avatar' in request.FILES:
            data['avatar'] = request.FILES['avatar']

        updated_profile = UserService.update_user_profile(request.user, data)
        if updated_profile:
            # Перевіряємо чи є помилка валідації
            if (isinstance(updated_profile, dict) and
                    'error' in updated_profile):
                return Response(
                    updated_profile, status=status.HTTP_400_BAD_REQUEST)
            return Response(updated_profile)
        return Response(
            {
                'error': (
                    'Помилка оновлення профілю. Можливо, email вже '
                    'використовується.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class AppointmentViewSet(viewsets.ModelViewSet):
    """API для записів на обслуговування"""
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Якщо користувач є адміністратором, повертаємо всі записи
        if self.request.user.is_staff:
            return Appointment.objects.all().select_related(
                'customer__user', 'service', 'box')

        # Переконуємось, що у користувача є профіль клієнта
        Customer.objects.get_or_create(user=self.request.user)

        return AppointmentService.get_user_appointments(self.request.user)

    def get_serializer_context(self):
        """Додавання контексту до серіалізатора"""
        context = super().get_serializer_context()
        context['language'] = get_language_from_request(self.request)
        return context

    def get_object(self):
        """Отримання об'єкта запису"""
        # Якщо користувач є адміністратором,
        # дозволяємо отримати будь-який запис
        if self.request.user.is_staff:
            return super().get_object()

        # Для звичайних користувачів використовуємо стандартну логіку
        return super().get_object()

    def create(self, request, *args, **kwargs):
        """Створення запису для зареєстрованого користувача"""
        # Перевіряємо чи користувач заблокований
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.is_blocked:
                error_msg = (
                    'Ваш акаунт заблокований. Ви не можете створювати '
                    'записи. Зверніться до адміністратора для '
                    'розблокування.'
                )
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_403_FORBIDDEN)
        except Customer.DoesNotExist:
            # Якщо профіль клієнта не знайдено, створюємо його
            customer = Customer.objects.create(user=request.user)
            # Після створення профілю перевіряємо чи він не заблокований
            if customer.is_blocked:
                error_msg = (
                    'Ваш акаунт заблокований. Ви не можете створювати '
                    'записи. Зверніться до адміністратора для '
                    'розблокування.'
                )
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_403_FORBIDDEN)

        result = AppointmentService.create_appointment(
            request.data, request.user)
        if result['success']:
            serializer = self.get_serializer(
                result['appointment'], context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'error': result['error']},
            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Оновлення запису для зареєстрованого користувача"""
        # Перевіряємо чи користувач заблокований
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.is_blocked:
                error_msg = (
                    'Ваш акаунт заблокований. Ви не можете редагувати '
                    'записи. Зверніться до адміністратора для '
                    'розблокування.'
                )
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_403_FORBIDDEN)
        except Customer.DoesNotExist:
            # Якщо профіль клієнта не знайдено, створюємо його
            customer = Customer.objects.create(user=request.user)
            # Після створення профілю перевіряємо чи він не заблокований
            if customer.is_blocked:
                error_msg = (
                    'Ваш акаунт заблокований. Ви не можете редагувати '
                    'записи. Зверніться до адміністратора для '
                    'розблокування.'
                )
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_403_FORBIDDEN)

        appointment = self.get_object()

        # Перевіряємо чи користувач є власником запису
        if appointment.customer and appointment.customer.user != request.user:
            return Response(
                {'error': 'Доступ заборонено'},
                status=status.HTTP_403_FORBIDDEN)

        # Перевіряємо чи можна редагувати запис
        if appointment.status not in ['pending']:
            return Response(
                {'error': 'Не можна редагувати запис у поточному статусі'},
                status=status.HTTP_400_BAD_REQUEST)

        # Перевіряємо час до запису (не менше 2 годин)
        now = timezone.now()
        appointment_datetime = datetime.combine(
            appointment.appointment_date, appointment.appointment_time)
        appointment_datetime = timezone.make_aware(appointment_datetime)

        time_difference = appointment_datetime - now
        if time_difference.total_seconds() < 7200:  # 2 години = 7200 секунд
            return Response({
                'error': (
                    'Не можна редагувати запис менше ніж за 2 години '
                    'до його початку. Зверніться до адміністратора для '
                    'внесення змін.'
                )
            }, status=status.HTTP_400_BAD_REQUEST)

        # Використовуємо AppointmentService для оновлення
        result = AppointmentService.update_appointment(
            appointment.id, request.data, request.user)
        if result['success']:
            serializer = self.get_serializer(
                result['appointment'], context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {'error': result['error']},
            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_appointments(self, request):
        """Отримання записів поточного користувача"""
        # Переконуємось, що у користувача є профіль клієнта
        Customer.objects.get_or_create(user=request.user)

        appointments = AppointmentService.get_user_appointments(request.user)
        serializer = self.get_serializer(
            appointments, many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Підтвердження запису (тільки для адміністраторів)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Доступ заборонено'},
                status=status.HTTP_403_FORBIDDEN)

        try:
            appointment = self.get_object()
            msg = (
                f"Підтвердження запису {appointment.id} "
                f"адміністратором {request.user.username}")
            print(msg)

            # Перевіряємо чи можна підтвердити запис
            if appointment.status not in ['pending']:
                return Response(
                    {'error': 'Не можна підтвердити запис у поточному статусі'},
                    status=status.HTTP_400_BAD_REQUEST)

            appointment.status = 'confirmed'
            appointment.save()
            return Response({'message': 'Запис підтверджено'})
        except Exception as e:
            print(f"Помилка при підтвердженні запису: {str(e)}")
            return Response(
                {'error': 'Помилка при підтвердженні запису'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Завершення запису (тільки для адміністраторів)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Доступ заборонено'},
                status=status.HTTP_403_FORBIDDEN)

        try:
            appointment = self.get_object()
            msg = (
                f"Завершення запису {appointment.id} "
                f"адміністратором {request.user.username}")
            print(msg)

            # Перевіряємо чи можна завершити запис
            if appointment.status not in ['confirmed', 'in_progress']:
                return Response(
                    {'error': 'Не можна завершити запис у поточному статусі'},
                    status=status.HTTP_400_BAD_REQUEST)

            appointment.status = 'completed'
            appointment.save()
            return Response({'message': 'Запис завершено'})
        except Exception as e:
            print(f"Помилка при завершенні запису: {str(e)}")
            return Response(
                {'error': 'Помилка при завершенні запису'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Скасування запису (тільки власник запису)"""
        # Перевіряємо чи користувач заблокований
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.is_blocked:
                error_msg = (
                    'Ваш акаунт заблокований. Ви не можете скасовувати '
                    'записи. Зверніться до адміністратора для '
                    'розблокування.'
                )
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_403_FORBIDDEN)
        except Customer.DoesNotExist:
            # Якщо профіль клієнта не знайдено, створюємо його
            customer = Customer.objects.create(user=request.user)
            # Після створення профілю перевіряємо чи він не заблокований
            if customer.is_blocked:
                error_msg = (
                    'Ваш акаунт заблокований. Ви не можете скасовувати '
                    'записи. Зверніться до адміністратора для '
                    'розблокування.'
                )
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_403_FORBIDDEN)

        appointment = self.get_object()

        # Перевіряємо чи користувач є власником запису
        if appointment.customer and appointment.customer.user != request.user:
            return Response(
                {'error': 'Доступ заборонено'},
                status=status.HTTP_403_FORBIDDEN)

        # Перевіряємо чи можна скасувати запис
        if appointment.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Не можна скасувати запис у поточному статусі'},
                status=status.HTTP_400_BAD_REQUEST)

        appointment.status = 'cancelled'
        appointment.save()
        return Response({'message': 'Запис скасовано'})


class ServiceHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API для історії обслуговування"""
    serializer_class = ServiceHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Переконуємось, що у користувача є профіль клієнта
        Customer.objects.get_or_create(user=self.request.user)

        return ServiceHistory.objects.filter(
            appointment__customer__user=self.request.user)


class LoyaltyTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """API для транзакцій лояльності"""
    serializer_class = LoyaltyTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Переконуємось, що у користувача є профіль клієнта
        Customer.objects.get_or_create(user=self.request.user)

        return LoyaltyTransaction.objects.filter(
            customer__user=self.request.user)


class AuthViewSet(viewsets.ViewSet):
    """API для аутентифікації"""
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Реєстрація користувача"""
        result = AuthorizationService.register_user(request.data)
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(
            {'error': result['error']},
            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Вхід користувача"""
        result = AuthorizationService.login_user(request.data)
        if result['success']:
            return Response(result)
        return Response(
            {'error': result['error']},
            status=status.HTTP_400_BAD_REQUEST)


class BoxViewSet(viewsets.ModelViewSet):
    """ViewSet для управління боксами"""
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Фільтрація боксів за активністю"""
        return Box.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def available_boxes(self, request):
        """Отримання доступних боксів на конкретну дату та час"""
        date_str = request.query_params.get('date')
        time_str = request.query_params.get('time')
        if not date_str or not time_str:
            return Response(
                {'error': 'Потрібно вказати параметри date та time'},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return Response(
                {'error': 'Неправильний формат дати або часу'},
                status=status.HTTP_400_BAD_REQUEST)
        available_boxes = []
        for box in Box.objects.filter(is_active=True):
            if box.is_available_at_time(appointment_date, appointment_time):
                conflicting_appointments = Appointment.objects.filter(
                    box=box,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    status__in=['pending', 'confirmed', 'in_progress']
                )
                if not conflicting_appointments.exists():
                    available_boxes.append(box)
        serializer = BoxSerializer(available_boxes, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=['get'],
        permission_classes=[permissions.AllowAny])
    def available_dates(self, request):
        """Отримання доступних дат на наступні 30 днів
        з урахуванням робочих годин боксів та тривалості послуги"""
        from datetime import timedelta

        service_id = request.query_params.get('service_id')
        exclude_appointment_id = request.query_params.get(
            'exclude_appointment_id')

        if not service_id:
            return Response(
                {'error': 'Потрібно вказати service_id'}, status=400)

        try:
            service = Service.objects.get(
                id=service_id)  # pylint: disable=no-member
        except Service.DoesNotExist:  # pylint: disable=no-member
            return Response({'error': 'Послуга не знайдена'}, status=404)

        available_dates = []
        today = datetime.now().date()
        service_duration_minutes = service.duration_minutes or 60

        for i in range(30):
            check_date = today + timedelta(days=i)
            day_name = check_date.strftime('%A').lower()

            # Перевіряємо чи є хоча б один активний бокс
            # з вільним часом на цю дату
            active_boxes = Box.objects.filter(is_active=True)
            for box in active_boxes:
                working_hours = box.get_working_hours_for_day(day_name)
                start = working_hours.get('start')
                end = working_hours.get('end')
                if working_hours and start != '00:00' and end != '00:00':
                    start_time = working_hours.get('start', '09:00')
                    end_time = working_hours.get('end', '18:00')

                    # Конвертуємо час в хвилини для обчислень
                    start_minutes = int(start_time.split(
                        ':')[0]) * 60 + int(start_time.split(':')[1])
                    end_minutes = int(end_time.split(
                        ':')[0]) * 60 + int(end_time.split(':')[1])

                    # Перевіряємо чи є хоча б один вільний часовий слот
                    current_minutes = start_minutes
                    has_available_slot = False

                    while current_minutes + service_duration_minutes <= end_minutes:
                        hours = current_minutes // 60
                        mins = current_minutes % 60
                        time_slot = f"{hours:02d}:{mins:02d}"

                        # Перевіряємо перекриття з існуючими записами
                        start_time_obj = datetime.strptime(
                            time_slot, '%H:%M').time()
                        slot_start_minutes = start_time_obj.hour * 60 + start_time_obj.minute
                        slot_end_minutes = slot_start_minutes + service_duration_minutes

                        # Знаходимо всі записи для цього бокса на цю дату
                        existing_appointments = Appointment.objects.filter(
                            box=box,
                            appointment_date=check_date,
                            status__in=['pending', 'confirmed', 'in_progress']
                        )

                        # Виключаємо поточний запис при редагуванні
                        if exclude_appointment_id:
                            existing_appointments = existing_appointments.exclude(
                                id=exclude_appointment_id)

                        has_conflict = False
                        for appointment in existing_appointments:
                            appointment_start = appointment.appointment_time
                            appointment_start_minutes = (
                                appointment_start.hour * 60 +
                                appointment_start.minute)
                            appointment_end_minutes = appointment_start_minutes + \
                                (appointment.service.duration_minutes or 60)

                            # Перевіряємо чи перекриваються часові проміжки
                            if (slot_start_minutes < appointment_end_minutes and
                                    slot_end_minutes > appointment_start_minutes):
                                has_conflict = True
                                break

                        if not has_conflict:
                            has_available_slot = True
                            break

                        current_minutes += 30  # Крок 30 хвилин

                    if has_available_slot:
                        available_dates.append(check_date.strftime('%Y-%m-%d'))
                        break

        return Response({'available_dates': available_dates})

    @action(
        detail=False, methods=['get'],
        permission_classes=[permissions.AllowAny])
    def available_times(self, request):
        """Отримання доступних часів для конкретної дати з урахуванням тривалості послуги"""
        date_str = request.query_params.get('date')
        service_id = request.query_params.get('service_id')
        exclude_appointment_id = request.query_params.get(
            'exclude_appointment_id')

        if not date_str or not service_id:
            return Response({'error': 'Потрібно вказати date та service_id'}, status=400)

        try:
            # Парсимо дату
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            service = Service.objects.get(id=service_id)

            # Отримуємо день тижня
            day_name = appointment_date.strftime('%A').lower()

            # Знаходимо активні бокси
            active_boxes = Box.objects.filter(is_active=True)
            available_times = []

            for box in active_boxes:
                working_hours = box.get_working_hours_for_day(day_name)
                start = working_hours.get('start')
                end = working_hours.get('end')
                if working_hours and start != '00:00' and end != '00:00':
                    start_time = working_hours.get('start', '09:00')
                    end_time = working_hours.get('end', '18:00')

                    # Конвертуємо час в хвилини для обчислень
                    start_minutes = int(start_time.split(
                        ':')[0]) * 60 + int(start_time.split(':')[1])
                    end_minutes = int(end_time.split(
                        ':')[0]) * 60 + int(end_time.split(':')[1])
                    service_duration_minutes = service.duration_minutes or 60

                    # Генеруємо часові слоти з урахуванням тривалості послуги
                    current_minutes = start_minutes
                    while current_minutes + service_duration_minutes <= end_minutes:
                        hours = current_minutes // 60
                        mins = current_minutes % 60
                        time_slot = f"{hours:02d}:{mins:02d}"

                        # Перевіряємо перекриття з існуючими записами
                        start_time_obj = datetime.strptime(
                            time_slot, '%H:%M').time()
                        slot_start_minutes = start_time_obj.hour * 60 + start_time_obj.minute
                        slot_end_minutes = slot_start_minutes + service_duration_minutes

                        # Знаходимо всі записи для цього бокса на цю дату
                        existing_appointments = Appointment.objects.filter(
                            box=box,
                            appointment_date=appointment_date,
                            status__in=['pending', 'confirmed', 'in_progress']
                        )

                        # Виключаємо поточний запис при редагуванні
                        if exclude_appointment_id:
                            existing_appointments = existing_appointments.exclude(
                                id=exclude_appointment_id)

                        has_conflict = False
                        for appointment in existing_appointments:
                            appointment_start = appointment.appointment_time
                            appointment_start_minutes = (
                                appointment_start.hour * 60 +
                                appointment_start.minute)
                            appointment_end_minutes = appointment_start_minutes + \
                                (appointment.service.duration_minutes or 60)

                            # Перевіряємо чи перекриваються часові проміжки
                            # Новий слот не повинен починатися під час виконання існуючого запису
                            # і не повинен закінчуватися після початку існуючого запису
                            if (slot_start_minutes < appointment_end_minutes and
                                    slot_end_minutes > appointment_start_minutes):
                                has_conflict = True
                                break

                        if not has_conflict:
                            available_times.append(time_slot)

                        current_minutes += 30  # Крок 30 хвилин

            # Видаляємо дублікати та сортуємо
            available_times = sorted(list(set(available_times)))

            return Response({'available_times': available_times})

        except ValueError:
            return Response({'error': 'Неправильний формат дати'}, status=400)
        except Service.DoesNotExist:
            return Response({'error': 'Послуга не знайдена'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class AdminViewSet(viewsets.ViewSet):
    """ViewSet для адміністративних функцій"""
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_context(self):
        """Додаємо мову в контекст серіалізатора"""
        try:
            # ViewSet doesn't have get_serializer_context by default,
            # so we create our own
            language = get_language_from_request(self.request)

            context = {
                'request': self.request,
                'view': self,
                'language': language
            }
            return context
        except Exception as e:
            import traceback
            error_msg = (
                f"Error in AdminViewSet.get_serializer_context: {str(e)}")
            print(error_msg)
            print(f"Traceback: {traceback.format_exc()}")
            # Fallback to basic context
            return {'language': 'uk'}

    @action(detail=False, methods=['get'])
    def statistics(self, _request):
        """Отримання статистики"""
        from datetime import timedelta

        today = timezone.now().date()
        month_ago = today - timedelta(days=30)

        stats = {
            'total_appointments': Appointment.objects.count(),  # pylint: disable=no-member
            'pending_appointments': Appointment.objects.filter(  # pylint: disable=no-member
                status='pending').count(),
            'completed_appointments': Appointment.objects.filter(  # pylint: disable=no-member
                status='completed').count(),
            'total_customers': Customer.objects.count(),  # pylint: disable=no-member
            'blocked_customers': Customer.objects.filter(  # pylint: disable=no-member
                is_blocked=True).count(),
            'total_revenue': Appointment.objects.filter(  # pylint: disable=no-member
                status='completed'
            ).aggregate(total=Sum('total_price'))['total'] or 0,
            'monthly_appointments': Appointment.objects.filter(  # pylint: disable=no-member
                appointment_date__gte=month_ago
            ).count(),
            'services_count': Service.objects.filter(  # pylint: disable=no-member
                is_active=True).count(),
            'revenue_today': Appointment.objects.filter(  # pylint: disable=no-member
                appointment_date=today, status='completed'
            ).aggregate(total=Sum('total_price'))['total'] or 0
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def weekly_schedule(self, request):
        """Отримання розкладу записів на цей тиждень"""
        from datetime import timedelta

        # Отримуємо мову з запиту
        language = get_language_from_request(request)

        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Понеділок
        end_of_week = start_of_week + timedelta(days=6)  # Неділя

        # Отримуємо записи на цей тиждень
        weekly_appointments = Appointment.objects.filter(
            appointment_date__gte=start_of_week,
            appointment_date__lte=end_of_week
        ).select_related('customer__user', 'service', 'box').order_by('appointment_date', 'appointment_time')

        # Отримуємо всі активні бокси
        active_boxes = Box.objects.filter(is_active=True).order_by('name')

        # Словник для перекладу статусів
        status_translations = {
            'pending': {'uk': 'Очікує', 'en': 'Pending'},
            'confirmed': {'uk': 'Підтверджено', 'en': 'Confirmed'},
            'completed': {'uk': 'Завершено', 'en': 'Completed'},
            'cancelled': {'uk': 'Скасовано клієнтом', 'en': 'Cancelled by client'},
            'cancelled_by_admin': {'uk': 'Скасовано адміністратором', 'en': 'Cancelled by administrator'}
        }

        # Групуємо записи по днях і боксах
        schedule = {}
        for i in range(7):
            current_date = start_of_week + timedelta(days=i)
            day_name = current_date.strftime('%A')

            # Словник для перекладу днів тижня
            day_translations = {
                'Monday': {'uk': 'Понеділок', 'en': 'Monday'},
                'Tuesday': {'uk': 'Вівторок', 'en': 'Tuesday'},
                'Wednesday': {'uk': 'Середа', 'en': 'Wednesday'},
                'Thursday': {'uk': 'Четвер', 'en': 'Thursday'},
                'Friday': {'uk': 'П\'ятниця', 'en': 'Friday'},
                'Saturday': {'uk': 'Субота', 'en': 'Saturday'},
                'Sunday': {'uk': 'Неділя', 'en': 'Sunday'}
            }

            day_name_translated = day_translations.get(
                day_name, {}).get(language, day_name)

            day_appointments = weekly_appointments.filter(
                appointment_date=current_date)

            # Групуємо записи по боксах для цього дня
            boxes_schedule = {}
            for box in active_boxes:
                box_appointments = day_appointments.filter(box=box)
                boxes_schedule[box.id] = {
                    'box_id': box.id,
                    'box_name': box.get_name(language),
                    'appointments': []
                }

                for appointment in box_appointments:
                    boxes_schedule[box.id]['appointments'].append({
                        'id': appointment.id,
                        'time': appointment.appointment_time.strftime('%H:%M'),
                        'service_name': appointment.service.get_name(language),
                        'customer_name': appointment.customer.user.get_full_name() if appointment.customer else appointment.guest_name,
                        'status': appointment.status,
                        'status_text': status_translations.get(appointment.status, {}).get(language, appointment.status),
                        'total_price': float(appointment.total_price)
                    })

            # Додаємо записи без призначеного бокса
            unassigned_appointments = day_appointments.filter(box__isnull=True)
            if unassigned_appointments.exists():
                unassigned_name = 'Не призначено' if language == 'uk' else 'Not assigned'
                boxes_schedule['unassigned'] = {
                    'box_id': 'unassigned',
                    'box_name': unassigned_name,
                    'appointments': []
                }

                for appointment in unassigned_appointments:
                    boxes_schedule['unassigned']['appointments'].append({
                        'id': appointment.id,
                        'time': appointment.appointment_time.strftime('%H:%M'),
                        'service_name': appointment.service.get_name(language),
                        'customer_name': appointment.customer.user.get_full_name() if appointment.customer else appointment.guest_name,
                        'status': appointment.status,
                        'status_text': status_translations.get(appointment.status, {}).get(language, appointment.status),
                        'total_price': float(appointment.total_price)
                    })

            schedule[current_date.isoformat()] = {
                'date': current_date.isoformat(),
                'day_name': day_name_translated,
                'day_short': day_name[:3],
                'boxes_schedule': boxes_schedule
            }

        return Response({
            'week_start': start_of_week.isoformat(),
            'week_end': end_of_week.isoformat(),
            'schedule': schedule,
            'boxes': [{'id': box.id, 'name': box.get_name(language)} for box in active_boxes]
        })

    @action(detail=False, methods=['get'])
    def customer_management(self, _request):
        """Управління клієнтами"""
        customers = Customer.objects.select_related(
            'user').all()  # pylint: disable=no-member
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def block_customer(self, _request, pk=None):
        """Блокування клієнта"""
        customer = Customer.objects.get(pk=pk)  # pylint: disable=no-member
        customer.is_blocked = True
        customer.save()
        return Response({'message': 'Клієнта заблоковано'})

    @action(detail=True, methods=['post'])
    def unblock_customer(self, _request, pk=None):
        """Розблокування клієнта"""
        customer = Customer.objects.get(pk=pk)  # pylint: disable=no-member
        customer.is_blocked = False
        customer.save()
        return Response({'message': 'Клієнта розблоковано'})

    # Управління послугами
    @action(detail=False, methods=['get'])
    def services_management(self, _request):
        """Отримання списку всіх послуг для управління"""
        services = Service.objects.select_related(
            'category').all()  # pylint: disable=no-member
        context = self.get_serializer_context()
        serializer = ServiceListSerializer(
            services, many=True, context=context)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_service(self, request):
        """Створення нової послуги"""
        context = self.get_serializer_context()
        context['admin_panel'] = True
        serializer = ServiceSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def get_service_for_edit(self, _request, pk=None):
        """Отримання даних послуги для редагування"""
        try:
            service = Service.objects.get(pk=pk)  # pylint: disable=no-member
            context = self.get_serializer_context()
            context['admin_panel'] = True
            serializer = ServiceSerializer(service, context=context)
            return Response(serializer.data)
        except Service.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {'error': 'Послугу не знайдено'},
                status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['put', 'patch'])
    def update_service(self, request, pk=None):
        """Оновлення послуги"""
        try:
            service = Service.objects.get(pk=pk)  # pylint: disable=no-member
            context = self.get_serializer_context()
            context['admin_panel'] = True
            serializer = ServiceSerializer(
                service, data=request.data, partial=True, context=context)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Service.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {'error': 'Послугу не знайдено'},
                status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'])
    def delete_service(self, _request, pk=None):
        """Видалення послуги"""
        try:
            service = Service.objects.get(pk=pk)  # pylint: disable=no-member
            service.delete()
            return Response({'message': 'Послугу видалено'})
        except Service.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {'error': 'Послугу не знайдено'},
                status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def toggle_service_status(self, _request, pk=None):
        """Зміна статусу послуги (активна/неактивна)"""
        try:
            service = Service.objects.get(pk=pk)  # pylint: disable=no-member
            service.is_active = not service.is_active
            service.save()
            status_msg = 'активовано' if service.is_active else 'деактивовано'
            return Response({
                'message': f'Послугу {status_msg}',
                'is_active': service.is_active
            })
        except Service.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {'error': 'Послугу не знайдено'},
                status=status.HTTP_404_NOT_FOUND)

    # Управління категоріями послуг
    @action(detail=False, methods=['get'])
    def categories_management(self, _request):
        """Отримання списку всіх категорій для управління"""
        categories = ServiceCategory.objects.all()  # pylint: disable=no-member
        context = self.get_serializer_context()
        context['admin_panel'] = True
        serializer = ServiceCategorySerializer(
            categories, many=True, context=context)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_category(self, request):
        """Створення нової категорії"""
        data = request.data.copy()

        # Якщо порядок не вказано або порожній, встановлюємо його автоматично
        if 'order' not in data or data['order'] == '' or data['order'] is None:
            max_order = ServiceCategory.objects.aggregate(Max('order'))[
                'order__max'] or 0
            data['order'] = max_order + 1

        context = self.get_serializer_context()
        context['admin_panel'] = True
        serializer = ServiceCategorySerializer(data=data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put', 'patch'])
    def update_category(self, request, pk=None):
        """Оновлення категорії"""
        try:
            category = ServiceCategory.objects.get(
                pk=pk)  # pylint: disable=no-member
            context = self.get_serializer_context()
            context['admin_panel'] = True
            serializer = ServiceCategorySerializer(
                category, data=request.data, partial=True, context=context)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ServiceCategory.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {'error': 'Категорію не знайдено'},
                status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'])
    def delete_category(self, _request, pk=None):
        """Видалення категорії та всіх послуг в ній"""
        try:
            category = ServiceCategory.objects.get(pk=pk)

            # Отримуємо кількість послуг в категорії
            services = category.services.all()
            services_count = services.count()

            # Підраховуємо кількість записів, які будуть видалені
            appointments_count = 0
            for service in services:
                appointments_count += service.appointment_set.count()

            # Видаляємо всі послуги в категорії (записи видаляться автоматично через CASCADE)
            services.delete()

            # Видаляємо саму категорію
            category.delete()

            message = f'Категорію та {services_count} послуг видалено'
            if appointments_count > 0:
                message += f' (включаючи {appointments_count} записів)'

            return Response({
                'message': message
            })
        except ServiceCategory.DoesNotExist:
            return Response({'error': 'Категорію не знайдено'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def boxes_management(self, _request):
        """Отримання списку боксів"""
        try:
            boxes = Box.objects.all()  # pylint: disable=no-member
            serializer = BoxSerializer(
                boxes, many=True, context=self.get_serializer_context())
            return Response(serializer.data)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def create_box(self, request):
        """Створення нового боксу"""
        try:
            serializer = BoxSerializer(
                data=request.data, context=self.get_serializer_context())
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def update_box(self, request, pk=None):
        """Оновлення боксу"""
        try:
            box = Box.objects.get(id=pk)  # pylint: disable=no-member
            serializer = BoxSerializer(
                box, data=request.data, partial=True,
                context=self.get_serializer_context())
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Box.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {'error': 'Бокс не знайдено'},
                status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'])
    def delete_box(self, _request, pk=None):
        """Видалення боксу"""
        try:
            box = Box.objects.get(id=pk)  # pylint: disable=no-member
            box.delete()
            return Response({'message': 'Бокс видалено'})
        except Box.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {'error': 'Бокс не знайдено'},
                status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def toggle_box_status(self, _request, pk=None):
        """Зміна статусу боксу"""
        try:
            box = Box.objects.get(id=pk)  # pylint: disable=no-member
            box.is_active = not box.is_active
            box.save()
            status_msg = 'активовано' if box.is_active else 'деактивовано'
            return Response({'message': f'Бокс {status_msg}'})
        except Box.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {'error': 'Бокс не знайдено'},
                status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def home_page_management(self, _request):
        """Отримання інформації про головну сторінку для адміністратора"""
        try:
            sto_info = ServiceCatalog.get_sto_info()
            if sto_info:
                serializer = STOInfoSerializer(
                    sto_info, context=self.get_serializer_context())
                return Response(serializer.data)
            return Response(
                {'error': 'Інформація про СТО не знайдена'},
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return Response(
                {'error': f'Помилка отримання даних: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def update_home_page(self, request):
        """Оновлення інформації про головну сторінку"""
        try:
            # Фільтруємо порожні пункти якщо вони є
            data = request.data.copy()
            if 'what_you_can_items' in data and isinstance(data['what_you_can_items'], list):
                data['what_you_can_items'] = [
                    item for item in data['what_you_can_items'] if item and item.strip()]

            result = ServiceCatalog.update_sto_info(data)
            if result['success']:
                serializer = STOInfoSerializer(result['sto_info'])
                return Response(serializer.data)
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return Response(
                {'error': f'Помилка оновлення: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def featured_services(self, _request):
        """Отримання основних послуг для головної сторінки"""
        featured_services = Service.objects.filter(  # pylint: disable=no-member
            is_featured=True, is_active=True)
        serializer = ServiceSerializer(
            featured_services, many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_featured_service(self, _request, pk=None):
        """Зміна статусу основної послуги"""
        try:
            service = Service.objects.get(pk=pk)  # pylint: disable=no-member
            service.is_featured = not service.is_featured
            service.save()
            msg = 'додано до основних' if service.is_featured else 'видалено з основних'
            return Response({
                'message': f'Послугу {msg}',
                'is_featured': service.is_featured
            })
        except Service.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {'error': 'Послугу не знайдено'},
                status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def appointments(self, request):
        """Отримання списку бронювань з фільтрами для адміністратора"""
        # Отримуємо параметри фільтрів
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        box_id = request.query_params.get('box_id')
        service_id = request.query_params.get('service_id')
        appointment_status = request.query_params.get('status')
        customer_name = request.query_params.get('customer_name')
        time_from = request.query_params.get('time_from')
        time_to = request.query_params.get('time_to')
        price_min = request.query_params.get('price_min')
        price_max = request.query_params.get('price_max')

        # Початковий queryset
        queryset = Appointment.objects.select_related(
            'customer__user', 'service', 'box'
        ).order_by('-appointment_date', '-appointment_time')

        # Застосовуємо фільтри
        if date_from:
            queryset = queryset.filter(appointment_date__gte=date_from)

        if date_to:
            queryset = queryset.filter(appointment_date__lte=date_to)

        if box_id:
            queryset = queryset.filter(box_id=box_id)

        if service_id:
            queryset = queryset.filter(service_id=service_id)

        if appointment_status:
            queryset = queryset.filter(status=appointment_status)

        # Фільтр по імені клієнта
        if customer_name:
            queryset = queryset.filter(
                Q(customer__user__first_name__icontains=customer_name) |
                Q(customer__user__last_name__icontains=customer_name) |
                Q(guest_name__icontains=customer_name)
            )

        # Фільтр по часу
        if time_from:
            queryset = queryset.filter(appointment_time__gte=time_from)

        if time_to:
            queryset = queryset.filter(appointment_time__lte=time_to)

        # Фільтр по ціні
        if price_min:
            queryset = queryset.filter(total_price__gte=price_min)

        if price_max:
            queryset = queryset.filter(total_price__lte=price_max)

        # Серіалізуємо результати
        serializer = AppointmentSerializer(
            queryset, many=True, context=self.get_serializer_context())

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel_appointment(self, _request, pk=None):
        """Скасування запису адміністратором"""
        try:
            appointment = Appointment.objects.get(
                pk=pk)  # pylint: disable=no-member

            # Перевіряємо чи можна скасувати запис
            if appointment.status not in ['pending', 'confirmed']:
                return Response(
                    {'error': 'Не можна скасувати запис у поточному статусі'},
                    status=status.HTTP_400_BAD_REQUEST)

            appointment.status = 'cancelled_by_admin'
            appointment.save()

            return Response({'message': 'Запис скасовано адміністратором'})
        except Appointment.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {'error': 'Запис не знайдено'},
                status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def appointment_details(self, _request, pk=None):
        """Отримання деталей запису для адміністратора"""
        try:
            appointment = Appointment.objects.select_related(  # pylint: disable=no-member
                'customer__user', 'service', 'box'
            ).get(pk=pk)

            serializer = AppointmentSerializer(
                appointment, context=self.get_serializer_context())

            return Response(serializer.data)
        except Appointment.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {'error': 'Запис не знайдено'},
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return Response(
                {'error': f'Помилка сервера: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['put', 'patch'])
    def update_customer(self, request, pk=None):
        """Оновлення даних клієнта адміністратором"""
        try:
            customer = Customer.objects.get(pk=pk)  # pylint: disable=no-member
            user = customer.user

            # Перевірка унікальності email
            if 'email' in request.data and request.data['email'] != user.email:
                email_exists = User.objects.filter(  # pylint: disable=no-member
                    email=request.data['email']).exclude(id=user.id).exists()
                if email_exists:
                    return Response(
                        {'error': 'Email вже використовується'},
                        status=status.HTTP_400_BAD_REQUEST)

            # Оновлюємо дані користувача
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            if 'email' in request.data:
                user.email = request.data['email']

            # Обробка зміни пароля
            if 'password' in request.data and request.data['password']:
                try:
                    validate_password(request.data['password'], user)
                    user.set_password(request.data['password'])
                except ValidationError as e:
                    error_messages = []
                    for error in e.error_list:
                        error_str = str(error).lower()
                        if 'too common' in error_str:
                            error_messages.append(
                                'Пароль занадто простий або часто використовується')
                        elif 'too short' in error_str:
                            error_messages.append('Пароль занадто короткий')
                        elif 'too similar' in error_str:
                            error_messages.append(
                                'Пароль занадто схожий на особисті дані')
                        elif 'numeric' in error_str:
                            error_messages.append(
                                'Пароль не може складатися тільки з цифр')
                        else:
                            error_messages.append(str(error))

                    error_msg = 'Помилка валідації пароля: ' + '; '.join(
                        error_messages)
                    return Response(
                        {'error': error_msg},
                        status=status.HTTP_400_BAD_REQUEST)

            user.save()

            # Оновлюємо дані клієнта
            customer.save()

            # Повертаємо оновлені дані
            serializer = CustomerSerializer(customer)

            return Response(serializer.data)
        except Customer.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {'error': 'Клієнта не знайдено'},
                status=status.HTTP_404_NOT_FOUND)
