# Generated by Django 5.0.3 on 2024-05-31 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_alter_product_options_product_discount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='products/products/default.jpg', upload_to='images/products/%Y/%m/%d', verbose_name='Изображение'),
        ),
    ]