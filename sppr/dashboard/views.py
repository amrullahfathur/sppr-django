from typing import List
from django.shortcuts import render, redirect
from .models import *
from django.db.models import Count 
from django.http import JsonResponse
from ajax_datatable.views import AjaxDatatableView
from .forms import CsvModelForm, LonglistForm, Output_LFA_Form, Sasaran_LFA_Form, SkoringProyekForm, Tujuan_LFA_Form, IsuStrategisForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import csv
from distutils import util
import os
import mimetypes
from django.http.response import HttpResponse
from django.contrib import messages
from django.http import HttpResponseRedirect
from json import dumps

"""

    User Authentication

"""
# User Login

def loginUser(request):

    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')

        return render(request, 'auth/login.html')

# User Logout


def logoutUser(request):
    logout(request)
    return redirect('index')

############################


"""

    Routing

"""
# Route to Landing Page


def index(request):

    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return render(request, 'index.html')

# Route to Dashboard Main Page


@login_required(login_url='login')
def dashboard(request):
    total_provinsi = ProvinsiId.objects.count()
    total_isu_strategis = IsuStrategis.objects.count()
    total_mp = MajorprojectId.objects.count()
    total_prioritas_nasional = DataKawasanPrioritas.objects.count()
    return render(request, 'dashboard/index.html', {
        'provinsi' : total_provinsi,
        'mp' : total_mp,
        'isu_strategis' : total_isu_strategis,
        'prioritas_nasional' : total_prioritas_nasional,
    })

# Route to Profil Daerah Page


@login_required(login_url='login')
def profil(request, menu):
    # Page entities
    judul = cek_profil(menu)
    template = cek_profil_template(menu)
    content = cek_content(menu)
    tahun = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

    # Isu strategis & LFA entities
    provinsi = ProvinsiId.objects.all()
    request_get = request.GET.get('options', "0-0")
    pilih_provinsi = int(request_get.split("-")[0])
    pilih_tahun = int(request_get.split("-")[1])
    pilih_isu_strategis = int(request.GET.get('pilih_isu_strategis', 0))
    tujuans = []
    isu_strategis = []
    output_korelasi = []
    data = {} # Variable to be used for Javascript Template

    if request.method == "POST":

        if 'pilih_provinsi' in request.POST:
            # Pilih Provinsi dropdown select option logic
            pilih_provinsi = request.POST.get("pilih_provinsi", 0)
        else:
            # Pilih Isu Strategis dropdown select option logic
            response = request.POST.get("pilih_isu_strategis", "")

            pilih_provinsi = response.split("-")[0]
            pilih_isu_strategis = response.split("-")[1]

        # Convert String into Integer
        pilih_provinsi = int(pilih_provinsi)
        pilih_isu_strategis = int(pilih_isu_strategis)

    # Data Structure logic for Halaman Analisa Kerangka Logis
    if menu == "akl":
        if (pilih_provinsi != 0 and pilih_tahun != 0):
            tujuans = TujuanLFA.objects.all().filter(provinsi_id=pilih_provinsi, tahun=pilih_tahun)
        elif (pilih_tahun != 0):
            tujuans = TujuanLFA.objects.all().filter(tahun=pilih_tahun)
        else:
            tujuans = TujuanLFA.objects.all().filter(provinsi_id=pilih_provinsi)

        data['tujuan'] = []
        data['sasaran'] = []
        data['output'] = []

        for tujuan in tujuans:
            data['tujuan'].append({
                'id': tujuan.id,
                'nama_tujuan': tujuan.nama_tujuan
            })

            for sasaran in tujuan.sasaranlfa_set.all():
                data['sasaran'].append({
                    'tujuan_id': tujuan.id,
                    'id' : sasaran.id,
                    'nama_sasaran': sasaran.nama_sasaran
                })

                for output in sasaran.outputlfa_set.all():
                    data['output'].append({
                        'sasaran_id': sasaran.id,
                        'id' : output.id,
                        'nama_output': output.nama_output
                    })

                    # Load longlist and query SkoringProyek
                    for longlist in output.longlist_set.all():
                        skoring = SkoringProyek.objects.get(proyek_id=longlist.id)
                        output_korelasi.append({
                            "judul_proyek": longlist.judul_proyek,
                            "skoring": skoring
                        })

    # Data Structure logic for Halaman Permasalahan Isu Strategis
    if menu == "pis" or menu == "pis_diagram":
        isu_strategis = NewIsuStrategis.objects.all().filter(provinsi_id=pilih_provinsi, level=0)

        if pilih_isu_strategis != 0: # Pilih Isu Strategis dropdown selected
            head = NewIsuStrategis.objects.get(id=pilih_isu_strategis)

            data = {
                'name': head.nama_isu, 
            'fill': '#260df0', 
                'children': [{
                    'name': children_lvl_1.nama_isu,
                    'fill': '#301bdd',
                    'children': [{
                        'name': children_lvl_2.nama_isu,
                        'fill': '#4a3ace',
                        'children': [{
                            'name': children_lvl_3.nama_isu,
                            'fill': '#7467dd',
                            'children': [{
                                'name': children_lvl_4.nama_isu,
                                'fill': '#cbc5f8'
                            } for children_lvl_4 in children_lvl_3.get_children()]
                        } for children_lvl_3 in children_lvl_2.get_children()]
                    } for children_lvl_2 in children_lvl_1.get_children()]
                } for children_lvl_1 in head.get_children()] 
            }

    dataJSON = dumps(data)

    return render(
        request, 
        f'profil/{template}.html', 
        {
            'judul': judul, 
            'content': content, 
            'tahun': tahun,
            'pilih_provinsi': pilih_provinsi,
            'pilih_tahun': pilih_tahun,
            'pilih_isu_strategis': pilih_isu_strategis,
            'provinsi': provinsi,
            'isu_strategis': isu_strategis,
            'tujuans': tujuans,
            'output_korelasi': output_korelasi,
            "dataJSON": dataJSON
        }
    )

