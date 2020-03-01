import numpy as np
from .models import *
import itertools
import pandas as pd
import datetime
import calendar
from io import StringIO
import json

def parsing(data_list, key=None, val = None, mode = ""):
    data = {}
    for item in data_list:
        k =  item[key]
        v = item[val]
        if mode != "normal":
            if k not in  data.keys():
                data[k] = []
            data[k].append(v)
        else:
            data[k] = v
    return data

def int2month(val):
    abbr_to_num = {name:num for num, name in enumerate(calendar.month_abbr) if num}
    num_to_abbr = { num: name for num, name in enumerate(calendar.month_abbr) if num}
    return num_to_abbr[val]

def change_text1(a):
    if a["Purchase Order"] != "" and a["Unloading Point"] != "":
        return a["Unloading Point"] + " | "+ "PO: " + str(int(float(a["Purchase Order"])))
    else:
        return str(int(float(a["Purchase Order"])))

def change_text(a):
    if a["Kategori"] == "Kedatangan":
        if a["Receiving Plant"] != "":
            if a["Description"] == "":
                return "ZZ.Lainnya" + " | "  +a["Plant"] + " -> " + a["Receiving Plant"] 
            else:
                return  a["Description"] + " | " +  a["Plant"] + " -> " + a["Receiving Plant"] 
        else:
            return a["Description"]
    elif a["Kategori"] == "Saldo Awal" and a["Description"] == "":
        return "Produksi Sendiri"
    else:
        return a["Description"]

def date_change(a):
    text = str(a["To Date"])
    return text.replace(".", "/")

def default(obj):
    if type(obj).__module__ == np.__name__:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj.item()
    raise TypeError('Unknown type:', type(obj))

def get_class_desc(a):
    name = a["Description"].split(" | ")
    kategori = " | ".join(name[:-1])
    return kategori

def get_class_desc2(a):
    name = a["Description"].split(" | ")
    return name[-1]

