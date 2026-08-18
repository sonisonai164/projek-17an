import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Papan Pemenang", page_icon="🏆")

st.title("🏆 Leaderboard & Papan Pemenang")
st.write("Tabel ini secara otomatis mengurutkan peserta dari posisi atau nilai tertinggi. Baris berwarna hijau adalah pemuncak klasemen saat ini!")

# Tombol Kembali ke Home
st.page_link("app.py", label="**🏠 KEMBALI KE DASHBOARD UTAMA**", use_container_width=True)
st.divider()

# Fungsi untuk memberi warna baris Juara 1 (Baris dengan index 1)
def highlight_juara(baris):
    if baris.name == 1: 
        return ['background-color: #198754; color: white'] * len(baris)
    else:
        return [''] * len(baris)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_skor = conn.read(worksheet="Skor_Angka", ttl=0)
    df_status = conn.read(worksheet="Status_Tanding", ttl=0)
    
    st.header("Kategori Penilaian Skor (Juara 1, 2, 3)")
    if not df_skor.empty:
        lomba_skor = df_skor["Kategori"].unique()
        for lomba in lomba_skor:
            st.subheader(f"🥇 {lomba}")
            
            # Urutkan berdasarkan Total Skor dari tinggi ke rendah
            df_filter = df_skor[df_skor["Kategori"] == lomba].sort_values(by="Total Skor", ascending=False).reset_index(drop=True)
            df_filter.index += 1  # Indeks mulai dari 1
            
            # Paksa urutan kolom
            urutan_kolom = ["Nama Peserta", "Kategori", "Nilai Juri 1", "Nilai Juri 2", "Nilai Juri 3", "Total Skor"]
            kolom_tersedia = [kolom for kolom in urutan_kolom if kolom in df_filter.columns]
            df_filter = df_filter[kolom_tersedia]

            # Bersihkan angka nol desimal
            kolom_angka = [c for c in ["Nilai Juri 1", "Nilai Juri 2", "Nilai Juri 3", "Total Skor"] if c in df_filter.columns]
            for col in kolom_angka:
                df_filter[col] = pd.to_numeric(df_filter[col], errors='coerce')

            # Terapkan warna hijau dan format angka
            styled_df = df_filter.style.apply(highlight_juara, axis=1).format(
                subset=kolom_angka,
                formatter="{:.0f}",
                na_rep="-"
            )
            
            st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("Belum ada data nilai yang masuk.")

    st.divider()

    st.header("Kategori Sistem Gugur & Voli")
    if not df_status.empty:
        lomba_status = df_status["Kategori"].unique()
        for lomba in lomba_status:
            st.subheader(f"⚔️ {lomba}")
            
            # Urutkan berdasarkan alfabetik status (Juara akan muncul lebih dulu)
            df_filter = df_status[df_status["Kategori"] == lomba].sort_values(by="Status", ascending=False).reset_index(drop=True)
            df_filter.index += 1
            
            # Bersihkan Skor Voli
            if "Skor Voli" in df_filter.columns:
                df_filter["Skor Voli"] = df_filter["Skor Voli"].astype(str)
                df_filter["Skor Voli"] = df_filter["Skor Voli"].str.replace(r'\.0$', '', regex=True)
                df_filter["Skor Voli"] = df_filter["Skor Voli"].replace({'nan': '-', 'None': '-', '': '-'})
            
            # Terapkan warna hijau untuk baris teratas (Juara)
            styled_df = df_filter.style.apply(highlight_juara, axis=1)
            
            st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("Belum ada data status pertandingan yang masuk.")

except Exception as e:
    st.error(f"Gagal memuat data. Pastikan database siap. Detail Error: {e}")