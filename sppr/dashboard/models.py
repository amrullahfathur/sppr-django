from django.core import validators
from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from mptt.models import MPTTModel, TreeForeignKey
from decimal import Decimal
import datetime


# Create your models here.


class ProvinsiId(models.Model):
    # Field name made lowercase.
    provinsi_id = models.IntegerField(
        db_column='Provinsi_ID', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_provinsi = models.TextField(
        db_column='Nama Provinsi', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Provinsi_ID'

    def __str__(self) -> str:
        return self.nama_provinsi

class UnitsatuanID(models.Model):
    # Field name made lowercase.
    unitsatuan_id = models.IntegerField(
        db_column='Unitsatuan_ID', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_satuan = models.TextField(
        db_column='Nama_Satuan', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Unitsatuan_ID'
    
    def __str__(self) -> str:
        return self.nama_satuan
    
    


def year_choices():
    return [(r, r) for r in range(2019, datetime.date.today().year + 5)]


def current_year():
    return datetime.date.today().year


class NewIsuStrategis(MPTTModel):
    nama_isu = models.CharField(max_length=400, blank=False, null=False, default='')
    provinsi = models.ForeignKey(
        ProvinsiId, on_delete=models.SET_NULL, db_column='provinsi', blank=False, null=True)
    tahun = models.IntegerField(choices=year_choices(), default=2019)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')
    data_pendukung = models.TextField(max_length=500, blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ['nama_isu']

    def __str__(self) -> str:
        return f'{self.provinsi} - {self.nama_isu}'


class IsuStrategis(MPTTModel):
    nama_isu = models.CharField(max_length=400, blank=True, null=True, default='')
    provinsi = models.ForeignKey(
        ProvinsiId, on_delete=models.SET_NULL, db_column='provinsi', blank=True, null=True)
    tahun = models.IntegerField(choices=year_choices(), default=2019)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['nama_isu']

    def __str__(self) -> str:
        return f'{self.provinsi} - {self.nama_isu}'


class TujuanLFA(models.Model):
    nama_tujuan = models.TextField(blank=False, null=False, default='')
    provinsi = models.ForeignKey(
        "ProvinsiId", on_delete=models.SET_NULL, blank=False, null=True)
    tahun = models.IntegerField(choices=year_choices(), default=2019)
    indikator = models.TextField(max_length=500, blank=True, null=True)
    sumber_data = models.TextField(max_length=500, blank=True, null=True)
    asumsi = models.TextField(max_length=500, blank=True, null=True)
    baseline = models.FloatField(default=0, blank=True, null=True)
    tahun_anggaran = models.FloatField(default=0, blank=True, null=True)
    target = models.FloatField(default=0, blank=True, null=True)
    unitsatuanbaseline = models.ForeignKey(
        "UnitsatuanID", on_delete=models.SET_NULL, blank=True, null=True, related_name='unitsatuan_baseline_tujuan')
    unit_satuan_baseline = models.TextField(max_length=500, blank=True, null=True)
    unitsatuantarget = models.ForeignKey(
        "UnitsatuanID", on_delete=models.SET_NULL, blank=True, null=True, related_name='unitsatuan_target_tujuan')
    unit_satuan_target = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.provinsi} - {self.nama_tujuan}'


class SasaranLFA(models.Model):
    tujuan = models.ForeignKey(
        'TujuanLFA', on_delete=models.CASCADE, blank=False, null=False, default='')
    nama_sasaran = models.TextField(blank=False, null=False)
    indikator = models.TextField(max_length=500, blank=True, null=True)
    sumber_data = models.TextField(max_length=500, blank=True, null=True)
    asumsi = models.TextField(max_length=500, blank=True, null=True)
    target = models.FloatField(default=0, blank=True, null=True)
    baseline = models.FloatField(default=0, blank=True, null=True)
    tahun_anggaran = models.FloatField(default=0, blank=True, null=True)
    pengaruh_sasaran_tujuan = models.FloatField(default=0, blank=True, null=True)
    unitsatuanbaseline = models.ForeignKey(
        "UnitsatuanID", on_delete=models.SET_NULL, blank=True, null=True, related_name='unitsatuan_baseline_sasaran')
    unit_satuan_baseline = models.TextField(max_length=500, blank=True, null=True)
    unitsatuantarget = models.ForeignKey(
        "UnitsatuanID", on_delete=models.SET_NULL, blank=True, null=True, related_name='unitsatuan_target_sasaran')
    unit_satuan_target = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self) -> str:
        try:
            return f'{self.tujuan.nama_tujuan} - {self.nama_sasaran}'
        except:
            return f'{"Belum ada tujuan"} - {self.nama_sasaran}'

    @property
    def pengaruh_sasaran_tujuan(self):

        # Algoritma Korelasi & Regresi
        return 0


class OutputLFA(models.Model):
    sasaran = models.ForeignKey(
        'SasaranLFA', on_delete=models.CASCADE, blank=False, null=False, default='')
    nama_output = models.TextField(blank=False, null=False)
    indikator = models.TextField(max_length=500, blank=True, null=True)
    sumber_data = models.TextField(max_length=500, blank=True, null=True)
    asumsi = models.TextField(max_length=500, blank=True, null=True)
    baseline = models.FloatField(default=0, blank=True, null=True)
    tahun_anggaran = models.FloatField(default=0, blank=True, null=True)
    target = models.FloatField(default=0, blank=True, null=True)
    creation_time = models.DateField(auto_now_add=True, blank=True, null=True)
    unitsatuanbaseline = models.ForeignKey(
        "UnitsatuanID", on_delete=models.SET_NULL, blank=True, null=True, related_name='unitsatuan_baseline_output')
    unit_satuan_baseline = models.TextField(max_length=500, blank=True, null=True)
    unitsatuantarget = models.ForeignKey(
        "UnitsatuanID", on_delete=models.SET_NULL, blank=True, null=True, related_name='unitsatuan_target_output')
    unit_satuan_target = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self) -> str:
        try:
            try:
                return f'{self.sasaran.tujuan.provinsi} - {self.nama_output}'
            except:
                return f'{self.sasaran.nama_sasaran} - {self.nama_output}'
        except:
            return f'{"Belum ada sasaran"} - {self.nama_output}'

    @property
    def pengaruh_output_sasaran(self):

        # Algoritma Korelasi & Regresi
        return 0
# New Model Corresponding to Longlist and Shortlist Model


class DeputiId(models.Model):
    # Field name made lowercase.
    deputi_id = models.IntegerField(db_column='Deputi_ID', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_deputi = models.TextField(db_column='Nama Deputi')

    class Meta:
        managed = False
        db_table = 'Deputi_ID'

    def __str__(self) -> str:
        return self.nama_deputi


class DirektoratId(models.Model):
    # Field name made lowercase.
    direktorat_id = models.IntegerField(
        db_column='Direktorat_ID', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_direktorat = models.TextField(
        db_column='Nama Direktorat', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Direktorat_ID'

    def __str__(self) -> str:
        return self.nama_direktorat


class KlId(models.Model):
    # Field name made lowercase.
    kl_id = models.IntegerField(db_column='KL_ID', primary_key=True)
    nama = models.TextField(db_column='Nama')  # Field name made lowercase.
    # Field name made lowercase.
    singkatan = models.TextField(db_column='Singkatan', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'KL_ID'

    def __str__(self) -> str:
        return f'{self.nama} ({self.singkatan})'


class KabupatenId(models.Model):
    # Field name made lowercase.
    provinsi_id = models.IntegerField(db_column='Provinsi_ID')
    # Field name made lowercase.
    kabupaten_id = models.IntegerField(
        db_column='Kabupaten_ID', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_kabupaten = models.TextField(db_column='Nama Kabupaten')

    class Meta:
        managed = False
        db_table = 'Kabupaten_ID'

    def __str__(self) -> str:
        return self.nama_kabupaten


class KawasanprioritasId(models.Model):
    # Field name made lowercase.
    kp_id = models.AutoField(db_column='KP_ID', primary_key=True)
    # Field name made lowercase.
    kawasan_prioritas = models.TextField(
        db_column='Kawasan_Prioritas', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'KawasanPrioritas_ID'

    def __str__(self) -> str:
        return self.kawasan_prioritas


class MajorprojectId(models.Model):
    # Field name made lowercase.
    mp_id = models.IntegerField(db_column='MP_ID', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_major_project = models.TextField(
        db_column='Nama Major Project', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'MajorProject_ID'

    def __str__(self) -> str:
        return self.nama_major_project


class MitraId(models.Model):
    # Field name made lowercase.
    mitra_id = models.IntegerField(db_column='Mitra_ID', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_direktorat_mitra = models.TextField(db_column='Nama Direktorat Mitra')
    # Field name made lowercase.
    deputi = models.IntegerField(db_column='Deputi', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Mitra_ID'

    def __str__(self) -> str:
        return self.nama_direktorat_mitra


class ProyekId(models.Model):
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_proyek = models.TextField(db_column='Nama Proyek')
    # Field name made lowercase.
    proyek_idd = models.IntegerField(db_column='Proyek_IDD', primary_key=True)

    class Meta:
        managed = False
        db_table = 'Proyek_ID'

    def __str__(self) -> str:
        return self.nama_proyek


class StatusId(models.Model):
    # Field name made lowercase.
    status_id = models.IntegerField(db_column='Status_ID', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_status = models.TextField(
        db_column='Nama Status', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Status_ID'

    def __str__(self) -> str:
        return self.nama_status


class SubtemaId(models.Model):
    # Field name made lowercase.
    sub_tema_id = models.IntegerField(
        db_column='Sub_Tema_ID', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    subtema_rkp_2022 = models.TextField(
        db_column='Subtema RKP 2022', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SubTema_ID'

    def __str__(self) -> str:
        return self.subtema_rkp_2022


class SubditId(models.Model):
    # Field name made lowercase.
    subdit_id = models.IntegerField(db_column='Subdit_ID', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_subdit = models.TextField(
        db_column='Nama Subdit', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Subdit_ID'

    def __str__(self) -> str:
        return self.nama_subdit


class SumberdataId(models.Model):
    # Field name made lowercase.
    sumberdata_id = models.IntegerField(
        db_column='SumberData_ID', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_sumber = models.TextField(
        db_column='Nama Sumber', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SumberData_ID'

    def __str__(self) -> str:
        return self.nama_sumber


class TahapanId(models.Model):
    # Field name made lowercase.
    tahapan_id = models.IntegerField(db_column='Tahapan_ID', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_tahapan = models.TextField(
        db_column='Nama Tahapan', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Tahapan_ID'

    def __str__(self) -> str:
        return self.nama_tahapan


class UserStatus(models.Model):
    # Field name made lowercase.
    user_status = models.IntegerField(
        db_column='User_Status', primary_key=True)
    # Field name made lowercase. Field renamed to remove unsuitable characters.
    nama_status = models.TextField(
        db_column='Nama Status', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'User_Status'

    def __str__(self) -> str:
        return self.nama_status


class Longlist(models.Model):

    bool_choices = [(True, 'YES'), (False, 'NO')]

    # ro_id = models.IntegerField(blank=True, null=True)
    provinsi = models.ForeignKey(
        'ProvinsiId', on_delete=models.SET_NULL, db_column='provinsi', blank=True, null=True)
    judul_proyek = models.TextField(null=False)
    # This field type is a guess.
    lokasi_proyek = models.TextField(blank=True, null=True)
    lokasi_kabupaten = models.ForeignKey(
        KabupatenId, on_delete=models.SET_NULL, db_column='lokasi_kabupaten', blank=True, null=True)
    target_2021 = models.FloatField(blank=True, null=True)
    target_2022 = models.FloatField(blank=True, null=True)
    target_2023 = models.FloatField(blank=True, null=True)
    target_2024 = models.FloatField(blank=True, null=True)
    target_2025 = models.FloatField(blank=True, null=True)
    unit_satuan = models.TextField(blank=True, null=True)
    indikasi_pendanaan_2021 = models.FloatField(blank=True, null=True)
    indikasi_pendanaan_2022 = models.FloatField(blank=True, null=True)
    indikasi_pendanaan_2023 = models.FloatField(blank=True, null=True)
    indikasi_pendanaan_2024 = models.FloatField(blank=True, null=True)
    sumber_data = models.ForeignKey(
        'SumberdataId', on_delete=models.SET_NULL, db_column='sumber_data', blank=True, null=True)
    ket_sumber_data = models.TextField(
        db_column='ket_ sumber_data', blank=True, null=True)
    # Field name made lowercase.
    kl_pelaksana = models.ForeignKey(
        KlId, on_delete=models.SET_NULL, db_column='KL_pelaksana', blank=True, null=True)
    ket_kl_pelaksana = models.TextField(
        db_column='ket_KL_pelaksana', blank=True, null=True)
    shortlist_2022 = models.BooleanField(
        blank=True, null=True, choices=bool_choices)
    shortlist_2023 = models.BooleanField(
        blank=True, null=True, choices=bool_choices)
    isu_strategis = models.TextField(blank=True, null=True, default="")
    # Field name made lowercase.
    tujuan_lfa = models.TextField(
        db_column='tujuan_LFA', blank=True, null=True, default="")
    # Field name made lowercase.
    sasaran_lfa = models.TextField(
        db_column='sasaran_LFA', blank=True, null=True, default="")
    # Field name made lowercase.
    output_lfa = models.TextField(
        db_column='output_LFA', blank=True, null=True, default="")
    # Field name made lowercase.
    mp = models.ForeignKey('MajorprojectId', on_delete=models.SET_NULL,
                           db_column='MP', blank=True, null=True)
    status_usulan = models.ForeignKey(
        'StatusId', on_delete=models.SET_NULL, db_column='status_usulan', blank=True, null=True)
    sumber_bahasan = models.TextField(blank=True, null=True)
    taging_kawasan_prioritas = models.ForeignKey(
        KawasanprioritasId, on_delete=models.SET_NULL, db_column='taging_kawasan_prioritas', blank=True, null=True)
    prioritas_tahun_2022 = models.TextField(blank=True, null=True)
    prioritas_tahun_2023 = models.TextField(blank=True, null=True)
    prioritas_tahun_2024 = models.TextField(blank=True, null=True)
    jenis_project = models.ForeignKey(
        'ProyekId', on_delete=models.SET_NULL, db_column='jenis_project', blank=True, null=True)
    sub_tema_rkp = models.TextField(blank=True, null=True)
    klasifikasi_proyek = models.TextField(blank=True, null=True)
    jenis_impact = models.TextField(blank=True, null=True)
    staging_perkembangan = models.TextField(blank=True, null=True)
    keterangan = models.TextField(blank=True, null=True)
    usulan_baru = models.BooleanField(
        blank=True, null=True, default=False, choices=bool_choices)

    shortlist = models.BooleanField(
        blank=True, null=True, default=False, choices=bool_choices)
    prarakorgub = models.BooleanField(
        blank=True, null=True, default=False, choices=bool_choices)
    rakorgub = models.BooleanField(
        blank=True, null=True, default=False, choices=bool_choices)
    rakortekbang = models.BooleanField(
        blank=True, null=True, default=False, choices=bool_choices)
    musrenbangprov = models.BooleanField(
        blank=True, null=True, default=False, choices=bool_choices)
    musrenbangnas = models.BooleanField(
        blank=True, null=True, default=False, choices=bool_choices)
    endorsement = models.BooleanField(
        blank=True, null=True, default=False, choices=bool_choices)

    tahun_longlist = models.IntegerField(
        choices=year_choices(), blank=True, null=True)

    output_test = models.ForeignKey(
        'OutputLFA', on_delete=models.SET_NULL, db_column='output_test', blank=True, null=True)
    isu_strategis_test = models.ForeignKey(
        'IsuStrategis', models.DO_NOTHING, db_column='isu_strategis_test', blank=True, null=True)

    def __str__(self) -> str:
        return self.judul_proyek

    class Meta:
        managed = False
        db_table = 'Longlist'

    def save(self, *args, **kwargs):
        super(Longlist, self).save(*args, **kwargs)
        if self.shortlist == True:
            if SkoringProyek.objects.filter(proyek=self).exists() == False:
                SkoringProyek.objects.create(proyek=self)
        elif self.shortlist == False:
            if SkoringProyek.objects.filter(proyek=self).exists():
                SkoringProyek.objects.get(proyek=self).delete()


class CsvLongList(models.Model):
    file_name = models.FileField(upload_to="csv_longlist", null=False, validators=[
                                 FileExtensionValidator(['csv'])])
    uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"File name: {self.file_name}"


class DataKawasanPrioritas(models.Model):
    id = models.IntegerField(primary_key=True)
    nama_kawasan_prioritas = models.TextField(blank=True, null=True)
    perencanaan = models.FloatField(blank=True, null=True)
    kesiapan_kawasan = models.FloatField(blank=True, null=True)
    potensi_konektivitas = models.FloatField(blank=True, null=True)
    dampak_ekonomi = models.FloatField(blank=True, null=True)
    dampak_lingkungan = models.FloatField(blank=True, null=True)
    risiko_bencana = models.FloatField(blank=True, null=True)
    total_nilai = models.FloatField(blank=True, null=True)
    dampak_ekonomi_revisi = models.FloatField(blank=True, null=True)
    kawasan_prioritas = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Data_Kawasan_Prioritas'

    def __str__(self) -> str:
        return self.nama_kawasan_prioritas


class SkoringProyek(models.Model):

    bobot_korelasi_sasaran = 0.2
    bobot_korelasi_output = 0.45
    bobot_skor_MP = 0.15
    bobot_investasi = 0.2

    # id = models.IntegerField(primary_key=True)
    proyek = models.OneToOneField(
        Longlist, on_delete=models.CASCADE)
    nilai_raw_korelasi_sasaran = models.FloatField(
        blank=True, null=True, default=0)
    nilai_raw_korelasi_output = models.FloatField(
        blank=True, null=True, default=0)
    nilai_raw_MP = models.FloatField(blank=True, null=True, default=0)
    nilai_raw_investasi = models.FloatField(blank=True, null=True, default=0)

    @property
    def total_skoring(self):
        total = (self.nilai_raw_korelasi_output * self.bobot_korelasi_output) + (self.nilai_raw_korelasi_sasaran *
                                                                                 self.bobot_korelasi_sasaran) + (self.nilai_raw_MP * self.bobot_skor_MP) + (self.nilai_raw_investasi * self.bobot_investasi)
        return round(Decimal(total), 2)

    def __str__(self) -> str:
        return self.proyek.judul_proyek
