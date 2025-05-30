# Generated by Django 5.2 on 2025-05-29 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0020_notification_related_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="profile_image",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="partnercompany",
            name="logo",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="venue",
            name="logo",
            field=models.URLField(blank=True, null=True),
        ),
    ]
