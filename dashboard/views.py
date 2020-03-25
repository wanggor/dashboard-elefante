from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum
from django.db.models import Q

from dashboard.utils import *

import json
import pandas as pd
import random
import numpy as np
from datetime import datetime
import calendar

def home(request):
    context = {}
    data = pd.DataFrame(list(Data_pemakain.objects.all().values()))
    if data.empty:
        context["tahun"] = []
        context["material"] = []
        context["plant"] = []
        context["Data"] = []
    
    else:
        context["tahun"] = sorted(data["tahun"].unique())
        context["material"] = sorted(data["material"].unique())
        context["plant"] = sorted(data["plant"].unique())

        data_line = []
        abbr_to_num = {num: name for num, name in enumerate(calendar.month_abbr) if num}
        for bln in range(12):
            data_line.append(
                    {
                        "date": f"{abbr_to_num[bln+1]}",
                        "x" : bln+1,
                        "date-time": str(datetime(2019, bln+1, 1, 0, 0))
                    }
                )
            average = 0
            n_f = 0
            for th in Data_pemakain.objects.values('tahun').distinct():
                b = bln+1
                nilai = Data_pemakain.objects.filter(tahun = th["tahun"]).filter(bulan = b).aggregate(Sum('value'))
                if nilai["value__sum"] is not None:
                    data_line[-1][str(int(float(th["tahun"])))] = - nilai["value__sum"]
                    average +=  -nilai["value__sum"]
                    n_f += 1
            if n_f != 0:
                average = average/n_f
                data_line[-1]["Rata-rata"] = average
        context["Data"] = data_line
    return render(request,"index.html",context)

def notulensi(request):
    # reset(2019)
    context = {}

    waktu_unique = []
    waktu = list(Notulensi.objects.values( "tahun","bulan").distinct())
    if list(waktu) != []:
        for i in waktu:
            if [float(i["tahun"]), int2month(i["bulan"])] not in waktu_unique:
                waktu_unique.append(int2month(i["bulan"]) +" - "+str(i["tahun"]))
    context["waktu"] = waktu_unique
    return render(request,"notulensi.html",context)

def report(request, pk):
    data = {}
    data["data"] = get_data_report(pk)
    data["tahun"] = pk
    return render(request,"report.html",data)

def upload(request):
    context = {}
    return render(request,"upload.html",context)

def validasi(request):
    context = {}
    context["data"] = get_vatidate_data()
    return render(request,"validasi.html",context)

def daftar_harga(request):
    context = {}
    data = pd.DataFrame(list(Harga.objects.all().values()))
    if list(data) != []:
        context = extract_data(data, "harga")
    else:
        context["header"] = [{"title" : "No"}] + [{"title" : f.name.replace("_", " ").capitalize() } for f in SaldoAwal._meta.get_fields()][1:-2]
        context["value"] = [[" " for i in range(len(context["header"]))]]
    return render(request,"daftar_harga.html",context)

def saldo_awal(request):
    context = {}
    data = pd.DataFrame(list(SaldoAwal.objects.all().values()))
    if list(data) != []:
        context = extract_data(data, "saldo_awal")
    else:
        context["header"] = [{"title" : "No"}] + [{"title" : f.name.replace("_", " ").capitalize() } for f in SaldoAwal._meta.get_fields()][1:-2]
        context["value"] = [[" " for i in range(len(context["header"]))]]
    return render(request,"saldo_awal.html",context)

def daftar_plan(request):
    context = {}
    data = pd.DataFrame(list(Plant.objects.all().values()))
    if list(data) != []:
        context = extract_data(data, "plan")
    return render(request,"daftar_plan.html",context)

def daftar_material(request):
    context = {}
    data = pd.DataFrame(list(Material.objects.all().values()))
    if list(data) != []:
        context = extract_data(data, "material")

    return render(request,"daftar_material.html",context)

