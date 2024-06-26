# Generated by Django 5.0.3 on 2024-05-29 01:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-created_at'], 'verbose_name': 'Товар', 'verbose_name_plural': 'Товары'},
        ),
        migrations.AddField(
            model_name='product',
            name='discount',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Скидка'),
        ),
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='/products/default.png', upload_to='products/products/%Y/%m/%d', verbose_name='Изображение'),
        ),
    ]
