############### IMPORT PACKAGES ###############
import numpy as np
import pandas as pd
import streamlit as st
import json
from PIL import Image
############### IMPORT PACKAGES ###############


############### PENENTUAN DATA ###############
data_json = json.load(open('kode_negara_lengkap.json'))
data = pd.read_csv("produksi_minyak_mentah.csv")
############### PENENTUAN DATA ###############


############### PENGOLAHAN DATA ###############
list_nama_negara = []
list_kode_negara = []
dict_region = {}
dict_sub_region = {}

jenis_unik = list(data['kode_negara'].unique()) #mencari kode unik pada data csv
for i in range(len(jenis_unik)):
    for j in data_json:
        if j["alpha-3"]==jenis_unik[i]:
            #menambahkan kode negara pada list_kode_negara
            if jenis_unik[i] not in list_kode_negara:
                list_kode_negara.append(jenis_unik[i])
            #menambahkan nama negara pada list_nama_negara
            if j["name"] not in list_nama_negara:
                list_nama_negara.append(j["name"])
            #menambahkan region dan sub-region ke dictionary yang sesuai
            dict_region[jenis_unik[i]] = j["region"]
            dict_sub_region[jenis_unik[i]] = j["sub-region"]

#Penambahan kolom pada dataframe "data"
data["nama_negara"] = ""
data["region"] = ""
data["sub-region"] = ""

#Mengisi kolom pada dataframe "data" dari list dan dictionary yang sudah dibuat sebelumnya
for i in range(len(data["kode_negara"])):
    for j in range(len(list_kode_negara)):
        if data["kode_negara"][i] == list_kode_negara[j]:
            data["nama_negara"][i] = list_nama_negara[j]
            data["region"][i] = dict_region[list_kode_negara[j]]
            data["sub-region"][i] = dict_sub_region[list_kode_negara[j]]

#Menghapus baris pada data yang bukan merupakan negara, cirinya adalah kolom nama_negara kosong
data["nama_negara"].replace('', np.nan, inplace=True)
data.dropna(subset=["nama_negara"], inplace=True)

#mengubah urutan kolom sesuai dengan permintaan soal
data = data.reindex(columns = ["nama_negara","kode_negara","tahun","region","sub-region","produksi"])

#membuat list total produksi tiap negara dari 1971-2015
total_produksi = []
for i in range(len(list_nama_negara)):
    total = data[data["nama_negara"] == list_nama_negara[i]]["produksi"].sum()
    total_produksi.append(total)

#membuat list dari region dan sub rugion menggunakan dictionary yang telah dibauat
list_region = []
list_sub_region = []
for i in range(len((list_kode_negara))):
    list_region.append(dict_region[list_kode_negara[i]])
    list_sub_region.append(dict_sub_region[list_kode_negara[i]])

#membuat array yang nantinya digunakan dalam pembuatan data frame total produksi
a = np.array(list_nama_negara)
b = np.array(list_kode_negara)
c = np.array(list_region)
d = np.array(list_sub_region)

#membuat data frame dari array a,b,c,d dan ist total produksi
data_total_produksi = pd.DataFrame({"nama_negara":a,"kode_negara":b,"region":c,"sub-region":d})
data_total_produksi["total_produksi"] = ""
for i in range(len(data_total_produksi["nama_negara"])):
    for j in range(len(list_nama_negara)):
        if data_total_produksi["nama_negara"][i] == list_nama_negara[j]:
            data_total_produksi["total_produksi"][i] = total_produksi[j]

#membuat datafram total produksi dengan pengurutan terbesar dan terkecil
data_total_produksi_terbesar = data_total_produksi.sort_values("total_produksi", ascending=False)
data_total_produksi_terkecil = data_total_produksi.sort_values("total_produksi", ascending=True)
############### PENGOLAHAN DATA ###############



###############  ###############
st.set_page_config(layout="wide")
st.image(Image.open("up_image.png"))
st.title("WORLD OIL PRODUCTION ANALYSIS")
st.markdown("Data from trusted sources")
###############  ###############


############### CONTAINER 1 ###############
with st.container():
    st.image(Image.open("barrier_image.png"))
    st.header("COUNTRY ANNUAL OIL PRODUCTION")
    negara = st.selectbox("Country",list_nama_negara,) #selectbox untuk memilih negara
    #membuat data frame
    x_con1 = np.array(data[data["nama_negara"]==negara]["tahun"])
    y_con1 = np.array(data[data["nama_negara"]==negara]["produksi"])
    d_con1 = {"tahun":x_con1,"produksi":y_con1}
    df_con1 = pd.DataFrame(d_con1).set_index("tahun")
    #menentukan ekstremum dari data yang ditentukan
    ymax_con1 = max(y_con1)
    xmax_con1 = x_con1[np.where(y_con1 == ymax_con1)]
    ymin_con1 = min(y_con1)
    xmin_con1 = x_con1[np.where(y_con1 == ymin_con1)]

    col_con1_1,col_con1_2 = st.columns([3,1])
    with col_con1_1: #membuat grafik sesuai permintaan soal 1
        st.header("LINE CHART")
        st.line_chart(df_con1)
    with col_con1_2: #menamilkan maksimum dan minimum produksi beserta tahunnya
        st.header("SIMPLE STATISTICS")
        st.metric("MAX {}".format(xmax_con1), ymax_con1,delta=None)
        st.metric("MIN {}".format(xmin_con1), ymin_con1,delta=None)
        st.metric("MEAN",round((sum(y_con1)/len(y_con1)),3))
    
    with st.expander("Production table"): #menampilkan tabel data produksi 1971-2015
        st.subheader("{} Production Table (1971-2015)".format(negara))
        st.table(df_con1)
