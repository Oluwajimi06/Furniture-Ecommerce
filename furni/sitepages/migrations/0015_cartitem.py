# Generated by Django 5.1 on 2024-09-04 23:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitepages', '0014_rename_carts_cart'),
    ]

    operations = [
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='sitepages.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sitepages.product')),
            ],
        ),
    ]
