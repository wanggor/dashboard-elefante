# Generated by Django 2.2.4 on 2020-01-31 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_data_bulan_unit_data_tahun_unit_data_tanggal'),
    ]

    operations = [
        migrations.AddField(
            model_name='data_tanggal',
            name='bulan',
            field=models.IntegerField(default=1, verbose_name='Bulan'),
            preserve_default=False,
        ),
    ]