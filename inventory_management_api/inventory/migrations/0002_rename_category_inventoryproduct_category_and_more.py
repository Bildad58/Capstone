# Generated by Django 5.1 on 2024-09-26 20:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventoryproduct',
            old_name='Category',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='inventoryproduct',
            old_name='Description',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='inventoryproduct',
            old_name='Name',
            new_name='name',
        ),
    ]
