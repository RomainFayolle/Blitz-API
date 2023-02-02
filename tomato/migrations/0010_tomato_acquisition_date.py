# Generated by Django 3.2.8 on 2023-02-01 18:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tomato', '0009_alter_tomato_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='tomato',
            name='acquisition_date',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Acquisition date'),
        ),
    ]