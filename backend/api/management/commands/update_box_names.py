from django.core.management.base import BaseCommand
from api.models import Box

class Command(BaseCommand):
    help = 'Оновлення англійських назв боксів'

    def handle(self, *args, **options):
        # Словник для перекладу назв боксів
        box_translations = {
            'перший бокс': 'First Box',
            'другий бокс': 'Second Box', 
            'третій бокс': 'Third Box',
            'четвертий бокс': 'Fourth Box',
            'п\'ятий бокс': 'Fifth Box',
            'шостий бокс': 'Sixth Box',
            'сьомий бокс': 'Seventh Box',
            'восьмий бокс': 'Eighth Box',
            'дев\'ятий бокс': 'Ninth Box',
            'десятий бокс': 'Tenth Box'
        }
        
        updated_count = 0
        
        for box in Box.objects.all():
            uk_name = box.name
            if uk_name in box_translations and not box.name_en:
                box.name_en = box_translations[uk_name]
                box.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Оновлено: {uk_name} -> {box.name_en}")
                )
                updated_count += 1
            elif box.name_en:
                self.stdout.write(f"Вже має англійську назву: {uk_name} -> {box.name_en}")
            else:
                self.stdout.write(f"Немає перекладу для: {uk_name}")
        
        self.stdout.write(
            self.style.SUCCESS(f"\nЗагалом оновлено: {updated_count} боксів")
        )
