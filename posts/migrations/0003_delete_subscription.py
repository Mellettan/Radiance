# Generated by Django 5.1 on 2024-08-10 00:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0002_post_liked_by"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Subscription",
        ),
    ]
