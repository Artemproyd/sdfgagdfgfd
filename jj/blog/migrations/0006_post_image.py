# Generated by Django 3.2.16 on 2024-02-23 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20240223_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(default=None, upload_to='Post_images', verbose_name='Фото'),
        ),
    ]