def process_data_excell(pandas_file, request):
    pandas_file['export']['Posting Date'] = pandas_file['export']['Posting Date'].dropna().astype(str)
    list_month = list(pd.DatetimeIndex(pandas_file['export']['Posting Date'].dropna()).month.unique())
    year = list(pd.DatetimeIndex(pandas_file['export']['Posting Date'].dropna()).year.unique())[0]


    #Get Plant List from data base
    plant_list = pd.DataFrame(list(Plant.objects.all().values()))
    plant_list = plant_list.rename(columns = {"id":'ID','nama': 'Nama Plant', "kode":'Kode Plant', "departement":'Nama Departemen','perusahaan':'Perusahaan', 'kode pos':'Kode Pos', "lokasi":'Lokasi'})
    plant_convert = plant_list[["Kode Plant", "Nama Plant"]].set_index("Kode Plant").to_dict()["Nama Plant"]
    plant_dept = plant_list[["Nama Plant", "Nama Departemen"]].set_index("Nama Plant").to_dict()["Nama Departemen"]


    #Get Material list from database
    materail_list = pd.DataFrame(list(Material.objects.all().values()))
    material_list2 = materail_list[['kategori',"nama_kelompok",'kode']].set_index('kode').to_dict()['nama_kelompok']
    material_list1 = materail_list[['kategori',"nama_kelompok",'kode']].set_index('nama_kelompok').to_dict()['kode']

    #Get Movement type List from database
    movementTypeList = parsing(list(MovementType.objects.all().values()), key="deskripsi", val='kode')

    #rename plane code into its name
    pandas_file['export']['Receiving Plant'] = pandas_file['export']['Receiving Plant'].map(plant_convert)

    #Get order List 
    # print(pandas_file['export order'].columns)
    order_information = pandas_file['export order'][["Order","Material Description"]]
    order_information.columns = ['Order', 'Nama Order']

    #Add order in export
    export_activities = pandas_file['export'].merge(order_information,on="Order")
    export_activities['Bulan'] =  pd.DatetimeIndex(export_activities['Posting Date']).month
    export_activities['Base Unit of Measure'] =  export_activities.apply(lambda x: -1*x["Quantity"], axis=1)

    # change material code into material name
    export_activities['Material'] = export_activities['Material'].map(material_list2)
    pandas_file['export']['Material'] = pandas_file['export']['Material'].map(material_list2)
    export = pandas_file['export']
    
    #Create Data Variable
    Data_Per_Tanggal = {}
    Data_Per_Bulan = {}

    # F-1. SALDO AWAL
    #Hasil Produksi
    hasil_prod_tanggal = export[export['Movement Type'].isin(movementTypeList['hasil produksi'])].fillna("").pivot_table(index=[ "Posting Date",'Material','Name 1'], values=["Quantity"], aggfunc=np.sum).reset_index()
    hasil_prod_tanggal["Description"] = ""
    hasil_prod_tanggal["Receiving Plant"] = ""
    hasil_prod_tanggal['Bulan'] =  pd.DatetimeIndex(hasil_prod_tanggal['Posting Date']).month
    hasil_prod_tanggal['Tahun'] =  pd.DatetimeIndex(hasil_prod_tanggal['Posting Date']).year
    hasil_prod_tanggal.columns = ["Posting Date","Material","Plant","Value","Description","Receiving Plant","Bulan",'Tahun']
    hasil_prod_tanggal = hasil_prod_tanggal[["Posting Date","Material","Plant","Description","Value","Receiving Plant","Bulan",'Tahun']]

    hasil_prod_bulan = hasil_prod_tanggal.pivot_table(index=['Tahun',"Bulan",'Material','Plant'], aggfunc=np.sum).reset_index()
    hasil_prod_bulan["Description"] = ""
    hasil_prod_bulan["Receiving Plant"] = ""
    hasil_prod_bulan = hasil_prod_bulan[['Tahun',"Bulan","Material","Plant","Description","Value","Receiving Plant"]]
    hasil_prod_bulan[hasil_prod_bulan["Material"]=="KCL Putih"]

    Data_Per_Tanggal["Hasil Produksi"] = hasil_prod_tanggal
    Data_Per_Bulan["Hasil Produksi"] = hasil_prod_bulan

    #Pembelian CS
    pem_cs_tanggal = export[export['Movement Type'].isin(movementTypeList['pembelian cs']) & (export['Reservation'] == 0) ].pivot_table(index=[ "Posting Date",'Material','Name 1'], values=["Quantity"], aggfunc=np.sum).reset_index()
    if pem_cs_tanggal.shape[0] ==0:
        pem_cs_tanggal["Quantity"] = ""
    pem_cs_tanggal["Description"] = "Pembelian CS"
    pem_cs_tanggal["Receiving Plant"] = ""
    pem_cs_tanggal['Bulan'] =  pd.DatetimeIndex(pem_cs_tanggal['Posting Date']).month
    pem_cs_tanggal['Tahun'] =  pd.DatetimeIndex(pem_cs_tanggal['Posting Date']).year
    pem_cs_tanggal.columns = ["Posting Date","Material","Plant","Value","Description","Receiving Plant","Bulan",'Tahun']
    pem_cs_tanggal = pem_cs_tanggal[["Posting Date","Material","Plant","Description","Value","Receiving Plant","Bulan",'Tahun']]
    pem_cs_tanggal = pem_cs_tanggal[pem_cs_tanggal["Value"] != 0]

    pem_cs_bulan = pem_cs_tanggal.pivot_table(index=['Tahun',"Bulan", 'Material','Plant'], aggfunc=np.sum).reset_index()
    if pem_cs_bulan.shape[0] ==0:
        pem_cs_bulan["Value"] = ""
    pem_cs_bulan["Description"] = "Pembelian CS"
    pem_cs_bulan["Receiving Plant"] = ""
    pem_cs_bulan = pem_cs_bulan[['Tahun',"Bulan","Material","Plant","Description","Value","Receiving Plant"]]
    pem_cs_bulan.head()

    Data_Per_Tanggal["Pembelian CS"] = pem_cs_tanggal
    Data_Per_Bulan["Pembelian CS"] = pem_cs_bulan

    #Penjualan
    Penjualan_tanggal = export[export['Movement Type'].isin(movementTypeList['penjualan']) ].pivot_table(index=[ "Posting Date",'Material','Name 1'], values=["Quantity"], aggfunc=np.sum).reset_index()
    if Penjualan_tanggal.shape[0] ==0:
        Penjualan_tanggal["Quantity"] = ""
    Penjualan_tanggal["Description"] = "-"
    Penjualan_tanggal["Receiving Plant"] = "-"
    Penjualan_tanggal['Bulan'] =  pd.DatetimeIndex(Penjualan_tanggal['Posting Date']).month
    Penjualan_tanggal["Tahun"] =  pd.DatetimeIndex(Penjualan_tanggal['Posting Date']).year
    Penjualan_tanggal.columns = ["Posting Date","Material","Plant","Value","Description","Receiving Plant","Bulan",'Tahun']
    Penjualan_tanggal = Penjualan_tanggal[["Posting Date","Material","Plant","Description","Value","Receiving Plant","Bulan",'Tahun']]

    Penjualan_bulan = Penjualan_tanggal.pivot_table(index=['Tahun',"Bulan",'Material','Plant'], aggfunc=np.sum).reset_index()
    if Penjualan_bulan.shape[0] ==0:
        Penjualan_bulan["Value"] = ""
    Penjualan_bulan["Description"] = "-"
    Penjualan_bulan["Receiving Plant"] = "-"
    Penjualan_bulan = Penjualan_bulan[['Tahun',"Bulan","Material","Plant","Description","Value","Receiving Plant"]]

    Data_Per_Tanggal["Penjualan"] = Penjualan_tanggal
    Data_Per_Bulan["Penjualan"] = Penjualan_bulan

    #Kedatangan
    #create list all PO
    po2desc = export[export['Movement Type'].isin(movementTypeList['kedatangan bahan baku']) & export["Purchase Order"].notnull()].pivot_table(index=[ 'Unloading Point','Purchase Order'], values=["Quantity"], aggfunc=np.sum).reset_index()[ ['Unloading Point','Purchase Order']]
    if po2desc.shape[0] != 0:
        po2desc["Purchase Order"]  = po2desc["Purchase Order"].astype(str)
        po2desc["Unloading Point"] = po2desc.apply(change_text1, axis=1)
        po2desc = po2desc.set_index("Purchase Order")
        po2desc = po2desc.to_dict()['Unloading Point']
        po2desc = {str(int(float(k))) : i for k, i in po2desc.items()}

    #TP to PB
    tp_tb_tanggal = export[export['Movement Type'].isin(movementTypeList['TP dari TB']) & export['Name 1'].isin(['PERGUDANGAN & PEMELIHARAAN'])].fillna("").pivot_table(index=[ "Posting Date",'Material','Name 1','Receiving Plant','Document Header Text','Storage Location'], values=["Quantity"], aggfunc=np.sum).reset_index()
    tp_tb_tanggal["Document Header Text"] = tp_tb_tanggal["Document Header Text"].astype(str)
    tp_tb_tanggal = tp_tb_tanggal[~((tp_tb_tanggal["Storage Location"] == "3B05") & (tp_tb_tanggal["Name 1"]  == "PERGUDANGAN & PEMELIHARAAN"))]
    tp_tb_tanggal = tp_tb_tanggal[tp_tb_tanggal["Document Header Text"].str.isnumeric()]
    tp_tb_tanggal = (tp_tb_tanggal.replace({"Document Header Text":po2desc}))
    tp_tb_tanggal["Description"] = tp_tb_tanggal["Document Header Text"]
    tp_tb_tanggal['Bulan'] =  pd.DatetimeIndex(tp_tb_tanggal['Posting Date']).month
    tp_tb_tanggal['Tahun'] =  pd.DatetimeIndex(tp_tb_tanggal['Posting Date']).year

    tp_tb_bulan = tp_tb_tanggal.pivot_table(index=["Tahun","Bulan",'Material','Name 1' ,'Receiving Plant','Document Header Text','Storage Location'], aggfunc=np.sum).reset_index()
    tp_tb_bulan["Description"] = tp_tb_bulan['Document Header Text']
    tp_tb_bulan = tp_tb_bulan.drop(['Document Header Text', 'Storage Location'], axis=1)
    tp_tb_bulan.columns = ["Tahun","Bulan","Material","Plant","Receiving Plant","Value","Description"]
    tp_tb_bulan = tp_tb_bulan[["Tahun","Bulan","Material","Plant","Description","Value","Receiving Plant"]]

    tp_tb_tanggal = tp_tb_tanggal.drop(['Document Header Text', 'Storage Location'], axis=1)
    tp_tb_tanggal.columns = ["Posting Date","Material","Plant","Receiving Plant","Value","Description","Bulan","Tahun"]
    tp_tb_tanggal = tp_tb_tanggal[["Posting Date","Material","Plant","Description","Value","Receiving Plant","Bulan","Tahun"]]

    Data_Per_Tanggal["TP to TB"] = tp_tb_tanggal
    Data_Per_Bulan["TP to TB"] = tp_tb_bulan

    #TP to Prod
    tp_prod_tanggal = export[export['Movement Type'].isin(movementTypeList['TP dari TB']) & (~ export['Name 1'].isin(['PERGUDANGAN & PEMELIHARAAN']))].fillna("").pivot_table(index=[ "Posting Date",'Material','Name 1','Receiving Plant','Document Header Text','Storage Location'], values=["Quantity"], aggfunc=np.sum).reset_index()
    tp_prod_tanggal["Document Header Text"] = tp_prod_tanggal["Document Header Text"].astype(str)
    tp_prod_tanggal = tp_prod_tanggal[~((tp_prod_tanggal["Storage Location"] == "3B05") & (tp_prod_tanggal["Name 1"]  == "PERGUDANGAN & PEMELIHARAAN"))]
    tp_prod_tanggal = tp_prod_tanggal[tp_prod_tanggal["Document Header Text"].str.isnumeric()]
    tp_prod_tanggal = (tp_prod_tanggal.replace({"Document Header Text":po2desc}))
    tp_prod_tanggal["Description"] = tp_prod_tanggal["Document Header Text"]
    tp_prod_tanggal['Bulan'] =  pd.DatetimeIndex(tp_prod_tanggal['Posting Date']).month
    tp_prod_tanggal['Tahun'] =  pd.DatetimeIndex(tp_prod_tanggal['Posting Date']).year

    tp_prod_bulan = tp_prod_tanggal.pivot_table(index=["Tahun","Bulan",'Material','Name 1' ,'Receiving Plant','Document Header Text','Storage Location'], aggfunc=np.sum).reset_index()
    tp_prod_bulan["Description"] = tp_prod_bulan['Document Header Text']
    tp_prod_bulan = tp_prod_bulan.drop(['Document Header Text', 'Storage Location'], axis=1)
    tp_prod_bulan.columns = ["Tahun","Bulan","Material","Plant","Receiving Plant","Value","Description"]
    tp_prod_bulan = tp_prod_bulan[["Tahun","Bulan","Material","Plant","Description","Value","Receiving Plant"]]

    tp_prod_tanggal = tp_prod_tanggal.drop(['Document Header Text', 'Storage Location'], axis=1)
    tp_prod_tanggal.columns = ["Posting Date","Material","Plant","Receiving Plant","Value","Description","Bulan","Tahun"]
    tp_prod_tanggal = tp_prod_tanggal[["Posting Date","Material","Plant","Description","Value","Receiving Plant","Bulan","Tahun"]]

    Data_Per_Tanggal["TP to Prod"] = tp_prod_tanggal
    Data_Per_Bulan["TP to Prod"] = tp_prod_bulan


    #GI POSTO
    gi_posto_tanggal = export[export['Movement Type'].isin(movementTypeList['GI-POSTO']) & export["Receiving Plant"].notnull()].pivot_table(index=[ "Posting Date",'Material','Name 1','Receiving Plant'], values=["Quantity"], aggfunc=np.sum).reset_index()
    gi_posto_tanggal["Description"] = "-"
    gi_posto_tanggal['Bulan'] =  pd.DatetimeIndex(gi_posto_tanggal['Posting Date']).month
    gi_posto_tanggal['Tuhan'] =  pd.DatetimeIndex(gi_posto_tanggal['Posting Date']).year
    gi_posto_tanggal.columns = ["Posting Date","Material","Plant","Receiving Plant","Value","Description","Bulan","Tahun"]
    gi_posto_tanggal = gi_posto_tanggal[["Posting Date","Material","Plant","Description","Value","Receiving Plant","Bulan", "Tahun"]]


    gi_posto_bulan = gi_posto_tanggal.pivot_table(index=["Tahun","Bulan",'Material','Plant' ,"Receiving Plant"], aggfunc=np.sum).reset_index()
    gi_posto_bulan = gi_posto_bulan[gi_posto_bulan["Value"] !=0]
    gi_posto_bulan["Description"] = ""
    gi_posto_bulan = gi_posto_bulan[["Tahun","Bulan","Material","Plant","Description","Value","Receiving Plant"]]
    gi_posto_bulan[gi_posto_bulan["Material"]=="ZA"]

    Data_Per_Tanggal["GI POSTO"] = gi_posto_tanggal
    Data_Per_Bulan["GI POSTO"] = gi_posto_bulan
    
    #Konsumsi Bahan Baku
    konsumsi_bahan_baku_tanggal = export_activities[export_activities['Movement Type'].isin(movementTypeList['konsumsi bahan baku'])].pivot_table(index=[ "Posting Date",'Material','Name 1', "Nama Order"], values=["Base Unit of Measure"], aggfunc=np.sum).reset_index()
    # konsumsi_bahan_baku_tanggal = export_activities[export_activities['Movement Type'].isin(movementTypeList['konsumsi bahan baku']) & (export_activities['Reservation'] != 0)].pivot_table(index=[ "Posting Date",'Material','Name 1', "Nama Order"], values=["Base Unit of Measure"], aggfunc=np.sum).reset_index()
    konsumsi_bahan_baku_tanggal.columns = ["Posting Date", "Material", "Plant", "Description" , "Value"]
    konsumsi_bahan_baku_tanggal["Description"] = konsumsi_bahan_baku_tanggal["Plant"] + " | "+ konsumsi_bahan_baku_tanggal["Description"]
    konsumsi_bahan_baku_tanggal["Receiving Plant"] = ""
    konsumsi_bahan_baku_tanggal['Bulan'] =  pd.DatetimeIndex(konsumsi_bahan_baku_tanggal['Posting Date']).month
    konsumsi_bahan_baku_tanggal['Tahun'] =  pd.DatetimeIndex(konsumsi_bahan_baku_tanggal['Posting Date']).year

    konsumsi_bahan_baku_bulan = konsumsi_bahan_baku_tanggal.pivot_table(index=["Tahun","Bulan",'Material','Plant', "Description"], aggfunc=np.sum).reset_index()
    konsumsi_bahan_baku_bulan["Receiving Plant"] = ""
    Data_Per_Tanggal["Konsumsi"] = konsumsi_bahan_baku_tanggal
    Data_Per_Bulan["Konsumsi"] = konsumsi_bahan_baku_bulan
    
    #F - STOCK
    pandas_file['stock']['To Date'] = pandas_file['stock'].apply(date_change, axis=1)
    pandas_file['stock']['To Date'] =  pd.to_datetime(pandas_file['stock']['To Date'])
    pandas_file['stock']['Tanggal'] =  pd.to_datetime(pandas_file['stock']['To Date'], format='%d%b%Y:%H:%M:%S.%f')
    pandas_file['stock']['Bulan'] =  pd.DatetimeIndex(pandas_file['stock']['Tanggal']).month
    pandas_file['stock']['Tahun'] =  pd.DatetimeIndex(pandas_file['stock']['Tanggal']).year
    pandas_file['stock']['Vala'] = pandas_file['stock']['Vala'].map(plant_convert)
    pandas_file['stock']['Material'] = pandas_file['stock']['Material'].map(material_list2)

    data_stock = pandas_file['stock'].pivot_table(index=[ "Tahun","Bulan",'Material','Vala'], values=["Closing Stock", "Closing Value"], aggfunc=np.sum).reset_index()
    data_stock.columns = ["Tahun","Bulan",'Material','Plant',"Closing Stock", "Closing Value"]
    data_stock["Receiving Plant"] = ""

    Data_Per_Bulan["Stock Tonase"] = data_stock[["Tahun","Bulan",'Material','Plant',"Closing Stock","Receiving Plant"]]
    Data_Per_Bulan["Stock Tonase"].columns = ["Tahun","Bulan",'Material','Plant',"Value","Receiving Plant"]
    Data_Per_Bulan["Stock Tonase"]["Description"] = "Jumlah Stock Fisik (Tonase)"

    Data_Per_Bulan["Stock Value"] = data_stock[["Tahun","Bulan",'Material','Plant',"Closing Value","Receiving Plant"]]
    Data_Per_Bulan["Stock Value"].columns = ["Tahun","Bulan",'Material','Plant',"Value","Receiving Plant"]
    Data_Per_Bulan["Stock Value"]["Description"] = "Jumlah Stock Value"

    #combining data
    Data_Per_Bulan = pd.concat(Data_Per_Bulan, sort=False).reset_index(level=0).rename(columns={"level_0": "Kategori"})

    Data_Per_Tanggal = pd.concat(Data_Per_Tanggal).reset_index(level=0).rename(columns={"level_0": "Kategori"})
    Data_Per_Tanggal = Data_Per_Tanggal.drop(columns = ["Bulan"])
    Data_Per_Tanggal["Kategori"] = Data_Per_Tanggal["Kategori"].map({"Konsumsi" : "Pemakaian","Kedatangan": "Kedatangan","GI POSTO":"Kedatangan","TP to TB":"Kedatangan","TP to Prod":"Kedatangan","Hasil Produksi": "Saldo Awal","Pembelian CS":"Saldo Awal","Penjualan":"Saldo Awal"})
    Data_Per_Tanggal["Posting Date"] = Data_Per_Tanggal["Posting Date"].astype(str)

    Data_Per_Bulan["Kategori"] = Data_Per_Bulan["Kategori"].map({"Konsumsi" : "Pemakaian","Kedatangan": "Kedatangan","GI POSTO":"Kedatangan","TP to TB":"Kedatangan","TP to Prod":"Kedatangan","Hasil Produksi": "Saldo Awal","Pembelian CS":"Saldo Awal","Penjualan":"Saldo Awal", "Stock Tonase":"Stock Tonase","Stock Value":"Stock Value"})
    Data_Per_Bulan["Description"] = Data_Per_Bulan.apply(change_text, axis=1)
    Data_Per_Bulan["Departement"] = Data_Per_Bulan["Plant"].map(plant_dept)
    Data_Per_Bulan = Data_Per_Bulan[Data_Per_Bulan["Departement"] != "0"]
    Data_Per_Bulan = Data_Per_Bulan.pivot_table(index = ["Tahun", "Bulan","Kategori","Description", "Material", "Plant", "Departement"],values = ["Value"],aggfunc=np.sum).fillna(0).reset_index()

    bln = Data_Per_Bulan["Bulan"].value_counts().idxmax()
    thn = Data_Per_Bulan["Tahun"].value_counts().idxmax()

    data = {}

    data_dept = []
    data_mont = []
    data_tgl  = [data_tanggal(tahun = i["Tahun"],
                    bulan = int(float(bln)),
                    posting_date = i["Posting Date"],
                    material = i["Material"],
                    kategori = i["Kategori"],
                    plant = i["Plant"],
                    receiving_plant = i["Receiving Plant"],
                    description = i["Description"],
                    value = i["Value"],
                    uploader = request.user,
                    confirm = False,
                    valid = False) for i in Data_Per_Tanggal.to_dict("report")]

    for n, mat in enumerate(Data_Per_Bulan["Material"].unique()):
        if mat != "":
            output = spit_data_into_departemen(Data_Per_Bulan, thn, bln, mat)
            output = output.drop("Kategori", axis = 1)

            output2 = split_data_month(Data_Per_Bulan, thn, bln, mat)

            data_dept.append(data_bulan_unit(
                                    tahun = int(float(thn)),
                                    material = mat,
                                    bulan = int(float(bln)),
                                    data = output.fillna("").to_csv(), 
                                    valid = False,
                                    confirm = False,
                                    uploader = request.user
                                )
                            )

            data_mont.append(data_tahun_unit(
                                    tahun = int(float(thn)),
                                    material = mat,
                                    bulan = int(float(bln)),
                                    data = output2.fillna("").to_csv(), 
                                    valid = False,
                                    confirm = False,
                                    uploader = request.user
                                )
                            )

            data_output = {}
            data_output["value"] = output.values.tolist()
            data_output["columns"] = [{"title" : i}  for i in list(output.columns)]
            data_output["Header"] = mat
            data_output["table"] = f'<div style = ""><table id="table-{int(float(thn))}{int(float(bln))}{n}"  class="table  table-hover"  style="width : 100%"></table></div>'                                                                 
            data_output["id"] = f"#table-{int(float(thn))}{int(float(bln))}{n}"
            data[mat] = data_output
    

    
    data_tahun_unit.objects.filter(uploader=request.user).filter(tahun=int(float(thn))).filter(bulan=int(float(bln))).filter(confirm=False).delete()
    data_bulan_unit.objects.filter(uploader=request.user).filter(tahun=int(float(thn))).filter(bulan=int(float(bln))).filter(confirm=False).delete()
    
    
    date_delete = list(pandas_file['export']['Posting Date'].dropna().unique())
    for dt in date_delete:
        data_tanggal.objects.filter(uploader=request.user).filter(posting_date=str(dt)).filter(confirm=False).delete()


    data_tanggal.objects.bulk_create(data_tgl)
    data_tahun_unit.objects.bulk_create(data_mont)
    data_bulan_unit.objects.bulk_create(data_dept)

    return data

