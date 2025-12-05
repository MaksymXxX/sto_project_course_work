from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from backend.api.models import Customer

class Command(BaseCommand):
    help = 'Створює Customer запис для адміністратора'

    def handle(self, *args, **options):
        try:
            # Знаходимо адміністратора
            admin_user = User.objects.filter(is_staff=True).first()

            if not admin_user:
                self.stdout.write(
                    self.style.ERROR('Адміністратор не знайдено')  # pylint: disable=no-member
                )
                return

            # Перевіряємо чи вже є Customer для цього користувача
            customer, created = Customer.objects.get_or_create(  # pylint: disable=no-member,unused-variable
                user=admin_user,
                defaults={
                    'phone': '+380441234567',
                    'address': 'Адреса адміністратора',
                    'loyalty_points': 0,
                    'is_blocked': False
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(  # pylint: disable=no-member
                        f'Створено Customer запис для {admin_user.username}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(  # pylint: disable=no-member
                        f'Customer запис для {admin_user.username} вже існує'
                    )
                )

        except Exception as e:  # pylint: disable=broad-exception-caught
            self.stdout.write(
                self.style.ERROR(f'Помилка: {str(e)}')  # pylint: disable=no-member
            ) 