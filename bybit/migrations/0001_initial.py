# Generated by Django 4.2.4 on 2023-09-23 01:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeBybit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('order_q', models.IntegerField()),
                ('order_p', models.FloatField(default=0)),
                ('price', models.FloatField(default=0)),
                ('lim_min', models.FloatField(default=0)),
                ('lim_max', models.FloatField(default=0)),
                ('fiat', models.CharField(max_length=10)),
                ('token', models.CharField(max_length=10)),
                ('buy_sell', models.CharField(default=10)),
                ('exchange', models.CharField(max_length=20)),
                ('adv_no', models.CharField(default='#', max_length=50)),
                ('payments', models.JSONField()),
                ('best_payment', models.CharField(blank=True, max_length=20, null=True)),
                ('available', models.FloatField(default=0, max_length=30)),
                ('available_rub', models.FloatField(default=0, max_length=30)),
            ],
            options={
                'db_table': 'exchange_bybit',
            },
        ),
    ]
