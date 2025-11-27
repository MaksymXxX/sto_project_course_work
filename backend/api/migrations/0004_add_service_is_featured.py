# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_add_sto_info_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='is_featured',
            field=models.BooleanField(default=False, verbose_name='Основна послуга'),
        ),
    ] 