def daftar_mvt(request):
    context = {}
    data = pd.DataFrame(list(MovementType.objects.all().values()))
    if list(data) != []:
        context = extract_data(data, "mvt")
    return render(request,"daftar_mvt.html",context)
    

def delete_data(request):
    if request.method == 'POST':
        data = request.POST["data"]
        delete_data_from_post(data)
        return HttpResponse("Sucsess") 
    else:
        context = {}
        context["data"] = get_available_data(request)
        return render(request,"delete_data.html",context)

def login(request):
    context = {}
    return render(request,"login.html",context)

def reset_password(request):
    context = {}
    return render(request,"reset_password.html",context)


def get_data_position(request):
    t = random.random()
    data = get_home_data()
    return HttpResponse(json.dumps(data, default=default))

#GET
def getTableData(request):
    if request.method == 'POST':
        data = dict(request.POST)
        if "start" in data.keys() and "end" in data.keys():
            start = [int(float(i)) for i  in  data["start"][0].split("/")]
            end = [int(float(i)) for i  in  data["end"][0].split("/")]
            start = datetime(year=start[2], month=start[1], day=start[0])
            end = datetime(year=end[2], month=end[1], day=end[0])

            data = data_tanggal.objects.filter(posting_date__range=(start, end)).filter(valid = True).values("posting_date", "kategori", "material", "plant","receiving_plant", "description","value")
            data = {"data" : [[i["posting_date"].strftime("%d/%m/%Y"), i["kategori"], i["material"], i["plant"], i['receiving_plant'], i["description"], i['value']] for i in data]}

            return HttpResponse(json.dumps(data,default=default))

def getNotulensi(request):
    if request.method == 'POST':
        abbr_to_num = {name :num  for num, name in enumerate(calendar.month_abbr) if num}
        num2mont = {num :name  for num, name in enumerate(calendar.month_abbr) if num}
        data = dict(request.POST)["data"][0].split(" - ")
        bulan = abbr_to_num[data[0]]
        tahun = int(float(data[1]))
        
        data_bulan = sorted([i["bulan"] for i in list(Notulensi.objects.filter(tahun = tahun).values("bulan"))])
        ind = data_bulan.index(bulan)
        if ind == 0:
            bulan_lalu = "-"
        elif ind > 0:
            bulan_lalu = num2mont[data_bulan[ind-1]]
        data = {}
        data["bulan"] = dict(request.POST)["data"][0].split(" - ")[0]
        data["bulan_lalu"] = bulan_lalu
        data["tahun"] = tahun
        data["tanggal"] = calendar.monthrange(tahun, bulan)[1]

       
        data["data"] = list(Notulensi.objects.filter(tahun = tahun).filter(bulan = bulan).values())[0]
        
        return HttpResponse(json.dumps(data,default=default))

def updateNotulensi(request):
    if request.method == 'POST':
        abbr_to_num = {name :num  for num, name in enumerate(calendar.month_abbr) if num}
        data = dict(request.POST)

        tanggal = data["bulan"][0].split(" ")
        bulan = abbr_to_num[tanggal[0]]
        tahun = int(float(tanggal[1]))

        Notulensi.objects.filter(tahun = tahun).filter(bulan = bulan).update(
            nomor = data["nomor-surat"][0],
            hari_tanggal = data["hari-tanggal-rapat"][0],
            ruang = data["ruang-rapat"][0],
            pukul = data["Pukul-rapat"][0],
            hal = data["perihal-rapat"][0],
            info = data["additional-info"][0],
            pimpinan_rapat = data["nama-pimpinan-rapat"][0],
            notulis = data["notulis"][0],
            jabatan = data["penanggung-jawab-rapat"][0],
            nama_pimpinan = data["nama-penanggung-jawab-rapat"][0],
            total = data["total"][0],
            perihal = data["container-perihal-rapat"][0],
            perhatian = data["table-perhatian-id"][0],
            rekons = data["table-rekons-id"][0],
            catatan = data["table-catatan-id"][0],
            hal_disampaikan = data["container-summary-rapat"][0],
            bertanda_bintang = data["bertanda-bintang-table"][0],
            distribusi =  data["distribusi"][0]
            
        )
        data = {}
        data["data"] = {}
        return HttpResponse(json.dumps(data,default=default))