# Route to Kebutuhan Daerah Page


@login_required(login_url='login')
def kebdaerah(request, menu):

    sub_menu = ""
    dataView = ""
    chartDataView = ""
    judul = cek_kebdaerah(menu)
    content = {}
    status_upload = ""

    if menu == "longlist":
        dataView = "longlist"
        chartDataView = "longlistChartView"
        form = CsvModelForm(request.POST or None, request.FILES or None)

        try:
            if form.is_valid():
                row_uploaded = 0
                obj = form.save()

                # Read data from csv

                with open(obj.file_name.path, 'r') as f:
                    reader = csv.reader(f)

                    for i, row in enumerate(reader):
                        if i == 0:
                            pass
                        elif row[2] == "":
                            pass
                        else:
                            Longlist.objects.create(
                                judul_proyek=row[2],
                                provinsi=ProvinsiId(
                                    provinsi_id=int(row[1])),
                                lokasi_kabupaten=KabupatenId(
                                    kabupaten_id=int(row[4])),
                                lokasi_proyek=row[5],
                                target_2021=float(row[6]),
                                target_2022=float(row[7]),
                                target_2023=float(row[8]),
                                target_2024=float(row[9]),
                                target_2025=float(row[10]),
                                unit_satuan=row[11],
                                # indikasi_pendanaan_2021=float(row[12]),
                                # indikasi_pendanaan_2022=float(row[13]),
                                # indikasi_pendanaan_2023=float(row[14]),
                                # indikasi_pendanaan_2024=float(row[15]),
                                sumber_data=SumberdataId(
                                    sumberdata_id=int(row[17])),
                                ket_sumber_data=row[18],
                                kl_pelaksana=KlId(kl_id=int(row[20])),
                                ket_kl_pelaksana=row[21],
                                shortlist_2022=bool(
                                    util.strtobool(row[22])),
                                shortlist_2023=bool(
                                    util.strtobool(row[23])),
                                isu_strategis=row[24],
                                tujuan_lfa=row[25],
                                sasaran_lfa=row[26],
                                output_lfa=row[27],
                                mp=MajorprojectId(mp_id=int(row[29])),
                                status_usulan=StatusId(
                                    status_id=int(row[31])),
                                sumber_bahasan=row[32],
                                taging_kawasan_prioritas=KawasanprioritasId(
                                    kp_id=int(row[34])),
                                prioritas_tahun_2022=row[35],
                                prioritas_tahun_2023=row[36],
                                prioritas_tahun_2024=row[37],
                                jenis_project=ProyekId(
                                    proyek_idd=int(row[39])),
                                sub_tema_rkp=row[40],
                                klasifikasi_proyek=row[41],
                                jenis_impact=row[42],
                                staging_perkembangan=row[43],
                                keterangan=row[44],
                                usulan_baru=bool(
                                    util.strtobool(row[45])),
                                shortlist=bool(
                                    util.strtobool(row[46])),
                                prarakorgub=bool(
                                    util.strtobool(row[47])),
                                rakorgub=bool(
                                    util.strtobool(row[48])),
                                rakortekbang=bool(
                                    util.strtobool(row[49])),
                                musrenbangprov=bool(
                                    util.strtobool(row[50])),
                                musrenbangnas=bool(
                                    util.strtobool(row[51])),
                                endorsement=bool(
                                    util.strtobool(row[52]))

                            )
                            row_uploaded += 1

                # content[status_upload] = f'Berhasil Mengunggah {row_uploaded} Objek Data.'
                return redirect('/kebdaerah/longlist', content)

        except:
            content['status_upload'] = f'Terdapat Kesalahan Dalam Mengunggah Data. Cek Kembali Format Data.'
            return redirect('/kebdaerah/longlist', content)

        content = {'form': form}
        sub_menu = "longlist"

    elif menu == "prioritas":
        dataView = "skoring_lfa"
        chartDataView = "endoresementChartView"
        sub_menu = "endorsement"

    elif menu == "forum":
        dataView = "kesepakatan-forum"
        sub_menu = "ckfp"

    elif menu == "logis":
        # Initialize local variable only for menu == "logis"
        tujuans = []
        data = {} # Variable to be used for Javascript Template
        output_korelasi = []

        sub_menu = "kerangka-logis"
        tahun = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
        provinsi = ProvinsiId.objects.all()
        request_get = request.GET.get('options', "0-0")
        pilih_provinsi = int(request_get.split("-")[0])
        pilih_tahun = int(request_get.split("-")[1])

        if (pilih_provinsi != 0 and pilih_tahun != 0):
            tujuans = TujuanLFA.objects.all().filter(provinsi_id=pilih_provinsi, tahun=pilih_tahun)
        elif (pilih_tahun != 0):
            tujuans = TujuanLFA.objects.all().filter(tahun=pilih_tahun)
        else:
            tujuans = TujuanLFA.objects.all().filter(provinsi_id=pilih_provinsi)

        data['tujuan'] = []
        data['sasaran'] = []
        data['output'] = []

        for tujuan in tujuans:
            data['tujuan'].append({
                'id': tujuan.id,
                'nama_tujuan': tujuan.nama_tujuan
            })

            for sasaran in tujuan.sasaranlfa_set.all():
                data['sasaran'].append({
                    'tujuan_id': tujuan.id,
                    'id' : sasaran.id,
                    'nama_sasaran': sasaran.nama_sasaran
                })

                for output in sasaran.outputlfa_set.all():
                    data['output'].append({
                        'sasaran_id': sasaran.id,
                        'id' : output.id,
                        'nama_output': output.nama_output
                    })

                    # Load longlist and query SkoringProyek
                    for longlist in output.longlist_set.all():
                        skoring = SkoringProyek.objects.get(proyek_id=longlist.id)
                        output_korelasi.append({
                            "judul_proyek": longlist.judul_proyek,
                            "skoring": skoring
                        })

        dataJSON = dumps(data)

        content['tahun'] = tahun
        content['tujuans'] = tujuans
        content['provinsi'] = provinsi
        content['dataJSON'] = dataJSON
        content['pilih_tahun'] = pilih_tahun
        content['pilih_provinsi'] = pilih_provinsi

    else:
        sub_menu = "error"

    content["judul"] = judul
    content["dataView"] = dataView

    return render(request, f'kebutuhan_daerah/{sub_menu}.html', content)

