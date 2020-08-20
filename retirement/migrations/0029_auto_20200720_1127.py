# Generated by Django 2.2.12 on 2020-07-20 15:27

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('retirement', '0028_auto_20200601_1613'),
    ]

    operations = [
        migrations.CreateModel(
            name='RetreatType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=253, verbose_name='Name')),
                (
                    'name_en',
                    models.CharField(
                        max_length=253,
                        null=True,
                        verbose_name='Name',
                    )
                ),
                (
                    'name_fr',
                    models.CharField(
                        max_length=253,
                        null=True,
                        verbose_name='Name',
                    )
                ),
                ('minutes_before_display_link', models.IntegerField(verbose_name='Minute before displaying the link')),
            ],
            options={
                'verbose_name': 'Type of retreat',
                'verbose_name_plural': 'Types of retreat',
            },
        ),
        migrations.AddField(
            model_name='historicalretreat',
            name='type_new',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='retirement.RetreatType'),
        ),
        migrations.AddField(
            model_name='retreat',
            name='type_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='retirement.RetreatType'),
        ),
        migrations.CreateModel(
            name='HistoricalRetreatType',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True,
                                           db_index=True, verbose_name='ID')),
                (
                'name', models.CharField(max_length=253, verbose_name='Name')),
                ('name_fr', models.CharField(max_length=253, null=True,
                                             verbose_name='Name')),
                ('name_en', models.CharField(max_length=253, null=True,
                                             verbose_name='Name')),
                ('minutes_before_display_link', models.IntegerField(
                    verbose_name='Minute before displaying the link')),
                ('history_id',
                 models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason',
                 models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(
                    choices=[('+', 'Created'), ('~', 'Changed'),
                             ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True,
                                                   on_delete=django.db.models.deletion.SET_NULL,
                                                   related_name='+',
                                                   to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Type of retreat',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]