def split_data_month(data, tahun, bulan, mat):
    data = data[(data["Tahun"] == tahun) &  (data["Material"] == mat) & (data["Bulan"] == bulan)]
    data = data.pivot_table(index = ["Kategori"],values = ["Value"], columns = ["Plant"],aggfunc=np.sum).fillna(0).reset_index()
    data.columns = [i[1] if (i[1] != "" and i[1] != "") else i[0] for n,i in enumerate(data.columns)]
    data = data.loc[:, data.any()]
    
    return data


def spit_data_into_departemen(data, tahun, bulan, mat):
    data = data[(data["Tahun"] == tahun) &  (data["Material"] == mat) & (data["Bulan"] == bulan)]
    data = data.pivot_table(index = ["Kategori", "Description"],values = ["Value"], columns = ["Departement"],aggfunc=np.sum).fillna(0).reset_index()
    data.columns = [i[1] if (i[1] != "" and i[1] != "") else i[0] for n,i in enumerate(data.columns)]
    data = data.loc[:, data.any()]

    order_data = [{"Saldo Awal" : ["Saldo Bulan Sebelumnya", "Produksi Sendiri","Pembelian CS"]}, {"Kedatangan" : []}, {"Pemakaian" : []},{"Stock Value":[]},{"Stock Tonase":[]}]

    data_ordered = []
    for i in order_data:
        if list(i.keys())[0] == "Saldo Awal":
            a = data[data["Kategori"] == list(i.keys())[0]].sort_values(by=['Description'], ascending=False)
            if a.shape[0] != 0:
                jumlah = ["saldo awal","Jumlah " + list(i.keys())[0]] + list(a[a["Kategori"] == list(i.keys())[0]].sum(axis = 0).values[2:])
                a.loc[-1] = jumlah
                a = (a.reset_index(drop  = True))

                value_div = str(list(range(0, a.shape[0]-1)))
                text = f'<div class = "dropdown-table-month" style =" width: 0px ; display: inline-block; height: 12px; margin-right: 3px;font-weigth: bolder" value="{value_div}" name=""></div>' + list(i.keys())[0]
                a.loc[-1] = ["saldo awal",text] + list([""for i in range((a.shape[1]-2))])
                a.index = a.index + 1 
                a = a.sort_index() 
                data_ordered.append(a[list(a.columns)])
            else:
                value_div = str([])
                text2 = f'<div class = "dropdown-table-month" style =" width: 0px ; display: inline-block; height: 12px; margin-right: 3px;font-weigth: bolder" value="{value_div}" name=""></div>'
                jumlah2 = pd.DataFrame([["saldo awal",text2 + list(i.keys())[0]] + list([""for i in range((a.shape[1]-2))])], columns = list(a.columns))
                data_ordered.append(jumlah2)

        elif list(i.keys())[0] == "Kedatangan":
            a = data[data["Kategori"] == list(i.keys())[0]].sort_values(by=['Description'], ascending=True)

            if a.shape[0] != 0:
                jumlah = (["kedatangan","Jumlah " + list(i.keys())[0] ] + list(a[a["Kategori"] == list(i.keys())[0]].sum(axis = 0).values[2:]))
                a["kategori desc"] = a.apply(get_class_desc, axis=1)
                a["Description"] = a.apply(get_class_desc2, axis=1)
                kat = a["kategori desc"].unique()

                value_div = str(list(range(0, a.shape[0] + len(kat))))
                text2 = f'<div class = "dropdown-table-month" style =" width: 0px ; display: inline-block; height: 12px; margin-right: 3px;font-weigth: bolder" value="{value_div}" name=""></div>'

                for n, j in enumerate(kat):
                    b = a[a["kategori desc"] == j]    
                    b = b.pivot_table(index=['Kategori','Description'],margins=True,margins_name="kedatangan",aggfunc=sum).reset_index()
                    b = b.reindex(np.roll(b.index, shift=1))
                    value_div = str(list(range(0, b.shape[0]-1)))
                    if "ZZ." in j:
                        j = j.split(".")[-1]
                    text = f'<div class = "dropdown-table-month" style =" width: 12px ; display: inline-block; height: 12px; margin-right: 3px;font-weigth: bolder" value="{value_div}" name=""><stong>+</strong></div>' + j
                    b.iloc[0,1] = text
                    if n == 0:
                        jumlah2 = pd.DataFrame([["kedatangan",text2+list(i.keys())[0]] + list([""for i in range((b.shape[1]-2))])], columns = list(b.columns))
                        data_ordered.append(jumlah2)
                    data_ordered.append(b)
                data_ordered[-1].loc[len(data_ordered[-1])] = jumlah
            else:
                value_div = str([])
                text2 = f'<div class = "dropdown-table-month" style =" width: 0px ; display: inline-block; height: 12px; margin-right: 3px;font-weigth: bolder" value="{value_div}" name=""></div>'
                jumlah2 = pd.DataFrame([["kedatangan",text2 + list(i.keys())[0]] + list([""for i in range((a.shape[1]-2))])], columns = list(a.columns))
                data_ordered.append(jumlah2)
            # data_ordered[-1].loc[len(data_ordered[-1])] = jumlah2

        elif list(i.keys())[0] == "Pemakaian":
            a = data[data["Kategori"] == list(i.keys())[0]].sort_values(by=['Description'], ascending=True)
            if a.shape[0] != 0:
                jumlah = ["pemakaian", "Jumlah " + list(i.keys())[0] ] + list(a[a["Kategori"] == list(i.keys())[0]].sum(axis = 0).values[2:])
                a["kategori desc"] = a.apply(get_class_desc, axis=1)
                a["Description"] = a.apply(get_class_desc2, axis=1)
                kat = a["kategori desc"].unique()

                value_div = str(list(range(0, a.shape[0] + len(kat))))
                text2 = f'<div class = "dropdown-table-month" style =" width: 0px ; display: inline-block; height: 12px; margin-right: 3px;font-weigth: bolder" value="{value_div}" name=""></div>'


                for n,j in enumerate(kat):
                    b = a[a["kategori desc"] == j]
                    b = b.pivot_table(index=['Kategori','Description'],margins=True,margins_name="pemakaian",aggfunc=sum).reset_index()
                    b = b.reindex(np.roll(b.index, shift=1))

                    value_div = str(list(range(0, b.shape[0]-1)))
                    if "ZZ." in j:
                        j = j.split(".")[-1]
                    text = f'<div class = "dropdown-table-month" style =" width: 12px ; display: inline-block; height: 12px; margin-right: 3px;font-weigth: bolder" value="{value_div}" name=""><stong>+</strong></div>' + j
                    b.iloc[0,1] = text
                    if n == 0:
                        jumlah2 = pd.DataFrame([["pemakaian",text2+list(i.keys())[0]] + list([""for i in range((b.shape[1]-2))])], columns = list(b.columns))
                        data_ordered.append(jumlah2)
                    data_ordered.append(b)
                
                data_ordered[-1].loc[len(data_ordered[-1])] = jumlah
            else:
                value_div = str([])
                text2 = f'<div class = "dropdown-table-month" style =" width: 0px ; display: inline-block; height: 12px; margin-right: 3px;font-weigth: bolder" value="{value_div}" name=""></div>'
                jumlah2 = pd.DataFrame([["pemakaian",text2 + list(i.keys())[0]] + list([""for i in range((a.shape[1]-2))])], columns = list(a.columns))
                data_ordered.append(jumlah2)

        elif  list(i.keys())[0] == "Stock Tonase":
            
            a = data[data["Kategori"] == list(i.keys())[0]].sort_values(by=['Description'], ascending=False)
            # a.iloc[0, 1] = "Stock Fisik (Tonase)"
            data_ordered.append(a[list(a.columns) ])
            # data_ordered.append(pd.Series(["Stock Fisik"] + [ "" for i in range(len(a)-1)]))
        else:
            a = data[data["Kategori"] == list(i.keys())[0]].sort_values(by=['Description'], ascending=False)
            # a.iloc[0, 1] = "Stock Value"
            data_ordered.append(a[list(a.columns) ])

    a = pd.concat(data_ordered).reset_index(level=0).rename(columns={"level_0": "Kategori"}).iloc[:,1:]
    jumlah = ["Summary","Jumlah Administrasi"] + list(a[a["Kategori"] == "Saldo Awal"].sum(axis = 0).values[2:] + a[a["Kategori"] == "Kedatangan"].sum(axis = 0).values[2:] - a[a["Kategori"] == "Pemakaian"].sum(axis = 0).values[2:])
    
    # a = a.drop(["kategori"], axis =1)
    a.loc[len(a)] = ["Stock Fisik", "Stock Fisik"] + [""  for i in range(len(jumlah) - 2)]
    a.loc[len(a)] = jumlah
    a.loc[len(a)] = ["Summary","Total Administrasi"] + [""  for i in range(len(jumlah) - 2)]
    
    idx = list(a.index)
    idx[-3], idx[-3] = idx[-3], idx[-3]
    idx[-2], idx[-4] = idx[-4], idx[-2]
    idx[-1], idx[-5] = idx[-5], idx[-1]
    a = a.reindex(idx).reset_index().iloc[:,1:]
    return a



