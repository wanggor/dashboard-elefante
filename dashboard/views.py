from django.shortcuts import render
from django.http import HttpResponse

from dashboard.utils import *

import json
import pandas as pd

def home(request):
    context = {}
    return render(request,"index.html",context)

def notulensi(request):
    context = {}
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

def saldo_awal(request):
    context = {}
    data = pd.DataFrame(list(SaldoAwal.objects.all().values()))
    if list(data) != []:
        context = extract_data(data)
    else:
        context["header"] = [{"title" : "No"}] + [{"title" : f.name.replace("_", " ").capitalize() } for f in SaldoAwal._meta.get_fields()][1:-2]
        context["value"] = [[" " for i in range(len(context["header"]))]]
    return render(request,"saldo_awal.html",context)

def daftar_plan(request):
    context = {}
    data = pd.DataFrame(list(Plant.objects.all().values()))
    if list(data) != []:
        context = extract_data(data)
    return render(request,"daftar_plan.html",context)

def daftar_material(request):
    context = {}
    data = pd.DataFrame(list(Material.objects.all().values()))
    if list(data) != []:
        context = extract_data(data)

    return render(request,"daftar_material.html",context)

def daftar_mvt(request):
    context = {}
    data = pd.DataFrame(list(MovementType.objects.all().values()))
    if list(data) != []:
        context = extract_data(data)
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