# Route to Proyek Daerah Page


@login_required(login_url='login')
def proyek(request, menu):

    judul = cek_proyek(menu)

    return render(request, 'proyek/index.html', {'judul': judul})

# Route to Kajian Kewilayahan


@login_required(login_url="login")
def kajian_wilayah(request):

    return render(request, 'kajian_wilayah/index.html')


# Route to Monev Spasial


@login_required(login_url="login")
def monev_spasial(request):

    return render(request, 'monev_spasial/index.html')
############################


"""

    Routing Support

"""


def cek_profil(menu):

    if menu == "ku":
        judul = "Kondisi Umum Wilayah Regional I"
    elif menu == "pis":
        judul = "Permasalahan Isu Strategis"
    elif menu == "akl":
        judul = "Analisis Kerangka Logis"
    elif menu == "akp":
        judul = "Analisis Kawasan Prioritas"
    elif menu == "aceh":
        judul = "Kondisi Umum Wilayah Aceh"
    elif menu == "sumaterabarat":
        judul = "Kondisi Umum Wilayah Sumatera Barat"
    elif menu == "sumaterautara":
        judul = "Kondisi Umum Wilayah Sumatera Utara"
    elif menu == "jambi":
        judul = "Kondisi Umum Wilayah Jambi"
    elif menu == "bengkulu":
        judul = "Kondisi Umum Wilayah Bengkulu"
    elif menu == "bangkabelitung":
        judul = "Kondisi Umum Wilayah Bangka Belitung"
    elif menu == "sumateraselatan":
        judul = "Kondisi Umum Wilayah Sumatera Selatan"
    elif menu == "riau":
        judul = "Kondisi Umum Wilayah Riau"
    elif menu == "kepulauanriau":
        judul = "Kondisi Umum Wilayah Kepulauan Riau"
    elif menu == "lampung":
        judul = "Kondisi Umum Wilayah Lampung"
    elif menu == "banten":
        judul = "Kondisi Umum Wilayah Banten"
    elif menu == "dkijakarta":
        judul = "Kondisi Umum Wilayah DKI Jakarta"
    elif menu == "jawabarat":
        judul = "Kondisi Umum Wilayah Jawa Barat"
    elif menu == "jawatengah":
        judul = "Kondisi Umum Wilayah Jawa Tengah"
    elif menu == "diy":
        judul = "Kondisi Umum Wilayah Daerah Istimewa Yogyakarta"
    elif menu == "bali":
        judul = "Kondisi Umum Wilayah Bali"
    elif menu == "jawatimur":
        judul = "Kondisi Umum Wilayah Jawa Timur"
    else:
        judul = "Kesalahan Memilih Menu"

    return judul


