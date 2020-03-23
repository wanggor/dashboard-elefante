# Generated by Django 2.2.4 on 2020-03-22 11:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0007_notulensi'),
    ]

    operations = [
        migrations.CreateModel(
            name='Harga',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tahun', models.IntegerField()),
                ('bulan', models.IntegerField()),
                ('material', models.IntegerField()),
                ('nilai', models.FloatField()),
                ('last_updated', models.DateTimeField(auto_now_add=True, verbose_name='Update Terakhir')),
                ('uploader', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
