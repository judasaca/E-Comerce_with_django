# Generated by Django 4.1.5 on 2023-02-04 02:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_address_zip_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='memberchip',
            new_name='membership',
        ),
    ]