def cek_content(menu):
    template = None
    if menu == "aceh":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/bf53f8e1e7494042b70d1cf739838601"
    elif menu == "ku":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/60b9db129c4c4f5ab79f4fa8c30b7f9e"
    elif menu == "sumaterabarat":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/ee0befefe0e4425da5a4f11d69475cc6"
    elif menu == "sumaterautara":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/b40c48d5e33d4259aaac7bf783b4f11b"
    elif menu == "jambi":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/b0cb7d450003489bb3beb5b148e91801"
    elif menu == "bengkulu":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/7230f3738de94355ba9e161134e26453"
    elif menu == "bangkabelitung":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/8f2768f275024ce18f459830bdef8c65"
    elif menu == "sumateraselatan":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/fa9adec2980c49a99f605a45ad691b71"
    elif menu == "riau":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/2a0d677b3c0840fca87948bbfb46900f"
    elif menu == "kepulauanriau":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/28949063aca549f596732f167f390836"
    elif menu == "lampung":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/8aa01ff1c78b4911835d92a22a57d91a"
    elif menu == "banten":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/80475af1daaa4a0a8e22a5e415a7ee14"
    elif menu == "dkijakarta":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/7b7384248e904e928845a9a044d751cd"
    elif menu == "jawabarat":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/942452b008cf46548eabdbc222b2302d"
    elif menu == "jawatengah":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/cb1ca19e1cd64ce793feca475f7cd4fc"
    elif menu == "diy":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/2b68130db02b4d7d99103383fe138736"
    elif menu == "bali":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/088fb805d40e4eeaba7dfeeda46bc726"
    elif menu == "jawatimur":
        template = "https://geospasial.bappenas.go.id/portal/apps/storymaps/stories/853f8a4a830a4eb090b00bd626438429"
    else:
        template = None

    return template


def cek_profil_template(menu):
    template = ""
    if menu == "ku":
        template = "index"
    elif menu == "pis":
        template = "isu-strategis"
    elif menu == "pis_diagram":
        template = "isu-strategis-diagram"
    elif menu == "akl":
        template = "kerangka-logis"
    elif menu == "akp":
        template = "kawasan-prioritas"
    elif menu == "aceh":
        template = "index"
    elif menu == "sumaterabarat":
        template = "index"
    elif menu == "sumaterautara":
        template = "index"
    elif menu == "jambi":
        template = "index"
    elif menu == "bengkulu":
        template = "index"
    elif menu == "bangkabelitung":
        template = "index"
    elif menu == "sumateraselatan":
        template = "index"
    elif menu == "riau":
        template = "index"
    elif menu == "kepulauanriau":
        template = "index"
    elif menu == "lampung":
        template = "index"
    elif menu == "banten":
        template = "index"
    elif menu == "dkijakarta":
        template = "index"
    elif menu == "jawabarat":
        template = "index"
    elif menu == "jawatengah":
        template = "index"
    elif menu == "diy":
        template = "index"
    elif menu == "bali":
        template = "index"
    elif menu == "jawatimur":
        template = "index"

    return template


def cek_kebdaerah(menu):

    if menu == "longlist":
        judul = "Daftar Panjang Proyek"
    elif menu == "prioritas":
        judul = "Daftar Proyek Prioritas"
    elif menu == "forum":
        judul = "Catatan Kesepakatan Forum perencanaan"
    elif menu == "logis":
        judul = "Hasil Analisis Kerangka Logis"
    else:
        judul = "Kesalahan Memilih Menu"

    return judul


