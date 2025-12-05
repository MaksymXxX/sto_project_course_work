from django.core.management.base import BaseCommand
from api.models import STOInfo


class Command(BaseCommand):
    help = 'Перевірка даних СТО в базі даних'

    def handle(self, *args, **options):
        sto_info_list = STOInfo.objects.all()  # pylint: disable=no-member

        if sto_info_list.exists():
            self.stdout.write(
                self.style.SUCCESS(  # pylint: disable=no-member
                    f'Знайдено {sto_info_list.count()} записів СТО:')
            )
            for sto_info in sto_info_list:
                self.stdout.write(f'ID: {sto_info.id}')
                self.stdout.write(f'Назва: {sto_info.name}')
                self.stdout.write(f'Девіз: {sto_info.motto}')
                self.stdout.write(f'Активна: {sto_info.is_active}')
                self.stdout.write('---')
        else:
            self.stdout.write(
                self.style.WARNING('Записів СТО не знайдено')  # pylint: disable=no-member
            ) 