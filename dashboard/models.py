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

class Harga(models.Model):
    tahun = models.IntegerField()
    bulan = models.IntegerField()
    material = models.IntegerField()
    nilai = models.FloatField()

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

class data_tahun_html(models.Model):
    tahun = models.IntegerField('Tahun')
    material = models.CharField('Material',max_length=255)
    data = models.TextField('Description')

    last_updated = models.DateTimeField('Update Terakhir',auto_now_add=True)
    # uploader = models.ForeignKey(User, on_delete=models.PROTECT)

class data_tanggal(models.Model):
    tahun = models.IntegerField('Tahun')
    bulan = models.IntegerField('Bulan')
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

class Data_pemakain(models.Model):
    tahun = models.IntegerField('Tahun')
    bulan = models.IntegerField('Bulan')
    material = models.CharField('Material',max_length=255)
    plant = models.CharField('Plant',max_length=255)
    value = models.FloatField('Value',)

class Notulensi(models.Model):
    lock = models.BooleanField("Lock")
    tahun = models.IntegerField('Tahun')
    bulan = models.IntegerField('Bulan')
    nomor = models.CharField('Nomor',max_length=255)
    hari_tanggal = models.CharField('Hari_tanggal',max_length=255)
    ruang = models.CharField('Hari_tanggal',max_length=255)
    pukul = models.CharField('Pukul',max_length=255)
    hal = models.CharField('Hal',max_length=255)
    info = models.CharField('Info',max_length=255)
    pimpinan_rapat = models.CharField('Pimpinan_rapat',max_length=255)
    notulis = models.CharField('Notulis',max_length=255)
    jabatan = models.CharField('Jabatan',max_length=255)
    nama_pimpinan = models.CharField('Nama_pimpinan',max_length=255)

    total = models.CharField('total',max_length=255)

    perihal = models.TextField('Perihal')
    perhatian =  models.TextField('Perhatian')
    rekons = models.TextField('Rekons')
    catatan = models.TextField('Catatan')
    hal_disampaikan = models.TextField('Hal_disampaikan')
    bertanda_bintang = models.TextField('Bertanda_bintang')

    distribusi = models.TextField('Distribusi')



#TrackNtrace

class Unit(models.Model):
    id_user             = models.CharField(max_length=100)
    name                = models.CharField(max_length=100)
    kontak              = models.CharField(max_length=100)
    current_latitude    = models.FloatField()
    current_longitude   = models.FloatField()
    current_directions  = models.FloatField()
    current_speed       = models.FloatField()
    time_step           = models.FloatField()
    accuracy            = models.FloatField()
    last_accumulate     = models.DateTimeField()

class DataAnalize(models.Model):
    cost_estimate   = models.FloatField()
    cost_real       = models.FloatField()
    revenue         = models.FloatField()
    score           = models.FloatField()
    time            = models.DateTimeField()
    unit            = models.ForeignKey(Unit, on_delete=models.PROTECT)

class DataSensor(models.Model):
    latitude        = models.FloatField()
    longitude       = models.FloatField()
    directions      = models.FloatField()
    speed           = models.FloatField()
    distance        = models.FloatField()
    accuracy        = models.FloatField()
    time_step       = models.FloatField()
    time            = models.DateTimeField()
    unit            = models.ForeignKey(Unit, on_delete=models.PROTECT)
