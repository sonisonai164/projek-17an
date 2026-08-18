import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Konfigurasi halaman (Wajib paling atas)
st.set_page_config(page_title="Dashboard 17-an", page_icon="🇮🇩", layout="wide")

# --- HEADER BERALA KEMERDEKAAN ---
st.markdown("<h1 style='text-align: center; color: #E51111;'>LINTAS SHUTTLE AGUSTUSAN</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Sistem Informasi Lomba 17 Agustusan 2026</h4>", unsafe_allow_html=True)
st.write("")

# --- TOMBOL NAVIGASI CEPAT ---
st.subheader("🚀 Menu Cepat")
col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    st.page_link("pages/1_📝_Pendaftaran.py", label="**PENDAFTARAN LOMBA**", icon="📝", use_container_width=True)
with col_nav2:
    st.page_link("pages/2_⚔️_Manajemen_Lomba.py", label="**MANAJEMEN LOMBA**", icon="⚔️", use_container_width=True)
with col_nav3:
    st.page_link("pages/3_🏆_Papan_Pemenang.py", label="**PAPAN PEMENANG**", icon="🏆", use_container_width=True)

st.divider()

try:
    # Memanggil Data
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_peserta = conn.read(worksheet="Pendaftaran", ttl=0)
    df_skor = conn.read(worksheet="Skor_Angka", ttl=0)
    df_status = conn.read(worksheet="Status_Tanding", ttl=0)
    
    if not df_peserta.empty:
        # Menghitung metrik
        total_peserta = len(df_peserta)
        total_kategori = df_peserta["Kategori Lomba"].nunique()
        
        # --- KARTU STATISTIK ---
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="👥 Total Keseluruhan", value=f"{total_peserta} Peserta/Tim")
        with col2:
            st.metric(label="🎯 Kategori Lomba Aktif", value=f"{total_kategori} Lomba")
        
        st.write("") # Memberi jarak kosong (spacer)
        st.divider()
        
        # --- TABEL INFORMASI (TANPA GRAFIK) ---
        col_rekap, col_terbaru = st.columns(2)
        
        with col_rekap:
            st.subheader("📌 Rekap per Kategori")
            # Hitung jumlah peserta per lomba
            rekap = df_peserta["Kategori Lomba"].value_counts().reset_index()
            rekap.columns = ["Kategori Lomba", "Jumlah Pendaftar"]
            st.dataframe(rekap, hide_index=True, use_container_width=True)
            
        with col_terbaru:
            st.subheader("🆕 5 Pendaftar Terbaru")
            # Mengambil 5 data pendaftar terakhir
            df_terbaru = df_peserta.tail(5)[["Waktu Daftar", "Nama Peserta/Tim", "Kategori Lomba"]]
            # Urutkan dari yang paling baru
            df_terbaru = df_terbaru.sort_values(by="Waktu Daftar", ascending=False)
            st.dataframe(df_terbaru, hide_index=True, use_container_width=True)
            
        st.divider()
        
        # --- HIGHLIGHT PEMENANG & LOLOS BABAK ---
        st.subheader("🏆 Highlight Pemenang & Status Lolos Babak")
        st.write("Pantau peringkat pertama sementara dan peserta yang berhasil lolos ke babak selanjutnya.")
        
        # Bikin 2 Tab biar rapi
        tab_skor, tab_status = st.tabs(["🥇 Peringkat 1 Sementara (Skor)", "⚔️ Lolos Babak / Juara (Eliminasi)"])
        
        with tab_skor:
            if not df_skor.empty:
                # Pastikan total skor terbaca sebagai angka
                df_skor["Total Skor"] = pd.to_numeric(df_skor["Total Skor"], errors='coerce')
                # Urutkan dari terbesar, lalu ambil HANYA 1 orang teratas di tiap kategori
                top_skor = df_skor.sort_values("Total Skor", ascending=False).drop_duplicates(["Kategori"])
                top_skor = top_skor[["Kategori", "Nama Peserta", "Total Skor"]].reset_index(drop=True)
                top_skor.index += 1
                
                # Format biar nggak ada .0 di belakang
                styled_top = top_skor.style.format(subset=["Total Skor"], formatter="{:.0f}")
                st.dataframe(styled_top, use_container_width=True)
            else:
                st.info("Belum ada data nilai juri yang masuk.")
                
        with tab_status:
            if not df_status.empty:
                # Filter hanya yang Lanjut atau Juara
                df_lolos = df_status[df_status["Status"].isin(["Lanjut (Menang Babak)", "Juara!"])].reset_index(drop=True)
                
                if not df_lolos.empty:
                    df_lolos = df_lolos[["Kategori", "Nama Peserta/Tim", "Status", "Skor Voli"]]
                    
                    # Bersihkan angka nol pada Skor Voli (jika ada)
                    if "Skor Voli" in df_lolos.columns:
                        df_lolos["Skor Voli"] = df_lolos["Skor Voli"].astype(str).str.replace(r'\.0$', '', regex=True)
                        df_lolos["Skor Voli"] = df_lolos["Skor Voli"].replace({'nan': '-', 'None': '-', '': '-'})
                    
                    df_lolos.index += 1
                    st.dataframe(df_lolos, use_container_width=True)
                else:
                    st.info("Belum ada peserta yang di-update statusnya menjadi Lanjut atau Juara.")
            else:
                st.info("Belum ada data pertandingan yang masuk.")
                
    else:
        st.info("Belum ada peserta yang terdaftar di database. Ayo sebar link pendaftarannya, panitia!")
        
except Exception as e:
    st.warning(f"Menunggu konfigurasi database. Error: {e}")
    
st.divider()
st.caption("© Dibuat dengan semangat 45 oleh Panitia Lomba.")