# POST
def home_data(request):
    if request.method == 'POST':
        data = get_home_data()
        return HttpResponse(json.dumps(data, default=default))
    else:
        return HttpResponse("Sucsess")

def delete_val_data_all(request):
    if request.method == 'POST':
        delete_data_validate_all()
    return HttpResponse("Sucsess")


def validate_data(request):
    if request.method == 'POST':
        data = request.POST["data"]
        validate(data)
    return HttpResponse("Sucsess")

def delete_val_data(request):
    if request.method == 'POST':
        data = request.POST["data"]
        delete_data_validate(data)
    return HttpResponse("Sucsess")


def upload_saldo(request):
    if request.method == 'POST':
        data = pd.read_excel (request.FILES['file[0]'],skipinitialspace=True)
        update_saldo(data, request)
    return HttpResponse("Sucsess")

def upload_plan(request):
    if request.method == 'POST':
        data = pd.read_excel (request.FILES['file[0]'],skipinitialspace=True)
        update_plan(data, request)
    return HttpResponse("Sucsess")

def upload_material(request):
    if request.method == 'POST':
        data = pd.read_excel (request.FILES['file[0]'],skipinitialspace=True)
        update_material(data, request)
    return HttpResponse("Sucsess")

def upload_mvt(request):
    if request.method == 'POST':
        data = pd.read_excel (request.FILES['file[0]'],skipinitialspace=True)
        update_mvt(data, request)
    return HttpResponse("Sucsess")

def upload_harga(request):
    if request.method == 'POST':
        data = pd.read_excel (request.FILES['file[0]'],skipinitialspace=True)
        update_harga(data, request)
    return HttpResponse("Sucsess")

def upload_files(request):
    if request.method == 'POST':
        data = {}
        pandas_file = {}
        for key in request.FILES:
            value = request.FILES[key]
            name = str(value.name).split(' ')[0:-1]
            name = [i.lower() for i in name]
            if 'outstanding' in [i.lower() for i in name]:
                name = 'outstanding'
                pandas_file[name] = pd.ExcelFile(request.FILES[key])
            else:
                if "order" in name:
                    name = "export order"
                else:
                    name = name[0]
                pandas_file[name] = pd.read_excel (request.FILES[key],skipinitialspace=True)
                pandas_file[name].columns = pandas_file[name].columns.str.strip().str.title()
        
        data = process_data_excell(pandas_file, request)
        
        return HttpResponse(json.dumps(data, default=default))

def check_upload_laporan(request):
    if request.method == 'POST':
        user = request.user
        data = request.POST["data"]
        if data == "Excecute":
            delete_unconfirm_data(request)
        else:
            cancel_data_upload(request)
        return HttpResponse("Sucsess")

#TracnTrace

def tracking(request):
    # DataSensor.objects.all().delete()
    data = {}
    data["data"] = get_unit_data()
    data["histori"] = get_unit_data_history()
    data["histori"] = {}
    data["route"] = {}

    with open("data/route_1.geojson") as f:
        data["route"][0] = json.load(f)
    
    with open("data/route_2.geojson") as f:
        data["route"][1] = json.load(f)

    with open("data/route_3.geojson") as f:
        data["route"][2] = json.load(f)
    
    data["route_appearence"] = {}
    col_pick = MplColorHelper("Paired", 0, 3)
    for i in range(3):
        data["route_appearence"][i] = {
            "color" : col_pick.get_hex(i),
            "transparan" : 0.8,
            "line-width" : 5
        }
    # data["route-appearence"][0] = {"color" : ""}
    return render(request,"tracking.html",data)

