# Generated by Django 5.1.2 on 2025-02-04 08:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_remove_customer_email_remove_customer_first_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'permissions': [('send_private_email', 'Can send private email to user by the button')]},
        ),
    ]