def extract_data(data, mode):

    #Get Plant List from data base
    plant_list = pd.DataFrame(list(Plant.objects.all().values()))
    plant_list = plant_list.rename(columns = {"id":'ID','nama': 'Nama Plant', "kode":'Kode Plant', "departement":'Nama Departemen','perusahaan':'Perusahaan', 'kode pos':'Kode Pos', "lokasi":'Lokasi'})
    plant_convert = plant_list[["Kode Plant", "Nama Plant"]].set_index("Kode Plant").to_dict()["Nama Plant"]
    plant_dept = plant_list[["Kode Plant", "Nama Departemen"]].set_index("Kode Plant").to_dict()["Nama Departemen"]


    #Get Material list from database
    materail_list = pd.DataFrame(list(Material.objects.all().values()))
    material_list2 = materail_list[['kategori',"nama_kelompok",'kode']].set_index('kode').to_dict()['nama_kelompok']
    material_list1 = materail_list[['kategori',"nama_kelompok",'kode']].set_index('kode').to_dict()['kategori']
    
    context = {}
    data = data.drop(['id'], axis=1)
    data = data.drop(['last_updated'], axis=1)
    data = data.drop(['uploader_id'], axis=1)

    if mode == "saldo_awal":
        data["departemen"] = data["unit"].map(plant_dept)
        data["nama unit"] = data["unit"].map(plant_convert)

        data["nama material"] = data["material"].map(material_list2)
        data["kelompok material"] = data["material"].map(material_list1)
        data = data[["tahun", "kelompok material", "nama material", "material", "departemen", "nama unit", "unit", "nilai"]]

    elif mode == "plan":
        data = data[["kode", "departement", "nama", "perusahaan", "kode_pos", "lokasi"]]
    
    elif mode == "material":
        data = data[["kategori","nama_kelompok","kode","deskripsi", "informasi"]]
    
        
    data["No"] = [ i+1 for i in range(data.shape[0])]
    header_name = list(data.columns)
    header_name.insert(0, header_name.pop(-1))
    data = data[header_name]
    data.columns = [i.replace("_", " ").capitalize() for i in data.columns]
    header = [{"title" : i }  for i in list(data.columns) ]
    values = data.values.tolist()

    context["value"] = values
    context["header"] = header

    return context

