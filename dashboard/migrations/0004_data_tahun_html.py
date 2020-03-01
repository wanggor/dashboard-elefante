# Generated by Django 2.2.4 on 2020-01-31 09:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0003_data_tanggal_bulan'),
    ]

    operations = [
        migrations.CreateModel(
            name='data_tahun_html',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tahun', models.IntegerField(verbose_name='Tahun')),
                ('material', models.CharField(max_length=255, verbose_name='Material')),
                ('data', models.TextField(verbose_name='Description')),
                ('last_updated', models.DateTimeField(auto_now_add=True, verbose_name='Update Terakhir')),
                ('uploader', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]