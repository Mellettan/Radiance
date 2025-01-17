# Generated by Django 5.1 on 2024-08-16 23:02

import django.core.validators
from django.db import migrations, models

import accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_customuser_temp_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="avatar",
            field=models.ImageField(
                default="default_avatar.png",
                upload_to=accounts.models.user_avatar_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["jpg", "jpeg", "png"]
                    )
                ],
            ),
        ),
    ]