def cek_proyek(menu):

    if menu == "batam":
        judul = "BP Batam"
    elif menu == "sabang":
        judul = "BPK Sabang"

    return judul

############################


"""

    Longlist

"""

# Retrieve Long List Data


class LonglistDataView(AjaxDatatableView):
    model = Longlist
    title = 'Longlist'
    initial_order = [["judul_proyek", "asc"], ]
    length_menu = [[10, 50, 100, -1], [10, 50, 100, 'all']]
    search_values_separator = ' '

    column_defs = [
        {'name': 'pk', 'visible': False, 'title': 'No'},
        {'name': 'judul_proyek', 'visible': True, 'title': 'Judul Proyek'},
        {'name': 'provinsi', 'title': 'Provinsi', 'foreign_field': 'provinsi__nama_provinsi',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'isu_strategis', 'visible': True, 'title': 'Isu Strategis'},
        {'name': 'kl_pelaksana', 'foreign_field': 'kl_pelaksana__nama', 'title': 'Kementrian Lembaga',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'sumber_data', 'foreign_field': 'sumber_data__nama_sumber', 'title': 'Sumber Data',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'status_usulan', 'foreign_field': 'status_usulan__nama_status', 'visible': True,
            'choices': True, 'autofilter': True},
        {'name': 'taging_kawasan_prioritas', 'title': 'Taging Kawasan', 'foreign_field': 'taging_kawasan_prioritas__kawasan_prioritas',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'output_test', 'title': 'Output LFA', 'foreign_field': 'output_test__nama_output',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'edit', 'title': 'Action', 'placeholder': True,
         'searchable': False, 'orderable': False, },
        {'name': 'lokasi_proyek', 'visible': False},
        {'name': 'target_2021', 'visible': False},
        {'name': 'target_2022', 'visible': False},
        {'name': 'target_2023', 'visible': False},
        {'name': 'target_2024', 'visible': False},
        {'name': 'target_2025', 'visible': False},
        {'name': 'indikasi_pendanaan_2021', 'visible': False},
        {'name': 'indikasi_pendanaan_2022', 'visible': False},
        {'name': 'indikasi_pendanaan_2023', 'visible': False},
        {'name': 'indikasi_pendanaan_2024', 'visible': False},
        {'name': 'keterangan', 'visible': False},
    ]

    def customize_row(self, row, obj):
        row['edit'] = """
            <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full" 
            onclick=" 
            var id = this.closest('tr').id.substr(4); location.replace('/forms/longlist/update/'+id);">
               Edit
            </button>
        """


# Retrieve Endorsement List Data

class EndorsementDataView(AjaxDatatableView):

    model = Longlist
    title = 'Endorsement'

    initial_order = [["judul_proyek", "asc"], ]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = ' '

    column_defs = [
        {'name': 'pk', 'visible': False, 'title': 'No'},
        {'name': 'judul_proyek', 'visible': True, 'title': 'Judul Proyek'},
        {'name': 'provinsi', 'title': 'Provinsi', 'foreign_field': 'provinsi__nama_provinsi',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'isu_strategis', 'visible': True, 'title': 'Isu Strategis'},
        {'name': 'kl_pelaksana', 'foreign_field': 'kl_pelaksana__nama', 'title': 'Kementrian Lembaga',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'sumber_data', 'foreign_field': 'sumber_data__nama_sumber', 'title': 'Sumber Data',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'status_usulan', 'foreign_field': 'status_usulan__nama_status', 'visible': True,
            'choices': True, 'autofilter': True},
        {'name': 'taging_kawasan_prioritas', 'title': 'Taging Kawasan', 'foreign_field': 'taging_kawasan_prioritas__kawasan_prioritas',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'edit', 'title': 'Action', 'placeholder': True,
         'searchable': False, 'orderable': False, }
    ]

    def get_initial_queryset(self, request=None):
        queryset = self.model.objects.filter(endorsement=True)
        return queryset

    def customize_row(self, row, obj):
        row['edit'] = """
            <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full" 
            onclick=" 
            var id = this.closest('tr').id.substr(4); location.replace('/forms/longlist/update/'+id);">
               Edit
            </button>
        """

# Retrieve Hasil Skoring


