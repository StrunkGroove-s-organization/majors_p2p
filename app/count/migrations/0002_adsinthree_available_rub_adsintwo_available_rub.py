# Generated by Django 4.2.5 on 2023-12-08 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('count', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='adsinthree',
            name='available_rub',
            field=models.FloatField(default=0.0, max_length=30),
        ),
        migrations.AddField(
            model_name='adsintwo',
            name='available_rub',
            field=models.FloatField(default=0.0, max_length=30),
        ),
    ]
