# Generated by Django 2.2.4 on 2020-01-31 09:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_data_tahun_html'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='data_tahun_html',
            name='uploader',
        ),
    ]