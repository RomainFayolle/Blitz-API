# Generated by Django 3.2.8 on 2022-12-16 18:49

from django.db import migrations


def populate_orderline_total_cost(apps, schema_editor):
    from django.contrib.contenttypes.models import ContentType
    OrderLine = apps.get_model('store', 'OrderLine')

    order_lines = OrderLine.objects.all()
    for line in order_lines:
        # total_cost is the value of old cost.
        line.total_cost = line.cost
        try:
            ct = ContentType.objects.get(model=line.content_type.model,
                                         app_label=line.content_type.app_label)
            content_object = ct.get_object_for_this_type(pk=line.object_id)
            base_price = content_object.price if content_object.price else 0
        except line.content_type.DoesNotExist:
            # Old data was deleted
            base_price = line.cost
        coupon_value = line.coupon_real_value if line.coupon_real_value else 0
        line.cost = base_price - coupon_value
        # No need to apply coupon on total_cost for it copies old cost
        line.save()


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0047_auto_20221214_1614'),
    ]

    operations = [
        migrations.RunPython(populate_orderline_total_cost),
    ]
