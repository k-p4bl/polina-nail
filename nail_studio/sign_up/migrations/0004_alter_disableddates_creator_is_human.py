# Generated by Django 4.1 on 2024-05-28 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sign_up', '0003_alter_disableddates_creator_is_human'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disableddates',
            name='creator_is_human',
            field=models.BooleanField(default=True, editable=False, verbose_name='Создано человеком'),
        ),
    ]
