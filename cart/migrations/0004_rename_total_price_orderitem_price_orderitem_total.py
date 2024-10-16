# Generated by Django 5.1.1 on 2024-10-16 04:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_order_payment_method_order_shipping_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='total_price',
            new_name='price',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]