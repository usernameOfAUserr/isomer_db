# Generated by Django 5.0.2 on 2024-04-24 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper_app', '0004_substance_validation_message_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='substance',
            name='url',
            field=models.CharField(default='unknown', max_length=200),
        ),
    ]