def update_plan(data, request):  
    data = data.fillna("").to_dict("report")
    data = [ Plant(
        kode = i["Kode"],
        departement = i["Departement"],
        nama = i["Nama"],
        perusahaan = i["Perusahaan"],
        kode_pos = i["Kode pos"],
        lokasi = i["Lokasi"],
        latitude = "",
        longitude = "",
        keterangan = "",
        email = "",
        number = "",
        # latitude = i["Latitude"],
        # longitude = i["Longitude"],
        # keterangan = i["Keterangan"],
        # email = i["Email"],
        # number = i["Number"],
        uploader = request.user, 
        ) for i in data ]
    Plant.objects.all().delete()
    Plant.objects.bulk_create(data)

def update_material(data, request):  
    data = data.fillna("").to_dict("report")
    data = [ Material(
        kategori = i["Kategori"],
        nama_kelompok = i["Nama kelompok"],
        kode = i["Kode"],
        deskripsi = i["Deskripsi"],
        informasi = i["Informasi"],
        uploader = request.user, 
        ) for i in data ]
    Material.objects.all().delete()
    Material.objects.bulk_create(data)


def update_mvt(data, request):  
    data = data.fillna("").to_dict("report")
    data = [ Material(
        kode = i["Kode"],
        deskripsi = i["Deskripsi"],
        uploader = request.user, 
        ) for i in data ]
    MovementType.objects.all().delete()
    MovementType.objects.bulk_create(data)


