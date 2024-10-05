# Generated by Django 5.1.1 on 2024-10-02 12:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0007_alter_sale_cashier_alter_saleitem_sale'),
        ('products', '0002_alter_product_branch'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='cashier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='staff.employee'),
        ),
        migrations.AlterField(
            model_name='saleitem',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='sale_items', to='products.product'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='saleitem',
            name='sale',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='pos.sale'),
            preserve_default=False,
        ),
    ]
