import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Manajemen Lomba", page_icon="⚔️")

st.title("⚔️ Manajemen & Penilaian Lomba")

# Tombol Kembali ke Home
st.page_link("app.py", label="**🏠 KEMBALI KE DASHBOARD UTAMA**", use_container_width=True)
st.divider()

# Tarik semua data dari database
conn = st.connection("gsheets", type=GSheetsConnection)
df_peserta = conn.read(worksheet="Pendaftaran", ttl=600)
df_skor = conn.read(worksheet="Skor_Angka", ttl=600)
df_status = conn.read(worksheet="Status_Tanding", ttl=600)

if df_peserta.empty:
    st.warning("Belum ada peserta yang mendaftar di database.")
    st.stop()

# Pilih lomba dan filter pesertanya
lomba_pilihan = st.selectbox("Pilih Lomba yang sedang berjalan:", df_peserta["Kategori Lomba"].unique())
peserta_lomba = df_peserta[df_peserta["Kategori Lomba"] == lomba_pilihan]["Nama Peserta/Tim"].tolist()

if not peserta_lomba:
    st.info("Belum ada peserta di kategori ini.")
    st.stop()

peserta_pilihan = st.selectbox("Pilih Peserta/Tim untuk dinilai:", peserta_lomba)

# Pengelompokan tipe lomba
lomba_skor = ["Lomba Karaoke", "Lomba Catwalk", "Lomba Costum"]
lomba_status = ["Lomba Two Last Man Standing", "Lomba Bola Voli"]

# 1. Logika untuk Lomba Sistem Skor
if lomba_pilihan in lomba_skor:
    st.subheader(f"Input Nilai Juri untuk {peserta_pilihan}")
    
    with st.form("form_skor", clear_on_submit=False):
        juri_1 = st.number_input("Nilai Juri 1 (0-100)", min_value=0, max_value=100)
        juri_2 = st.number_input("Nilai Juri 2 (0-100)", min_value=0, max_value=100)
        
        # Logika khusus Lomba Catwalk memunculkan Juri 3
        if lomba_pilihan == "Lomba Catwalk":
            juri_3 = st.number_input("Nilai Juri 3 (0-100)", min_value=0, max_value=100)
        else:
            juri_3 = 0  # Default 0 untuk lomba lain yang hanya 2 juri
            
        submit_skor = st.form_submit_button("Simpan Skor")
        
        if submit_skor:
            # Hitung total
            total_skor = juri_1 + juri_2 + juri_3
            
            # Siapkan data untuk disimpan (Format disesuaikan jika Catwalk atau bukan)
            nilai_juri_3_simpan = juri_3 if lomba_pilihan == "Lomba Catwalk" else ""
            
            data_skor_baru = pd.DataFrame([{
                "Nama Peserta": peserta_pilihan,
                "Kategori": lomba_pilihan,
                "Nilai Juri 1": juri_1,
                "Nilai Juri 2": juri_2,
                "Nilai Juri 3": nilai_juri_3_simpan,
                "Total Skor": total_skor
            }])
            
            # Timpa data peserta jika sudah pernah dinilai sebelumnya, atau tambah baru
            if df_skor.empty:
                df_skor_updated = data_skor_baru
            else:
                df_skor_updated = df_skor[df_skor["Nama Peserta"] != peserta_pilihan]
                df_skor_updated = pd.concat([df_skor_updated, data_skor_baru], ignore_index=True)
            
            conn.update(worksheet="Skor_Angka", data=df_skor_updated)
            st.success(f"Skor untuk {peserta_pilihan} berhasil disimpan! (Total: {total_skor})")

# 2. Logika untuk Lomba Sistem Eliminasi / Voli
elif lomba_pilihan in lomba_status:
    st.subheader(f"Update Status Pertandingan untuk {peserta_pilihan}")
    with st.form("form_status", clear_on_submit=False):
        status = st.radio("Status Peserta/Tim:", ["Lanjut (Menang Babak)", "Gugur", "Juara!"])
        skor_voli = st.text_input("Skor Pertandingan (Khusus Voli, opsional. Contoh: 25-21)")
        submit_status = st.form_submit_button("Update Status")
        
        if submit_status:
            data_status_baru = pd.DataFrame([{
                "Nama Peserta/Tim": peserta_pilihan,
                "Kategori": lomba_pilihan,
                "Status": status,
                "Skor Voli": skor_voli
            }])
            
            if df_status.empty:
                df_status_updated = data_status_baru
            else:
                df_status_updated = df_status[df_status["Nama Peserta/Tim"] != peserta_pilihan]
                df_status_updated = pd.concat([df_status_updated, data_status_baru], ignore_index=True)
            
            conn.update(worksheet="Status_Tanding", data=df_status_updated)
            st.success(f"Status {peserta_pilihan} berhasil diupdate menjadi '{status}'!")
