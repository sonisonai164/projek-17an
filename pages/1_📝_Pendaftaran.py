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

# --- SELECTBOX DI LUAR FORM (Biar bisa update tampilan secara real-time) ---
lomba = st.selectbox("Pilih Kategori Lomba", [
    "Lomba Two Last Man Standing", 
    "Lomba Catwalk", 
    "Lomba Bola Voli", 
    "Lomba Karaoke", 
    "Lomba Costum"
])

# Blok form pendaftaran
with st.form("form_daftar", clear_on_submit=True):
    
    # Logika dinamis: Jika Voli, beda form input-nya
    if lomba == "Lomba Bola Voli":
        nama_tampil = st.text_input("Nama Tim Voli", placeholder="Contoh: Tim Garuda Merah")
        anggota_tim = st.text_area("Daftar Anggota Tim (Nama-nama pemain)", placeholder="1. Budi (Captain)\n2. Joko\n3. Andi\n4. Rian")
        kontak = st.text_input("Nomor WhatsApp (Opsional)")
    else:
        nama_tampil = st.text_input("Nama Lengkap Peserta", placeholder="Contoh: Soni Abbasy")
        anggota_tim = "-" # Kosongkan untuk lomba individu
        kontak = st.text_input("Nomor WhatsApp (Opsional)")
    
    submit_button = st.form_submit_button(label="Daftarkan Sekarang!")

    if submit_button:
        if not nama_tampil:
            st.warning("Nama Peserta / Nama Tim wajib diisi, bro!")
        else:
            waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Jika Voli, kita gabungkan Nama Tim dan Anggotanya di database
            if lomba == "Lomba Bola Voli":
                final_nama = f"[TIM] {nama_tampil} (Anggota: {anggota_tim.replace(chr(10), ', ')})"
            else:
                final_nama = nama_tampil

            data_baru = pd.DataFrame([{
                "Waktu Daftar": waktu_sekarang,
                "Nama Peserta/Tim": final_nama,
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
            st.success(f"Mantap! Pendaftaran untuk **{nama_tampil}** berhasil disimpan.")

st.divider()

st.subheader("📋 Daftar Peserta Terbaru")
# Tampilkan data langsung setelah input berhasil
df_terbaru = conn.read(worksheet="Pendaftaran", ttl=600)
st.dataframe(df_terbaru, use_container_width=True)