############### CONTAINER 1 ###############


############### CONTAINER 2 ###############
with st.container():
    st.image(Image.open("barrier_image.png"))
    st.header("COUNTRY WITH THE LARGEST PRODUCTION (IN A YEAR)")
    #memasukkan input user
    B_con2 = st.number_input("Number of Countries: ",min_value=1,max_value=len(list_nama_negara),value=6)
    T_con2 = st.slider(label = "Year",min_value = 1971,max_value = 2015,step=1,value=2002) 
    #membuat dataframe
    data_urut_suatu_tahun = data.loc[data["tahun"] == T_con2].sort_values("produksi",ascending=False).head(B_con2)
    x_con2 = np.array(data_urut_suatu_tahun["nama_negara"])
    y_con2 = np.array(data_urut_suatu_tahun["produksi"])
    d_con2 = {"nama_negara":x_con2,"produksi":y_con2}
    df_con2 = pd.DataFrame(d_con2).set_index("nama_negara")
    
    col_con2_1,col_con2_2 = st.columns([3,1])
    #menampilkan grafik dan tabel
    with col_con2_1:
        st.subheader("Chart of {} Countries with The largest Production ({})".format(B_con2,T_con2))
        st.bar_chart(df_con2,use_container_width=True,height=450)
    with col_con2_2:
        with st.expander("Production Table"):
            st.subheader("Table of {} Countries with The Largest Production ({})".format(B_con2,T_con2))
            st.table(df_con2)
############### CONTAINER 2 ###############


############### CONTAINER 3 ###############
with st.container():
    st.image(Image.open("barrier_image.png"))
    st.header("COUNTRY WITH THE LARGEST PRODUCTION (TOTAL)")
    #memasukkan input user
    B_con3 = st.number_input("Number of Countries:",min_value=1,max_value=len(list_nama_negara),value=6)
    #membuat dataframe
    x_con3 = np.array(data_total_produksi_terbesar["nama_negara"].head(B_con3))
    y_con3 = np.array(data_total_produksi_terbesar["total_produksi"].head(B_con3))
    d_con3 = {"nama_negara":x_con3,"total_produksi":y_con3}
    df_con3 = pd.DataFrame(d_con3).set_index("nama_negara")

    col_con3_1,col_con3_2 = st.columns([3,1])
    #menampilkan grafik dan tabel
    with col_con3_1:
        st.subheader("Chart of {} Countries with The largest Total Production".format(B_con3))
        st.bar_chart(df_con3,height=450)
    with col_con3_2:
        with st.expander("Production Table"):
            st.subheader("Table of {} Countries with The Largest Total Production".format(B_con3))
            st.table(df_con3)
############### CONTAINER 3 ###############

############### CONTAINER 4 ###############
with st.container():
    st.image(Image.open("barrier_image.png"))
    st.header("SUMMARY OF PRODUCTION")
    #memasukkan input user
    T_con4 = st.slider(label = "Tahun",min_value = 1971,max_value = 2015,step=1,value=2002)
    #menyeleksi data sesuai tahun yang dipilih dan produksi diatas 0(agar produksi terkecil tidak 0)
    data_seleksi1 = data[(data["tahun"] == T_con4) & (data["produksi"] > 0)]
    #menyeleksi data sesuai tahun yang dipilih dan produksi 0
    data_seleksi2 = data[(data["tahun"] == T_con4) & (data["produksi"] == 0)]
    #membuat dataframe yang mengurut dari terbesar dan terkecil
    datasort_max = data_seleksi1.sort_values("produksi", ascending=False)
    datasort_min = data_seleksi1.sort_values("produksi", ascending=True)

    col_con4_1,col_con4_2 = st.columns(2)
    #menampilkan tabel data pada tahun yang dipilih
    with col_con4_1:
        st.subheader("({}) SUMMARY".format(T_con4))
        with st.expander("Biggest Production"):
            st.subheader("Country with The Largest Production ({})".format(T_con4))
            st.table(datasort_max[:1])
        with st.expander("Smallest Production"):
            st.subheader("Country with The Smallest Production ({})".format(T_con4))
            st.table(datasort_min[:1])
        with st.expander("Zero Production"):
            st.subheader("Country with Zero Production ({})".format(T_con4))
            st.markdown("Total: {} Countries".format(len(data_seleksi2)))
            st.table(data_seleksi2)
    #menampilkan tabel data produksi total
    with col_con4_2:
        st.subheader("(1971-2015) SUMMARY")
        with st.expander("Biggest Production"):
            st.subheader("Country with The Largest Total Production")
            st.table(data_total_produksi_terbesar[:1])
        with st.expander("Smallest Production"):
            st.subheader("Country with The Smallest Total Production")
            st.table(data_total_produksi_terkecil[data_total_produksi_terkecil["total_produksi"]>0][:1])
        with st.expander("Zero Production"):
            st.subheader("Country with Zero Total Production")
            st.markdown("Total: {} Countries".format(len(data_total_produksi[data_total_produksi["total_produksi"]==0])))
            st.table(data_total_produksi[data_total_produksi["total_produksi"]==0])
############### CONTAINER 4 ###############

###############  ###############
st.image(Image.open("bottom_image.png"))
###############  ###############