def get_data(request):
    data = {}
    data["data"] = get_unit_data()
    data["unit"] = list(Unit.objects.all().values("name","current_latitude", "current_longitude","current_directions"))
    return HttpResponse(json.dumps(data, default=default))

def get_current_data(request):
    unit = list(Unit.objects.all().values("id","current_latitude", "current_longitude","current_directions"))
    data = {}
    data["data"] = unit
    return HttpResponse(json.dumps(data, default=default))


def upload(request):
    if request.method == 'POST':
        time_save = 1
        data = json.loads(request.POST["data"])
        user_name = data["id"]
        name = data["name"]
        lat = float(data["latitude"])
        lon = float(data["longitude"])
        alt = float(data["altitude"])
        acc = float(data["gps_accuracy"])
        t   = datetime.datetime.fromtimestamp(int(data["tst"]))
        
        user = [i["id_user"] for i in list(Unit.objects.values("id_user"))]
        if user_name not in user:
            Unit.objects.create(
                id_user             = user_name,
                name                = name,
                kontak              = "None",
                current_latitude    = lat,
                current_longitude   = lon,
                accuracy = acc,
                current_directions  = 0,
                time_step       = 0,
                last_accumulate     = t,
                current_speed = 0
            )
        
        poss_before = list(Unit.objects.filter(id_user = user_name).values("current_latitude", "current_longitude", "last_accumulate","time_step"))[0]
        lat_before  = float(poss_before["current_latitude"])
        long_before = float(poss_before["current_longitude"])
        t_0         = (t - (poss_before["last_accumulate"])).total_seconds()

        
        if t_0 != 0:
            length = getPathLength(lat_before,long_before,lat, lon)
            direc  = (180 + calculateBearing(lat_before,long_before,lat, lon)) % 360
            speed  = length/t_0

            if speed != 0:
                time_step = poss_before["time_step"] + t_0
            else:
                time_step = poss_before["time_step"]

            Unit.objects.filter(id_user = user_name).update(
                current_latitude    = lat,
                current_longitude   = lon,
                accuracy            = acc,
                current_directions  = direc,
                time_step           = time_step,
                last_accumulate     = t,
                current_speed       = speed
            )

            unit_instace = Unit.objects.get(id_user = user_name)
            time_sensor = sorted([i["time"] for i in list(DataSensor.objects.filter(unit = unit_instace).values("time"))])
            # if time_sensor != [] :
            #     if float((t-time_sensor[-1]).total_seconds()) > time_save:
            #         poss_before_sensor = list(DataSensor.objects.filter(unit = unit_instace).filter(time = time_sensor[-1]).values("latitude", "longitude"))[0]
            #         lat_before_sensor  = float(poss_before_sensor["latitude"])
            #         long_before_sensor = float(poss_before_sensor["longitude"])

            #         length_sensor = getPathLength(lat_before_sensor,long_before_sensor,lat, lon)

            #         DataSensor.objects.create(
            #             latitude        = lat,
            #             longitude       = lon,
            #             directions      = direc,
            #             speed           = speed,
            #             distance        = length_sensor,
            #             time            = t,
            #             time_step       = time_step,
            #             unit            = unit_instace,
            #             accuracy        = acc
            #         )

            #         Unit.objects.filter(id_user = user_name).update(time_step = 0)
            #     else:
            #         pass
            # else:
                # DataSensor.objects.create(
                #     latitude        = lat,
                #     longitude       = lon,
                #     directions      = direc,
                #     speed           = speed,
                #     distance        = length,
                #     time            = t,
                #     time_step       = time_step,
                #     unit            = unit_instace,
                #     accuracy = 0
                # )
                # Unit.objects.filter(id_user = user_name).update(time_step = 0)
        return HttpResponse("Sucsess")


def visualisai(request):
    data = {}
    data["data"] = {}
    return render(request,"visualisasi.html",data)