def update_saldo(data, request):  
    data = data.fillna("").to_dict("report")
    data = [ SaldoAwal(
        tahun = i["Tahun"],
        unit = i["Unit"],
        material = i["Material"],
        nilai = i["Nilai"],
        uploader = request.user, 
        ) for i in data ]
    SaldoAwal.objects.all().delete()
    SaldoAwal.objects.bulk_create(data)

def create_saldo_awal(thn,request):
    SaldoAwal.objects.all().delete()
    materail_list = pd.DataFrame(list(Material.objects.all().values()))
    plant_list =  pd.DataFrame(list(Plant.objects.all().values()))

    mat = materail_list[materail_list["kategori"] == "Bahan Baku"]["kode"].unique()
    plant = plant_list[(plant_list["departement"] != "0") & (plant_list["departement"] != "")]["kode"].unique()
    
    a = [mat, plant]

    data = list(itertools.product(*a))
    idx = ['{}'.format(i) for i in range(1, len(data)+1)]
    df = pd.DataFrame(data, index=idx, columns=["Material", "Unit"])
    df["Tahun"] = thn
    df["Nilai"] = np.random.randint(30000, 100000)

    for i in (df.to_dict("report")):
        SaldoAwal.objects.create(
                                tahun = int(float(i["Tahun"])),
                                unit = i["Unit"],
                                material = i["Material"],
                                nilai = i["Nilai"],
                                uploader = request.user
                            )



def get_vatidate_data():
    id_username = ( pd.DataFrame(User.objects.all().values("id", "username")).set_index("id").to_dict()["username"])
    obj = list(data_bulan_unit.objects.filter(valid = False).filter(confirm = True).values("tahun", "bulan", "uploader").distinct())
    
    data = []
    for i in obj:
        tahun = i["tahun"]
        bulan = i["bulan"]
        i["username"] = id_username[i["uploader"]]
        last_update = list(data_bulan_unit.objects.filter(valid = False).filter(confirm = True).filter(tahun = tahun).filter(bulan = bulan).filter(uploader = i["uploader"]).values("last_updated").distinct())
        date = [ d["last_updated"].strftime("%d/%m/%Y") for d in last_update]
        i["last_update"] = max(set(date), key=date.count)
        data.append(i)
    
    data_output = {}
    for item in data:
        name = int2month(int(item["bulan"])) + " - " + str(int(item["tahun"])) + " by " + i["username"]
        data_output[name] = {}
        data_output[name]["last_update"] = item["last_update"]
        material = data_bulan_unit.objects.filter(valid = False).filter(confirm = True).filter(tahun = item["tahun"]).filter(bulan = item["bulan"]).filter(uploader = item["uploader"]).values("material").distinct()
        for n,mat in enumerate(material):
            data = list(data_bulan_unit.objects.filter(valid = False).filter(confirm = True).filter(tahun = item["tahun"]).filter(bulan = item["bulan"]).filter(uploader = item["uploader"]).filter(material= mat["material"]).values("data"))[0]["data"]
            data = pd.read_csv(StringIO(data))
            data = data.drop("Unnamed: 0", axis = 1)
            data = data.fillna("")
            
            data_output[name][mat["material"]] = {}
            data_output[name][mat["material"]]["value"] = data.values.tolist()
            data_output[name][mat["material"]]["columns"] = [{"title" : i}  for i in list(data.columns)]
            # data_output[name][mat["material"]][""] = mat["material"]
            data_output[name][mat["material"]]["table"] = f'<div style = ""><table id="table-{int(float(item["tahun"]))}{int(float(item["bulan"]))}_{n}_{item["uploader"]}"  class="display table  table-hover"  style="width : 100%"></table></div>'                                                                 
            data_output[name][mat["material"]]["id"] = f'#table-{int(float(item["tahun"]))}{int(float(item["bulan"]))}_{n}_{item["uploader"]}'
    context = json.dumps(data_output, default=default)
    return context