class HasilSkoringDataView(AjaxDatatableView):

    model = SkoringProyek
    title = 'Hasil Skoring Proyek'

    initial_order = [["proyek", "asc"], ]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = ' '

    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, 'title': 'No'},
        {'name': 'proyek', 'visible': True, 'title': 'Judul Proyek',
            'foreign_field': 'proyek__judul_proyek'},
        {'name': 'nilai_raw_korelasi_sasaran',
            'title': 'Pengaruh Sasaran', 'visible': True},
        {'name': 'nilai_raw_korelasi_output',
            'title': 'Pengaruh Output', 'visible': True},
        {'name': 'nilai_raw_MP',
            'title': 'Nilai MP', 'visible': True},
        {'name': 'nilai_raw_investasi',
         'title': 'Nilai Investasi', 'visible': True},
        {'name': 'total_skoring', 'title': 'Hasil Skoring', 'visible': True},
        {'name': 'edit', 'title': 'Action', 'placeholder': True,
         'searchable': False, 'orderable': False}

    ]

    def get_initial_queryset(self, request=None):
        queryset = self.model.objects.filter(proyek__shortlist=True)
        return queryset

    def customize_row(self, row, obj):
        row['edit'] = """
            <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full" 
            onClick="
            var id = this.closest('tr').id.substr(4); 
            location.replace('/forms/skoring/update/'+id);">
            Edit
            </button>
        """


# Retrieve Kesepakatan Forum List Data


class KesepakatanForumDataView(AjaxDatatableView):

    model = Longlist
    title = 'Catatan Kesepakatan Forum Perencanaan'

    initial_order = [["judul_proyek", "asc"], ]
    length_menu = [[20, 50, 100, -1], [20, 50, 100, 'all']]
    search_values_separator = ' '

    column_defs = [
        {'name': 'pk', 'visible': False, 'title': 'No'},
        {'name': 'judul_proyek', 'visible': True, 'title': 'Judul Proyek'},
        {'name': 'provinsi', 'title': 'Provinsi', 'foreign_field': 'provinsi__nama_provinsi',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'isu_strategis', 'visible': True, 'title': 'Isu Strategis'},
        {'name': 'kl_pelaksana', 'foreign_field': 'kl_pelaksana__nama', 'title': 'Kementrian Lembaga',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'sumber_data', 'foreign_field': 'sumber_data__nama_sumber', 'title': 'Sumber Data',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'status_usulan', 'foreign_field': 'status_usulan__nama_status', 'visible': True,
            'choices': True, 'autofilter': True},
        {'name': 'taging_kawasan_prioritas', 'title': 'Taging Kawasan', 'foreign_field': 'taging_kawasan_prioritas__kawasan_prioritas',
            'visible': True, 'choices': True, 'autofilter': True},
        {'name': 'edit', 'title': 'Action', 'placeholder': True,
         'searchable': False, 'orderable': False, }
    ]

    def get_initial_queryset(self, request=None):
        queryset = self.model.objects.filter(
            shortlist=True, prarakorgub=True, rakorgub=True, rakortekbang=True, musrenbangprov=True, musrenbangnas=True)
        return queryset

    def customize_row(self, row, obj):
        row['edit'] = """
            <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full" 
            onclick=" 
            var id = this.closest('tr').id.substr(4); location.replace('/forms/longlist/update/'+id);">
               Edit
            </button>
        """

# Retrieve Kawasan Prioritas List Data


class KawasanPrioritasDataView(AjaxDatatableView):

    model = DataKawasanPrioritas
    title = 'Skoring Kawasan Prioritas'

    initial_order = [["id", "asc"], ]
    length_menu = [[20, 50, 100, -1], [20, 50, 100, 'all']]
    search_values_separator = ' '

    column_defs = [
        {'name': 'id', 'visible': True, 'title': 'No'},
        {'name': 'nama_kawasan_prioritas',
            'visible': True, 'title': 'Kawasan Prioritas'},
        {'name': 'perencanaan', 'visible': True, 'title': 'Perencanaan'},
        {'name': 'kesiapan_kawasan', 'visible': True, 'title': 'Kesiapan Kawasan'},
        {'name': 'potensi_konektivitas', 'visible': True,
            'title': 'Potensi Konektivitas'},
        {'name': 'dampak_ekonomi', 'visible': True, 'title': 'Dampak Ekonomi'},
        {'name': 'dampak_lingkungan', 'visible': True, 'title': 'Dampak Lingkungan'},
        {'name': 'risiko_bencana', 'visible': True, 'title': 'Risiko Bencana'},
        {'name': 'total_nilai', 'visible': True, 'title': 'Total Nilai'},
        {'name': 'dampak_ekonomi_revisi', 'visible': True,
            'title': 'Dampak Ekonomi Revisi'},
        {'name': 'kawasan_prioritas', 'visible': True, 'title': 'Kawasan Prioritas'},
    ]

# Create Single Long List Data


