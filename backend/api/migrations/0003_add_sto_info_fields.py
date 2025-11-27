# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_servicecategory_alter_service_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stoinfo',
            name='motto',
            field=models.CharField(blank=True, max_length=200, verbose_name='Девіз'),
        ),
        migrations.AddField(
            model_name='stoinfo',
            name='welcome_text',
            field=models.TextField(blank=True, verbose_name='Привітальний текст'),
        ),
    ] 