def get_home_data():
    data = {}
    validasi_count = len(list(data_bulan_unit.objects.filter(valid = False).filter(confirm = True).values("tahun", "bulan", "uploader").distinct()))
    tahun = [i["tahun"] for i in list(data_bulan_unit.objects.filter(valid = True).values("tahun").distinct())]
    data["valid_count"] = validasi_count
    data["tahun_report"] = tahun

    return data

def validate(data):
    abbr_to_num = {name:num for num, name in enumerate(calendar.month_abbr) if num}
    id_username = ( pd.DataFrame(User.objects.all().values("id", "username")).set_index("username").to_dict()["id"])

    data = data.split(" ")
    bulan, tahun, user = abbr_to_num[data[0]], data[2], id_username[data[4]]
    
    start = datetime.date(int(tahun), int(bulan), 1)
    new_end = datetime.date(int(tahun), int(bulan +1), 1)
    
    data_bulan_unit.objects.filter(tahun = int(tahun)).filter(bulan = int(bulan)).filter(valid=True).filter(confirm=True).delete()
    data_tahun_unit.objects.filter(tahun = int(tahun)).filter(bulan = int(bulan)).filter(valid=True).filter(confirm=True).delete()
    data_tanggal.objects.filter(posting_date__range=[start, new_end]).filter(valid=True).filter(confirm=True).delete()


    data_bulan_unit.objects.filter(tahun = int(tahun)).filter(bulan = int(bulan)).filter(valid=False).filter(confirm=True).update(valid=True)
    data_tahun_unit.objects.filter(tahun = int(tahun)).filter(bulan = int(bulan)).filter(valid=False).filter(confirm=True).update(valid=True)
    data_tanggal.objects.filter(posting_date__range=[start, new_end]).filter(valid=False).filter(confirm=True).update(valid=True)

    reset(int(tahun))

def delete_data_validate(data):
    abbr_to_num = {name:num for num, name in enumerate(calendar.month_abbr) if num}
    id_username = ( pd.DataFrame(User.objects.all().values("id", "username")).set_index("username").to_dict()["id"])

    data = data.split(" ")
    bulan, tahun, user = abbr_to_num[data[0]], data[2], id_username[data[4]]

    start = datetime.date(int(tahun), int(bulan), 1)
    new_end = datetime.date(int(tahun), int(bulan +1), 1)
    
    print(data_bulan_unit.objects.filter(tahun = int(tahun)).filter(bulan = int(bulan)).filter(uploader = user).filter(valid=False).filter(confirm=True).delete())
    print(data_tahun_unit.objects.filter(tahun = int(tahun)).filter(bulan = int(bulan)).filter(uploader = user).filter(valid=False).filter(confirm=True).delete())
    print(data_tanggal.objects.filter(uploader = user).filter(posting_date__range=[start, new_end]).filter(valid=False).filter(confirm=True).delete())

def delete_data_validate_all():
    print(data_bulan_unit.objects.filter(valid=False).filter(confirm=True).delete())
    print(data_tahun_unit.objects.filter(valid=False).filter(confirm=True).delete())
    print(data_tanggal.objects.filter(valid=False).filter(confirm=True).delete())


def delete_unconfirm_data(request):
    for i in (data_bulan_unit.objects.filter(uploader=request.user).filter(confirm = False).values('bulan', "tahun").distinct()):
        data_bulan_unit.objects.filter(uploader=request.user).filter(confirm=True).filter(valid=False).filter(bulan=int(i["bulan"])).filter(tahun=int(i["tahun"]))
    
    for i in (data_tahun_unit.objects.filter(uploader=request.user).filter(confirm = False).values('bulan', "tahun").distinct()):
        data_tahun_unit.objects.filter(uploader=request.user).filter(confirm=True).filter(valid=False).filter(bulan=i["bulan"]).filter(tahun=i["tahun"]).delete()

    for i in (data_tanggal.objects.filter(uploader=request.user).filter(confirm = False).values('posting_date').distinct()):
        data_tanggal.objects.filter(uploader=request.user).filter(confirm=True).filter(valid=False).filter(posting_date=i["posting_date"]).delete()

    data_bulan_unit.objects.filter(uploader=request.user).update(confirm = True )
    data_tahun_unit.objects.filter(uploader=request.user).update(confirm = True)
    data_tanggal.objects.filter(uploader=request.user).update(confirm = True)


def cancel_data_upload(request):
    data_bulan_unit.objects.filter(uploader=request.user).filter(confirm=False).delete()
    data_tahun_unit.objects.filter(uploader=request.user).filter(confirm=False).delete()
    data_tanggal.objects.filter(uploader=request.user).filter(confirm=False).delete()



def get_data_report(tahun):
    data ={}
    material = sorted([i["material"] for i in list(data_bulan_unit.objects.filter(valid=True).filter(confirm=True).filter(tahun = int(tahun)).values("material").distinct())])
    
    for k,mat in enumerate(material):
        data[mat] = {}
        data[mat]["tahun"] = {}
        data[mat]["bulan"] = {}
        bln = sorted([i["bulan"] for i in list(data_bulan_unit.objects.filter(valid=True).filter(confirm=True).filter(tahun = int(tahun)).filter(material = mat).values("bulan").distinct())])
        for bulan in bln:
            data_unit = list(data_bulan_unit.objects.filter(valid=True).filter(confirm=True).filter(tahun = int(tahun)).filter(bulan = bulan).filter(material = mat).values("data"))[0]["data"]
 
            data_unit = pd.read_csv(StringIO(data_unit))
            data_unit = data_unit.drop("Unnamed: 0", axis = 1)
            data_unit = data_unit.fillna("")

            data[mat]["bulan"][int2month(bulan)] = {}
            data[mat]["bulan"][int2month(bulan)]["value"] = data_unit.values.tolist()
            data[mat]["bulan"][int2month(bulan)]["columns"] = [{"title" : i}  for i in list(data_unit.columns)]
            data[mat]["bulan"][int2month(bulan)]["Header"] = int2month(bulan)
            data[mat]["bulan"][int2month(bulan)]["table"] = f'<div style = ""><table id="table-tahun-{k}-{int2month(bulan)}"  class="table  table-hover"  style="width : 100%"></table></div>'                                                                 
            data[mat]["bulan"][int2month(bulan)]["id"] = f"#table-tahun-{k}-{int2month(bulan)}"
    
        data_mont2 = list(data_tahun_html.objects.filter(tahun = int(tahun)).filter(material = mat).values("data"))[0]["data"]
        data_mont2 = pd.read_csv(StringIO(data_mont2))
        data_mont2 = data_mont2.drop("Unnamed: 0", axis = 1)
        data_mont2 = data_mont2.fillna("")

        data[mat]["tahun"]["value"] = data_mont2.values.tolist()
        data[mat]["tahun"]["columns"] = [{"title" : i}  for i in list(data_mont2.columns)]
        data[mat]["tahun"]["Header"] = mat
        data[mat]["tahun"]["table"] = f'<div style = ""><table id="table-tahun-{k}"  class="table  table-hover"  style="width : 100%"></table></div>'                                                                 
        data[mat]["tahun"]["id"] = f"#table-tahun-{k}"
    return data

