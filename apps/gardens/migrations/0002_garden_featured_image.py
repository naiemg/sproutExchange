# Generated by Django 3.1.3 on 2020-12-06 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gardens', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='garden',
            name='featured_image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]