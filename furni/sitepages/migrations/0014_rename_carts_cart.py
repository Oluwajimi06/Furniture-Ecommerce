# Generated by Django 5.1 on 2024-09-04 23:27

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sitepages', '0013_rename_cart_carts'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Carts',
            new_name='Cart',
        ),
    ]