def get_available_data(request):
    waktu_unique = []
    waktu = list(data_bulan_unit.objects.filter(valid = True).values( "tahun","bulan").distinct())
    if list(waktu) != []:
        for i in waktu:
            if [float(i["tahun"]), int2month(i["bulan"])] not in waktu_unique:
                waktu_unique.append([float(i["tahun"]), int2month(i["bulan"])])

    waktu = list(data_tahun_unit.objects.filter(valid = True).values( "tahun","bulan").distinct())
    if list(waktu) != []:
        for i in waktu:
            if [float(i["tahun"]), int2month(i["bulan"])] not in waktu_unique:
                waktu_unique.append([float(i["tahun"]), int2month(i["bulan"])])
    
    waktu = list(data_tanggal.objects.filter(valid = True).values( "tahun","bulan").distinct())
    if list(waktu) != []:
        for i in waktu:
            if [float(i["tahun"]), int2month(i["bulan"])] not in waktu_unique:
                waktu_unique.append([float(i["tahun"]), int2month(i["bulan"])])
    
    return waktu_unique

def delete_data_from_post(data):
    num_to_abbr = { name:num for num, name in enumerate(calendar.month_abbr) if num}
    bln, thn = data.split(" - ")

    data_bulan_unit.objects.filter(valid=True).filter(tahun=int(thn)).filter( bulan = num_to_abbr[bln]).delete()
    data_tahun_unit.objects.filter(valid=True).filter(tahun=int(thn)).filter( bulan = num_to_abbr[bln]).delete()
    data_tanggal.objects.filter(valid=True).filter(tahun=int(thn)).filter( bulan = num_to_abbr[bln]).delete()

def reset(tahun):
    data = []
    material = sorted([i["material"] for i in list(data_bulan_unit.objects.filter(valid=True).filter(confirm=True).filter(tahun = int(tahun)).values("material").distinct())])
    for k,mat in enumerate(material):
        bln = sorted([i["bulan"] for i in list(data_bulan_unit.objects.filter(valid=True).filter(confirm=True).filter(tahun = int(tahun)).filter(material = mat).values("bulan").distinct())])
        data_month = {}
        for bulan in bln:
            data_mont = list(data_tahun_unit.objects.filter(valid=True).filter(confirm=True).filter(tahun = int(tahun)).filter(bulan = bulan).filter(material = mat).values("data"))[0]["data"]

            data_mont = pd.read_csv(StringIO(data_mont))
            data_mont = data_mont.drop("Unnamed: 0", axis = 1)
            data_mont = data_mont.fillna("")
            data_month[int2month(bulan)] = data_mont
    
        data_month = pd.concat(data_month, sort=False).reset_index(level=0).rename(columns={"level_0": "Bulan"}).fillna(0)
        list_kategori = ["Saldo Awal", "Kedatangan", "Pemakaian", "Stock Tonase"]
    
        data_total = {}
        data_mont2 = {}
        for n, kat in enumerate(list_kategori):
            d_temp = data_month[data_month["Kategori"] == kat].T
            d_temp.columns = d_temp.iloc[0]
            d_temp = d_temp.drop(['Bulan', 'Kategori']).sort_index()
            if n < 3:
                data_total[kat] = d_temp.sum().rename('Total' )
            d_temp = d_temp.append(d_temp.sum().rename('Total ' + kat)).reset_index() 

            value_div = str(list(range(0, max(d_temp.index))))
            text = f'<div class = "dropdown-table-month" style =" width: 0px ; display: inline-block; height: 12px; margin-right: 3px;font-weigth: bolder" value="{value_div}" name=""></div>' + kat.capitalize()

            d_temp.loc[-1] = [text]+ ["" for i in d_temp.columns[1:]]  # adding a row
            d_temp.index = d_temp.index + 1  # shifting index
            d_temp.sort_index(inplace=True)
            data_mont2[kat] = d_temp

            if n == 2:
                data_total = pd.concat(data_total, sort=False).reset_index(level=0).reset_index()
                data_total = pd.pivot_table(data_total, columns=["Bulan"], index = ["level_0"], values=["Total"]).fillna(0)
                ttl_adm = None
                for i in ["Saldo Awal", "Kedatangan","Pemakaian"]:
                    if i in data_total.index:
                        if ttl_adm is  None:
                            ttl_adm = data_total.loc[i]
                        else:
                            if  i in ["Saldo Awal", "Kedatangan"]:
                                ttl_adm = ttl_adm + data_total.loc[i]
                            else:
                                ttl_adm = ttl_adm - data_total.loc[i]
                if i is not None:
                    data_total.loc["Total Administrasi"] = ttl_adm
                data_total = data_total.reset_index()
                data_total.columns = ["index"] + [i[1] for i in data_total.columns[1:]]

                data_mont2["Total Administrasi"] = data_total.iloc[-1:]

            if n == 3 :
                b = (data_mont2["Total Administrasi"])
                a = d_temp.iloc[-1:].reset_index()
                a = a.drop("level_0", axis = 1)
                a.columns = ["index"] + [i for i in a.columns[1:]]

                c = b.iloc[0, 1:]-a.iloc[0,1:]
                c["index"] = "Sisa Administrasi"
                data_mont2["Sisa Administrasi"] = c.to_frame().T
        bln  = ["index"] + [int2month(i) for i in bln]
        data_mont2 = pd.concat(data_mont2, sort=False).reset_index().fillna(0).drop(["level_0", "level_1"], axis = 1)[bln]
        data_mont2.columns = ["Rincian"] + [ i for i in data_mont2.columns[1:]]

        data.append(data_tahun_html(
                                    tahun = int(float(tahun)),
                                    material = mat,
                                    data = data_mont2.fillna("").to_csv(),
                                )
                            )



    data_tahun_html.objects.filter(tahun = int(tahun)).delete()
    data_tahun_html.objects.bulk_create(data)


def get_chart_data():
    data = {
        "" : ['<a ><i class="fa fa-plus-circle" ></i><a/>','<a><i class="fa fa-plus-circle"></i><a/>','<a><i class="fa fa-plus-circle"></i><a/>'],
        "Unit" : ["Unit 1","Unit 2","Unit 3"],
        "Penanggung Jawab" : ["nama1", "nama2", "nama3"],
        "Kontak" : ["0857XX", "0737XX", "0677XX"],
        "Total Trip (km)" : [100, 120, 130],
        "Lama Trip (jam)" : [54,23, 80],
        "Estimate Cost" : [3434234,23234234,23423423],
        "Actual Cost" : [43435345,12312,54645],
        "Review" : ['<i class="fa fa-star"></i><i class="fa fa-star"></i><i class="fa fa-star"></i>','<i class="fa fa-star"></i><i class="fa fa-star"></i><i class="fa fa-star"></i>','<i class="fa fa-star"></i><i class="fa fa-star"></i><i class="fa fa-star"></i>'],
        "Trip History" : ["safe","safe","safe"],
        "Score" : [8,5,4]
    }

    data = pd.DataFrame(data= data)

    output = {}
    output["value"] = data.values.tolist()
    output["columns"] = [{"title" : i} if  n != 0 else {"title" : i, "className" : "details-control"}  for n, i in enumerate(list(data.columns)) ]
    output["table"] = f'<div style = ""><table id="mytable"  class="table  table-hover"  style="width : 100%"></table></div>'                                                                 
    output["id"] = f"#mytable"

    return output




