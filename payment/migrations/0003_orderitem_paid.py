# Generated by Django 5.0.3 on 2024-05-24 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
