import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Pendaftaran Lomba", page_icon="📝")

st.title("📝 Form Pendaftaran Peserta")

# Tombol Kembali ke Home
st.page_link("app.py", label="**🏠 KEMBALI KE DASHBOARD UTAMA**", use_container_width=True)
st.divider()

# Koneksi ke database sheet Pendaftaran
conn = st.connection("gsheets", type=GSheetsConnection)
df_peserta = conn.read(worksheet="Pendaftaran", ttl=0)

# Blok form pendaftaran
with st.form("form_daftar", clear_on_submit=True):
    nama = st.text_input("Nama Peserta / Nama Tim (Khusus Voli)")
    lomba = st.selectbox("Pilih Kategori Lomba", [
        "Lomba Two Last Man Standing", 
        "Lomba Catwalk", 
        "Lomba Bola Voli", 
        "Lomba Karaoke", 
        "Lomba Costum"
    ])
    kontak = st.text_input("Nomor WhatsApp (Opsional)")
    
    submit_button = st.form_submit_button(label="Daftarkan Peserta!")

    if submit_button:
        if not nama:
            st.warning("Nama peserta atau nama tim wajib diisi!")
        else:
            waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data_baru = pd.DataFrame([{
                "Waktu Daftar": waktu_sekarang,
                "Nama Peserta/Tim": nama,
                "Kategori Lomba": lomba,
                "Kontak": kontak
            }])
            
            # Gabungkan dengan data yang sudah ada
            if df_peserta.empty:
                df_updated = data_baru
            else:
                df_updated = pd.concat([df_peserta, data_baru], ignore_index=True)
            
            # Simpan kembali (update) ke Google Sheets
            conn.update(worksheet="Pendaftaran", data=df_updated)
            st.success(f"Mantap! {nama} berhasil didaftarkan ke kategori {lomba}.")

st.divider()

st.subheader("📋 Daftar Peserta Terbaru")
# Tampilkan data langsung setelah input berhasil
df_terbaru = conn.read(worksheet="Pendaftaran", ttl=0)
st.dataframe(df_terbaru, use_container_width=True)