@login_required(login_url='login')
def addSingleLonglist(request):
    form = LonglistForm()
    content = {'judul': "Anda Sedang Menambah Data Longlist"}

    if request.method == 'POST':
        form = LonglistForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/kebdaerah/longlist')

    content["form"] = form

    return render(request, 'forms/longlist.html', content)

# Update Single Long List Data


@login_required(login_url='login')
def updateLonglist(request, pk):

    longlist = Longlist.objects.get(id=pk)
    form = LonglistForm(instance=longlist)
    content = {'form': form,
               'judul': "Anda Sedang Memperbaharui Data Longlist", 'pk': pk}

    if request.method == 'POST':
        form = LonglistForm(request.POST, instance=longlist)
        if form.is_valid():
            form.save()
            messages.success(request, 'Berhasil Mengubah Longlist')
            return HttpResponseRedirect('/kebdaerah/longlist')
        else:
            messages.error(request, 'Gagal Mengubah Longlist')
            return render(request, 'forms/longlist.html', content)

    return render(request, 'forms/longlist.html', content)

# Delete Single Long List Data


@login_required(login_url='login')
def deleteSingleLonglist(request, pk):

    longlist = Longlist.objects.get(id=pk)

    longlist.delete()
    return redirect('/kebdaerah/longlist')

# Download Long List Data CSV Format

# Update Hasil Skoring


@login_required(login_url='login')
def updateHasilSkoring(request, pk):
    proyek = SkoringProyek.objects.get(id=pk)
    form = SkoringProyekForm(instance=proyek)

    content = {'form': form,
               'judul': "Anda Sedang Memperbaharui Hasil Skoring Proyek", 'pk': pk,
               'proyek': proyek
               }

    if request.method == 'POST':
        form = SkoringProyekForm(request.POST, instance=proyek)
        if form.is_valid():
            form.save()
            return redirect('/kebdaerah/prioritas')

    return render(request, 'forms/dpp-update.html', content)

# Create Isu Strategis

@login_required(login_url='login')
def addIsuStrategis(request):

    form = IsuStrategisForm()

    if request.method == 'POST':
        form = IsuStrategisForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Berhasil Menambahkan Isu Strategis Baru!')
            return HttpResponseRedirect('/forms/isu_strategis/add')
        else:
            messages.error(request, 'Gagal Menambahkan Isu Strategis')
            return HttpResponseRedirect('/forms/isu_strategis/add')

    return render(request, 'forms/isu-strategis.html', {'content': {
        'form': form
    }})

# CRUD Hasil Kerangka Logis

@login_required(login_url='login')
def deleteanalisakerangkalogis(request, tipe):
    tujuan_id = int(request.GET.get("tujuan_id", 0))
    sasaran_id = int(request.GET.get("sasaran_id", 0))
    output_id = int(request.GET.get("output_id", 0))
    pilih_provinsi = int(request.GET.get("provinsi_id", 0))
    pilih_tahun = int(request.GET.get("tahun", 0))
    tujuan_instance = TujuanLFA.objects.get(pk=tujuan_id) if tujuan_id != 0 else None
    sasaran_instance = SasaranLFA.objects.get(pk=sasaran_id) if sasaran_id != 0 else None
    output_instance = OutputLFA.objects.get(pk=output_id) if output_id != 0 else None

    # Delete tujuan LFA
    if tipe == 'tujuan':
        tujuan_instance.delete()
        messages.success(request, 'Berhasil Menghapus Tujuan LFA') 
    
    # Delete sasaran LFA
    if tipe == 'sasaran':
        sasaran_instance.delete()
        messages.success(request, 'Berhasil Menghapus Sasaran LFA') 

    # Delete output LFA
    if tipe == 'output':
        output_instance.delete()
        messages.success(request, 'Berhasil Menghapus output LFA') 

    return HttpResponseRedirect(f'/profil/akl/?options={pilih_provinsi}-{pilih_tahun}')

