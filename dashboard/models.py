from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class SaldoAwal(models.Model):
    tahun = models.IntegerField()
    unit = models.TextField()
    material = models.IntegerField()
    nilai = models.FloatField()

    last_updated = models.DateTimeField('Update Terakhir',auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.PROTECT)

class MovementType(models.Model):
    deskripsi = models.CharField('Deskripsi',max_length=255)
    kode = models.IntegerField('Movement Type')

    last_updated = models.DateTimeField('Update Terakhir',auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.PROTECT)

class Plant(models.Model):
    kode = models.CharField('Kode Plant',max_length=255)
    departement = models.CharField('Departemen',max_length=255)
    nama = models.CharField('Nama Plant',max_length=255)
    perusahaan = models.CharField('Perusahaan',max_length=255, default="PT PETROKIMIA GRESIK")
    kode_pos = models.IntegerField('Kode Pos', default=None)
    lokasi = models.CharField('Lokasi',max_length=255, default=None)

    latitude = models.CharField('Latitude',max_length=255, default=None)
    longitude = models.CharField('longitude',max_length=255, default=None)
    keterangan = models.CharField('Keterangan',max_length=4000)
    email = models.EmailField('Email')
    number = models.CharField('Phone Number',max_length=255)

    last_updated = models.DateTimeField('Update Terakhir',auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.PROTECT)

class Material(models.Model):
    kode = models.IntegerField('Kode Material')
    deskripsi = models.CharField('Deskripsi',max_length=255)
    kategori = models.CharField('Kategori',max_length=255)
    informasi = models.TextField('Informasi',max_length=4000)
    nama_kelompok = models.CharField('Nama Kelompok',max_length=255)

    last_updated = models.DateTimeField('Update Terakhir',auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.PROTECT)


class data_bulan_unit(models.Model):
    tahun = models.IntegerField('Tahun')
    bulan = models.IntegerField('Bulan')
    material = models.CharField('Material',max_length=255)
    data = models.TextField('Description')

    confirm = models.BooleanField("Konfirmasi")
    valid = models.BooleanField("Validasi")

    last_updated = models.DateTimeField('Update Terakhir',auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.PROTECT)

class data_tahun_unit(models.Model):
    tahun = models.IntegerField('Tahun')
    bulan = models.IntegerField('Bulan')
    material = models.CharField('Material',max_length=255)
    data = models.TextField('Description')

    confirm = models.BooleanField("Konfirmasi")
    valid = models.BooleanField("Validasi")

    last_updated = models.DateTimeField('Update Terakhir',auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.PROTECT)

class data_tanggal(models.Model):
    tahun = models.IntegerField('Tahun')
    posting_date = models.DateTimeField('posting_date')
    material = models.CharField('Material',max_length=255)
    kategori = models.CharField('Kategori',max_length=255)
    plant = models.CharField('Plant',max_length=255)
    receiving_plant = models.CharField('Receiving Plant',max_length=255)
    description = models.TextField('Description',max_length=4000)
    value = models.FloatField('Value',)

    confirm = models.BooleanField("Konfirmasi")
    valid = models.BooleanField("Validasi")

    last_updated = models.DateTimeField('Update Terakhir',auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.PROTECT)
