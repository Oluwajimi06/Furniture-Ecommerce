# Generated by Django 5.1 on 2024-08-31 18:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sitepages', '0005_cart'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together=set(),
        ),
    ]
