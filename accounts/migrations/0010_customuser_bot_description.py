# Generated by Django 5.1 on 2024-08-22 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_customuser_is_bot'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='bot_description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
