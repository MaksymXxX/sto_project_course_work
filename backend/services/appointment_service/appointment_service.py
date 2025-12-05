"""Сервіс для роботи із записами на обслуговування."""

from datetime import datetime

from django.utils import timezone
from ...api.models import Appointment, Box
from ...api.data_access import DataAccessLayer


class AppointmentService:
    """Сервіс записів згідно з архітектурною діаграмою"""

    @staticmethod
    def create_appointment(data, user=None):
        """Створення нового запису"""
        try:
            service = DataAccessLayer.get_service_by_id(data['service_id'])
            if not service:
                return {
                    'success': False,
                    'error': 'Послугу не знайдено'
                }

            # Перевіряємо доступність боксів
            appointment_date = datetime.strptime(
                data['appointment_date'], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(
                data['appointment_time'], '%H:%M').time()

            # Знаходимо вільний бокс
            available_box = AppointmentService._find_available_box(
                appointment_date, appointment_time, service)
            if not available_box:
                return {
                    'success': False,
                    'error': (
                        'На цей час немає доступних боксів. '
                        'Спробуйте інший час або дату.'
                    )
                }

            # Розраховуємо ціну з урахуванням знижки
            original_price = service.price
            final_price = original_price

            # Застосовуємо знижку якщо є користувач
            if user:
                # Перевіряємо чи у користувача є customer профіль
                if hasattr(user, 'customer') and user.customer:
                    final_price = user.customer.apply_discount_to_price(
                        original_price)
                    print(
                        f"Застосовано знижку для користувача "
                        f"{user.username}: {original_price} -> {final_price}")
                else:
                    # Якщо у користувача немає customer профілю, створюємо його
                    from ...api.models import Customer  # pylint: disable=import-outside-toplevel
                    try:
                        customer = Customer.objects.get(
                            user=user)  # pylint: disable=no-member
                    except Customer.DoesNotExist:  # pylint: disable=no-member
                        customer = Customer.objects.create(
                            user=user)  # pylint: disable=no-member

                    # Тепер застосовуємо знижку
                    final_price = customer.apply_discount_to_price(
                        original_price)
                    print(
                        f"Створено customer профіль та застосовано "
                        f"знижку для користувача {user.username}: "
                        f"{original_price} -> {final_price}")
            else:
                print(
                    "Користувач не авторизований, знижка не застосовується: "
                    f"{original_price}"
                )

            appointment = DataAccessLayer.create_appointment(
                customer=user.customer if user else None,
                guest_name=data.get('guest_name', ''),
                guest_phone=data.get('guest_phone', ''),
                guest_email=data.get('guest_email', ''),
                service=service,
                box=available_box,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                notes=data.get('notes', ''),
                total_price=final_price
            )

            return {
                'success': True,
                'appointment': appointment
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def update_appointment(appointment_id, data, user=None):
        """Оновлення існуючого запису"""
        try:
            # Отримуємо існуючий запис
            appointment = DataAccessLayer.get_appointment_by_id(
                appointment_id, user)

            if not appointment:
                return {
                    'success': False,
                    'error': 'Запис не знайдено'
                }

            # Перевіряємо чи користувач є власником запису
            if appointment.customer and appointment.customer.user != user:
                return {
                    'success': False,
                    'error': 'Доступ заборонено'
                }

            # Перевіряємо чи можна редагувати запис
            if appointment.status not in ['pending']:
                return {
                    'success': False,
                    'error': 'Не можна редагувати запис у поточному статусі'
                }

            # Перевіряємо час до запису (не менше 2 годин)
            now = timezone.now()
            appointment_datetime = datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time,
            )
            appointment_datetime = timezone.make_aware(appointment_datetime)

            time_difference = appointment_datetime - now
            # 2 години = 7200 секунд
            if time_difference.total_seconds() < 7200:
                return {
                    'success': False,
                    'error': (
                        'Не можна редагувати запис менше ніж за 2 години '
                        'до його початку. Зверніться до адміністратора '
                        'для внесення змін.'
                    )
                }

            # Отримуємо нову послугу
            service = DataAccessLayer.get_service_by_id(data['service_id'])
            if not service:
                return {
                    'success': False,
                    'error': 'Послугу не знайдено'
                }

            # Розраховуємо ціну з урахуванням знижки
            original_price = service.price
            final_price = original_price

            # Застосовуємо знижку якщо є користувач
            if user:
                # Перевіряємо чи у користувача є customer профіль
                if hasattr(user, 'customer') and user.customer:
                    final_price = user.customer.apply_discount_to_price(
                        original_price)
                    print(
                        f"Застосовано знижку при редагуванні для "
                        f"користувача {user.username}: "
                        f"{original_price} -> {final_price}")
                else:
                    # Якщо у користувача немає customer профілю, створюємо його
                    from ...api.models import Customer  # pylint: disable=import-outside-toplevel
                    try:
                        customer = Customer.objects.get(
                            user=user)  # pylint: disable=no-member
                    except Customer.DoesNotExist:  # pylint: disable=no-member
                        customer = Customer.objects.create(
                            user=user)  # pylint: disable=no-member

                    # Тепер застосовуємо знижку
                    final_price = customer.apply_discount_to_price(
                        original_price)
                    print(
                        f"Створено customer профіль та застосовано "
                        f"знижку при редагуванні для користувача "
                        f"{user.username}: {original_price} -> {final_price}")
            else:
                print(
                    f"Користувач не авторизований при редагуванні, "
                    f"знижка не застосовується: {original_price}")

            # Перевіряємо чи змінилася дата або час
            new_appointment_date = datetime.strptime(
                data['appointment_date'], '%Y-%m-%d').date()
            new_appointment_time = datetime.strptime(
                data['appointment_time'], '%H:%M').time()

            date_or_time_changed = (
                appointment.appointment_date != new_appointment_date or
                appointment.appointment_time != new_appointment_time or
                appointment.service != service
            )

            if date_or_time_changed:
                # Знаходимо новий вільний бокс
                available_box = AppointmentService._find_available_box(
                    new_appointment_date,
                    new_appointment_time,
                    service,
                    appointment_id,
                )

                if not available_box:
                    return {
                        'success': False,
                        'error': (
                            'На цей час немає доступних боксів. '
                            'Спробуйте інший час або дату.'
                        )
                    }

                # Оновлюємо запис з новим боксом
                updated_appointment = DataAccessLayer.update_appointment_by_id(
                    appointment_id=appointment_id,
                    service=service,
                    box=available_box,
                    appointment_date=new_appointment_date,
                    appointment_time=new_appointment_time,
                    guest_name=data.get('guest_name', ''),
                    guest_phone=data.get('guest_phone', ''),
                    guest_email=data.get('guest_email', ''),
                    notes=data.get('notes', ''),
                    total_price=final_price
                )
            else:
                # Оновлюємо тільки інші поля без зміни бокса
                updated_appointment = DataAccessLayer.update_appointment_by_id(
                    appointment_id=appointment_id,
                    service=service,
                    box=appointment.box,  # Залишаємо той самий бокс
                    appointment_date=new_appointment_date,
                    appointment_time=new_appointment_time,
                    guest_name=data.get('guest_name', ''),
                    guest_phone=data.get('guest_phone', ''),
                    guest_email=data.get('guest_email', ''),
                    notes=data.get('notes', ''),
                    total_price=final_price
                )

            return {
                'success': True,
                'appointment': updated_appointment
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def _find_available_box(
            appointment_date, appointment_time, service=None,
            exclude_appointment_id=None):
        """Знаходження доступного боксу для заданої дати та часу
        з урахуванням тривалості послуги"""
        # Отримуємо активні бокси
        active_boxes = Box.objects.filter(
            is_active=True)  # pylint: disable=no-member

        for box in active_boxes:
            # Перевіряємо чи бокс працює в цей час
            if not box.is_available_at_time(
                    appointment_date, appointment_time):
                continue

            # Перевіряємо перекриття з існуючими записами
            if service:
                service_duration_minutes = service.duration_minutes
            else:
                service_duration_minutes = 60

            # Конвертуємо час в хвилини
            start_time_obj = appointment_time
            slot_start_minutes = (
                start_time_obj.hour * 60 + start_time_obj.minute)
            slot_end_minutes = slot_start_minutes + service_duration_minutes

            # Знаходимо всі записи для цього бокса на цю дату
            existing_appointments = Appointment.objects.filter(  # pylint: disable=no-member
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
                duration = appointment.service.duration_minutes or 60
                appointment_end_minutes = (
                    appointment_start_minutes + duration)

                # Перевіряємо чи перекриваються часові проміжки
                if (slot_start_minutes < appointment_end_minutes and
                        slot_end_minutes > appointment_start_minutes):
                    has_conflict = True
                    break

            if not has_conflict:
                return box

        return None

    @staticmethod
    def get_user_appointments(user):
        """Отримання записів користувача"""
        return DataAccessLayer.get_appointments_by_user(user)

    @staticmethod
    def get_appointment_by_id(appointment_id, user=None):
        """Отримання запису за ID"""
        return DataAccessLayer.get_appointment_by_id(appointment_id, user)

    @staticmethod
    def confirm_appointment(appointment_id):
        """Підтвердження запису"""
        appointment = DataAccessLayer.get_appointment_by_id(
            appointment_id)
        if appointment:
            DataAccessLayer.update_appointment(
                appointment, status='confirmed')
            return True
        return False

    @staticmethod
    def complete_appointment(appointment_id, completion_data):
        """Завершення обслуговування"""
        appointment = DataAccessLayer.get_appointment_by_id(appointment_id)
        if appointment:
            # Оновлення статусу запису
            DataAccessLayer.update_appointment(appointment, status='completed')

            # Створення запису в історії
            DataAccessLayer.create_service_history(
                appointment=appointment,
                actual_duration=completion_data.get(
                    'actual_duration', appointment.service.duration),
                final_price=completion_data.get(
                    'final_price', appointment.total_price),
                mechanic_notes=completion_data.get('mechanic_notes', '')
            )

            # Нарахування балів лояльності
            if appointment.customer:
                points_to_add = int(appointment.total_price)
                DataAccessLayer.update_customer(
                    appointment.customer,
                    loyalty_points=appointment.customer.loyalty_points + points_to_add
                )

                service_name = appointment.service.name
                DataAccessLayer.create_loyalty_transaction(
                    customer=appointment.customer,
                    transaction_type='earned',
                    points=points_to_add,
                    description=f'Нарахування за послугу: {service_name}'
                )

            return True
        return False

    @staticmethod
    def get_service_history(user):
        """Отримання історії обслуговування"""
        return DataAccessLayer.get_service_history_by_user(user)

    @staticmethod
    def get_loyalty_transactions(user):
        """Отримання транзакцій лояльності"""
        return DataAccessLayer.get_loyalty_transactions_by_user(user)
