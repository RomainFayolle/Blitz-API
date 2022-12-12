# Generated by Django 3.2.8 on 2022-12-12 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0045_auto_20221103_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalorder',
            name='is_made_by_admin',
            field=models.BooleanField(default=False, verbose_name='Is made by admin'),
        ),
        migrations.AddField(
            model_name='order',
            name='is_made_by_admin',
            field=models.BooleanField(default=False, verbose_name='Is made by admin'),
        ),
    ]