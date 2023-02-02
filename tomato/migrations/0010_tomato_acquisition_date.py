# Generated by Django 3.2.8 on 2023-02-02 13:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tomato', '0009_alter_tomato_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='tomato',
            name='acquisition_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Acquisition date'),
        ),
    ]
