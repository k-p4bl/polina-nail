# Generated by Django 4.1 on 2024-05-20 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sign_up', '0002_alter_persondataanddate_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disableddates',
            name='creator_is_human',
            field=models.BooleanField(default=True, editable=False),
        ),
    ]
