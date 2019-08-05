# Generated by Django 2.2.2 on 2019-08-19 13:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0029_auto_20190816_0926'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderLineBaseProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='Quantity')),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.BaseProduct')),
                ('order_line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.OrderLine')),
            ],
        ),
        migrations.AddField(
            model_name='orderline',
            name='options',
            field=models.ManyToManyField(blank=True, through='store.OrderLineBaseProduct', to='store.BaseProduct', verbose_name='Options'),
        ),
    ]