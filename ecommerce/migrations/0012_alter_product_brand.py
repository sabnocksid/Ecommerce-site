# Generated by Django 5.1.1 on 2024-10-14 07:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0011_brand_color_product_brand_product_colors_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(default='None', on_delete=django.db.models.deletion.CASCADE, to='ecommerce.brand'),
        ),
    ]