@login_required(login_url='login')
def analisakerangkalogis(request, tipe):
    content_title = ""
    form = None
    provinsi = []
    page_mode = request.path.split("/")[2]
    tujuan_id = int(request.GET.get("tujuan_id", 0))
    sasaran_id = int(request.GET.get("sasaran_id", 0))
    output_id = int(request.GET.get("output_id", 0))
    tujuan_instance = TujuanLFA.objects.get(pk=tujuan_id) if tujuan_id != 0 else None
    sasaran_instance = SasaranLFA.objects.get(pk=sasaran_id) if sasaran_id != 0 else None
    output_instance = OutputLFA.objects.get(pk=output_id) if output_id != 0 else None

    if tipe == 'tujuan':
        content_title = "tujuan"
        form = Tujuan_LFA_Form() if request.path.split("/")[1] == "add_lfa" else Tujuan_LFA_Form(instance=tujuan_instance)
        # Create and Edit tujuan LFA
        if request.method == 'POST':
            form = Tujuan_LFA_Form(request.POST or None, instance=tujuan_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Berhasil Menambahkan/Mengubah Tujuan LFA') 
            else:
                messages.error(request, 'Gagal Menambahkan/Mengubah Tujuan LFA') 

            return HttpResponseRedirect('/forms/add_lfa/sasaran') if (page_mode == "add_lfa") else HttpResponseRedirect(f'/profil/akl/?options={tujuan_instance.provinsi_id}-0')

    elif tipe == 'sasaran':
        content_title = "sasaran"
        form = Sasaran_LFA_Form() if request.path.split("/")[1] == "add_lfa" else Sasaran_LFA_Form(instance=sasaran_instance)
        provinsi = ProvinsiId.objects.all()
        # Create and Edit sasaran LFA
        if request.method == 'POST':
            form = Sasaran_LFA_Form(request.POST or None, instance=sasaran_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Berhasil Menambahkan/Mengubah Sasaran LFA')
            else:
                messages.error(request, 'Gagal Menambahkan/Mengubah Sasaran LFA')

            return HttpResponseRedirect('/forms/add_lfa/output') if (page_mode == "add_lfa") else HttpResponseRedirect(f'/profil/akl/?options={sasaran_instance.tujuan.provinsi_id}-0')

    elif tipe == 'output':
        content_title = "output"
        form = Output_LFA_Form() if request.path.split("/")[1] == "add_lfa" else Output_LFA_Form(instance=output_instance)
        provinsi = ProvinsiId.objects.all()
        # Create and Edit output LFA
        if request.method == 'POST':
            form = Output_LFA_Form(request.POST or None, instance=output_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Berhasil Menambahkan/Mengubah Output LFA')
            else:
                messages.error(request, 'Gagal Menambahkan/Mengubah Output LFA')

            return HttpResponseRedirect('/forms/add_lfa/tujuan') if (page_mode == "add_lfa") else HttpResponseRedirect(f'/profil/akl/?options={output_instance.sasaran.tujuan.provinsi_id}-0')
    else:
        content_title = None

    return render(request, 'forms/kerangkalogis-add.html', {'content': {
        'page_url': page_mode,
        'content_title': content_title,
        'form': form,
        'provinsi': provinsi
    }})


def download_longlist_format(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'Longlist Format Database.xlsx'
    # Define the full file path
    filepath = BASE_DIR + '/Format_Database/' + filename
    # Open the file for reading content
    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value
    return response

# Chart Kementrian Lembaga Pelaksana


def chart_ro(request):

    labels = []
    data = []
    ro_by_kl = Longlist.objects.values(
        'kl_pelaksana__singkatan').annotate(jumlah=Count('judul_proyek'))

    for row in ro_by_kl:
        labels.append(row['kl_pelaksana__singkatan'])
        data.append(row['jumlah'])

    data = {
        'labels': labels,
        'data': data
    }

    return JsonResponse(data)

# Chart Status Usulan


def chart_prov(request):

    labels = []
    data = []
    ro_by_prov = Longlist.objects.values(
        'status_usulan__nama_status').annotate(jumlah=Count('judul_proyek'))

    for row in ro_by_prov:
        labels.append(row["status_usulan__nama_status"])
        data.append(row['jumlah'])

    data = {
        'labels': labels,
        'data': data
    }

    return JsonResponse(data)


# API Kondisi Umum Wilayah


def api_kuw(request):

    labels = []
    data = []
    ro_by_kl = Longlist.objects.values(
        'kl_pelaksana__singkatan').annotate(jumlah=Count('judul_proyek'))

    for row in ro_by_kl:
        labels.append(row['kl_pelaksana__singkatan'])
        data.append(row['jumlah'])

    data = {
        'labels': labels,
        'data': data
    }

    return JsonResponse(data)


# Data API Tujuan LFA


def AjaxTujuanLFA(request):
    provinsi_id = request.GET.get('provinsi_id')
    tujuan = list(TujuanLFA.objects.filter(provinsi_id=provinsi_id).values())
    return JsonResponse({"data": tujuan, "message": "Success"})


# Data API Sasaran LFA


def AjaxSasaranLFA(request):
    tujuan_id = request.GET.get('tujuan_id')
    sasaran = list(SasaranLFA.objects.filter(tujuan_id=tujuan_id).values())
    return JsonResponse({"data": sasaran, "message": "Success"})


# Data API Output LFA


def AjaxOutputLFA(request):
    return JsonResponse("test_data_output_lfa")


############################
