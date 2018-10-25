# Generated by Django 2.0.2 on 2018-10-14 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workplace', '0016_address_line_2_blank'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalreservation',
            name='cancelation_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Cancelation date'),
        ),
        migrations.AddField(
            model_name='historicalreservation',
            name='cancelation_reason',
            field=models.CharField(blank=True, choices=[('U', 'User canceled'), ('TD', 'Timeslot deleted'), ('TM', 'Timeslot modified')], max_length=100, null=True, verbose_name='Cancelation reason'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='cancelation_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Cancelation date'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='cancelation_reason',
            field=models.CharField(blank=True, choices=[('U', 'User canceled'), ('TD', 'Timeslot deleted'), ('TM', 'Timeslot modified')], max_length=100, null=True, verbose_name='Cancelation reason'),
        ),
    ]