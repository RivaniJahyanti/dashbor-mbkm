import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
# Mengatur layout menjadi wide (lebar) dan memberikan judul pada tab browser
st.set_page_config(
    layout="wide",
    page_title="Dashboard Statistik Regional Aceh",
    page_icon="📊"
)

# --- Custom CSS untuk Mempercantik Tampilan (Nuansa Biru Profesional) ---
st.markdown("""
<style>
    /* Styling untuk KPI Cards */
    .kpi-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #1E3A8A; /* Biru Gelap */
        margin-bottom: 10px;
    }
    .kpi-title {
        font-size: 14px;
        color: #4B5563;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 28px;
        color: #1E3A8A;
        font-weight: 700;
        margin: 0;
    }

    /* Styling untuk Kartu Top/Bottom */
    .rank-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #E5E7EB;
        height: 100%;
    }
    .rank-title {
        font-size: 15px;
        font-weight: bold;
        color: #1F2937;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }

    /* Styling untuk Blok Interpretasi */
    .interpretasi-container {
        background-color: #EFF6FF;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
        margin-top: 10px;
        font-size: 13.5px;
        color: #1E40AF;
    }
</style>
""", unsafe_allow_html=True)


# --- 2. FUNGSI LOAD DATA (DENGAN CACHING & ROBUST PARSING) ---
@st.cache_data(ttl=600) # Simpan cache selama 10 menit
def load_data():
    """
    Mengunduh data secara langsung dari Google Spreadsheet publik
    dan membersihkan struktur kolom serta tipe datanya.
    """
    sheet_id = "1VBeqi4OEmoDDQU5jOeZ2Jm5ois4M3YtAzY_rTcmiBSc"
    # Menggunakan format ekspor CSV resmi dari Google Drive API
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

    try:
        df = pd.read_csv(url)

        # Bersihkan spasi berlebih pada nama kolom
        df.columns = df.columns.str.strip()

        # Pemetaan kolom secara cerdas untuk mencocokkan kolom di spreadsheet Anda
        col_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'kabupaten' in col_lower or 'kota' in col_lower or 'daerah' in col_lower:
                col_mapping[col] = 'Kabupaten/Kota'
            elif 'ipm' in col_lower:
                col_mapping[col] = 'IPM'
            elif 'kemiskinan' in col_lower or 'penduduk miskin' in col_lower or 'miskin' in col_lower:
                col_mapping[col] = 'Kemiskinan (%)'
            elif 'tpt' in col_lower or 'pengangguran' in col_lower:
                col_mapping[col] = 'TPT (%)'

        df.rename(columns=col_mapping, inplace=True)

        # Validasi ketersediaan kolom utama yang sudah dipetakan
        required_cols = ['Kabupaten/Kota', 'IPM', 'Kemiskinan (%)', 'TPT (%)']
        for col in required_cols:
            if col not in df.columns:
                st.error(f"Kolom penting '{col}' tidak berhasil dipetakan dari dokumen spreadsheet.")
                st.stop()

        # Hapus baris kosong dan bersihkan data numerik
        df.dropna(subset=['Kabupaten/Kota'], inplace=True)
        df['Kabupaten/Kota'] = df['Kabupaten/Kota'].str.strip()

        for col in ['IPM', 'Kemiskinan (%)', 'TPT (%)']:
            # Bersihkan simbol persen, ganti koma desimal ke titik desimal, dan ubah ke numeric
            df[col] = df[col].astype(str).str.replace('%', '').str.replace(',', '.').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Hapus baris yang memiliki nilai NaN pada statistik utama
        df.dropna(subset=['IPM', 'Kemiskinan (%)', 'TPT (%)'], inplace=True)

        return df
    except Exception as e:
        st.error(f"Gagal memuat data dari Google Sheets. Pastikan link aktif dan setelan berbagi diatur ke publik. Detail Error: {e}")
        st.stop()


# Load data awal
df_raw = load_data()


# --- 3. FILTER INTERAKTIF DI SIDEBAR ---
st.sidebar.header("⚙️ Filter & Navigasi")
st.sidebar.write("Gunakan opsi di bawah ini untuk menyaring tampilan data pada dashboard.")

# Ambil daftar unik Kabupaten/Kota untuk opsi filter
daftar_daerah = sorted(df_raw['Kabupaten/Kota'].unique())

# Multiselect untuk memilih daerah
if 'selected_daerah' not in st.session_state:
    st.session_state['selected_daerah'] = []

selected_daerah = st.sidebar.multiselect(
    "Pilih Kabupaten/Kota:",
    options=daftar_daerah,
    default=st.session_state['selected_daerah'],
    key="daerah_filter"
)

# Tombol Reset Filter
if st.sidebar.button("🔄 Reset Filter"):
    st.session_state['daerah_filter'] = []
    st.rerun()

# Logika Filter: Jika kosong, maka tampilkan semua data
if selected_daerah:
    df_filtered = df_raw[df_raw['Kabupaten/Kota'].isin(selected_daerah)].copy()
else:
    df_filtered = df_raw.copy()


# --- 4. HEADER DASHBOARD ---
st.markdown("<h1 style='text-align: center; color: #1E3A8A; margin-bottom: 5px;'>📊 Dashboard Statistik Regional dan Area Kecil Aceh</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4B5563; font-size: 16px; margin-bottom: 25px;'>Analisis Perbandingan Kondisi Pembangunan Antar Wilayah berdasarkan IPM, Kemiskinan, dan Tingkat Pengangguran Terbuka (TPT)</p>", unsafe_allow_html=True)

# Menampilkan informasi total daerah terfilter
st.markdown(f"**Menampilkan data untuk {len(df_filtered)} dari {len(df_raw)} Kabupaten/Kota di Aceh**")
st.markdown("---")


# --- 5. INDIKATOR KINERJA UTAMA (KPI CARDS) ---
# Menghitung nilai rata-rata dari data terfilter
avg_ipm = df_filtered['IPM'].mean()
avg_kemiskinan = df_filtered['Kemiskinan (%)'].mean()
avg_tpt = df_filtered['TPT (%)'].mean()

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.markdown(f"""
    <div class="kpi-container">
        <p class="kpi-title">RATA-RATA IPM ACEH</p>
        <p class="kpi-value">{avg_ipm:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
    <div class="kpi-container" style="border-left-color: #EF4444;">
        <p class="kpi-title">RATA-RATA KEMISKINAN (%)</p>
        <p class="kpi-value">{avg_kemiskinan:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
    <div class="kpi-container" style="border-left-color: #F59E0B;">
        <p class="kpi-title">RATA-RATA TPT (%)</p>
        <p class="kpi-value">{avg_tpt:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- 6. VISUALISASI RANKING (BAR CHARTS) ---
st.markdown("<h3 style='color: #1E3A8A;'>📈 Urutan & Peringkat Indikator Pembangunan</h3>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Indeks Pembangunan Manusia (IPM)", "🛑 Tingkat Kemiskinan (%)", "💼 Tingkat Pengangguran Terbuka (TPT %)"])

with tab1:
    # Mengurutkan data berdasarkan IPM tertinggi ke terendah
    df_ipm_sorted = df_filtered.sort_values(by='IPM', ascending=True) # Ascending True agar bar chart horizontal terurut rapi dari atas ke bawah
    fig_ipm = px.bar(
        df_ipm_sorted,
        x='IPM',
        y='Kabupaten/Kota',
        orientation='h',
        text='IPM',
        title='Peringkat Indeks Pembangunan Manusia (IPM) per Kabupaten/Kota',
        color='IPM',
        color_continuous_scale='Blues',
        height=600
    )
    fig_ipm.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_ipm.update_layout(yaxis_title="", xaxis_title="Indeks", coloraxis_showscale=False)
    st.plotly_chart(fig_ipm, use_container_width=True)

with tab2:
    # Mengurutkan data berdasarkan Kemiskinan tertinggi ke terendah
    df_kemiskinan_sorted = df_filtered.sort_values(by='Kemiskinan (%)', ascending=True)
    fig_kemiskinan = px.bar(
        df_kemiskinan_sorted,
        x='Kemiskinan (%)',
        y='Kabupaten/Kota',
        orientation='h',
        text='Kemiskinan (%)',
        title='Persentase Tingkat Kemiskinan per Kabupaten/Kota',
        color='Kemiskinan (%)',
        color_continuous_scale='Reds',
        height=600
    )
    fig_kemiskinan.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_kemiskinan.update_layout(yaxis_title="", xaxis_title="Persentase (%)", coloraxis_showscale=False)
    st.plotly_chart(fig_kemiskinan, use_container_width=True)

with tab3:
    # Mengurutkan data berdasarkan TPT tertinggi ke terendah
    df_tpt_sorted = df_filtered.sort_values(by='TPT (%)', ascending=True)
    fig_tpt = px.bar(
        df_tpt_sorted,
        x='TPT (%)',
        y='Kabupaten/Kota',
        orientation='h',
        text='TPT (%)',
        title='Tingkat Pengangguran Terbuka (TPT) per Kabupaten/Kota',
        color='TPT (%)',
        color_continuous_scale='Oranges',
        height=600
    )
    fig_tpt.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_tpt.update_layout(yaxis_title="", xaxis_title="Persentase (%)", coloraxis_showscale=False)
    st.plotly_chart(fig_tpt, use_container_width=True)

st.markdown("---")


# --- 7. ANALISIS KORELASI (SCATTER PLOTS DENGAN REGRESI MANUAL) ---
st.markdown("<h3 style='color: #1E3A8A;'>🔍 Analisis Hubungan Antar Indikator</h3>", unsafe_allow_html=True)

col_sc1, col_sc2 = st.columns(2)

# Fungsi pembantu untuk membuat scatter plot beserta trendline manual
def create_scatter_with_trendline(data, x_col, y_col, title, color_theme):
    x = data[x_col].values
    y = data[y_col].values

    # Hitung koefisien regresi linier secara manual menggunakan numpy polyfit
    m, c = np.polyfit(x, y, 1)

    # Generate nilai x untuk trendline dan hitung nilai y prediksinya
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = m * x_line + c

    # Membuat figure kosong
    fig = go.Figure()

    # Tambahkan marker data utama
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers+text',
        text=data['Kabupaten/Kota'],
        textposition="top center",
        hoverinfo='text+x+y',
        name='Daerah',
        marker=dict(size=12, color=color_theme, opacity=0.8, line=dict(width=1, color='DarkSlateGrey'))
    ))

    # Tambahkan garis trendline regresi
    fig.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode='lines',
        name='Garis Tren',
        line=dict(color='red', width=2, dash='dash')
    ))

    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title=y_col,
        showlegend=False,
        height=500,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig, m, c

with col_sc1:
    fig_sc1, m1, c1 = create_scatter_with_trendline(
        df_filtered, 'IPM', 'Kemiskinan (%)',
        'Korelasi IPM vs Kemiskinan', '#1D4ED8'
    )
    st.plotly_chart(fig_sc1, use_container_width=True)

    # Format formula matematika menggunakan sintaks LaTeX
    st.markdown(f"""
    <div class="interpretasi-container">
        <strong>Interpretasi Model Matematika:</strong><br>
        Persamaan Regresi Linier: $y = {m1:.4f}x + {c1:.4f}$<br>
        Hubungan antara IPM and Kemiskinan bersifat <strong>negatif</strong>.
        Setiap peningkatan $1$ poin IPM secara teoritis akan menurunkan tingkat kemiskinan sebesar ${abs(m1):.2f}\%$.
        Ini membuktikan bahwa kualitas pembangunan manusia yang lebih baik berbanding lurus dengan berkurangnya kemiskinan regional.
    </div>
    """, unsafe_allow_html=True)

with col_sc2:
    fig_sc2, m2, c2 = create_scatter_with_trendline(
        df_filtered, 'IPM', 'TPT (%)',
        'Korelasi IPM vs Tingkat Pengangguran Terbuka (TPT)', '#EA580C'
    )
    st.plotly_chart(fig_sc2, use_container_width=True)

    st.markdown(f"""
    <div class="interpretasi-container" style="border-left-color: #EA580C; background-color: #FFF7ED; color: #9A3412;">
        <strong>Interpretasi Model Matematika:</strong><br>
        Persamaan Regresi Linier: $y = {m2:.4f}x + {c2:.4f}$<br>
        Hubungan antara IPM dan TPT menunjukkan kecenderungan yang dipengaruhi oleh struktur ekonomi daerah.
        Koefisien kemiringan (slope) sebesar ${m2:.4f}$ menggambarkan arah elastisitas penyediaan lapangan kerja bagi kelompok penduduk berpendidikan menengah ke atas yang mendominasi kelompok pencari kerja ber-IPM tinggi.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# --- 8. KARTU INFORMASI DAERAH EKSTREM (TOP & BOTTOM) ---
st.markdown("<h3 style='color: #1E3A8A;'>🏆 Sorotan Daerah Berkinerja Ekstrem (Top 5)</h3>", unsafe_allow_html=True)

col_info1, col_info2, col_info3, col_info4 = st.columns(4)

# Ambil data top dan bottom
top_ipm = df_filtered.nlargest(5, 'IPM')
bottom_ipm = df_filtered.nsmallest(5, 'IPM')
top_miskin = df_filtered.nlargest(5, 'Kemiskinan (%)')
top_tpt = df_filtered.nlargest(5, 'TPT (%)')

with col_info1:
    st.markdown('<div class="rank-card">', unsafe_allow_html=True)
    st.markdown('<div class="rank-title" style="border-bottom-color: #1E3A8A;">🌟 5 IPM Tertinggi</div>', unsafe_allow_html=True)
    for index, row in top_ipm.iterrows():
        st.write(f"🏆 **{row['Kabupaten/Kota']}** ({row['IPM']:.2f})")
    st.markdown('</div>', unsafe_allow_html=True)

with col_info2:
    st.markdown('<div class="rank-card">', unsafe_allow_html=True)
    st.markdown('<div class="rank-title" style="border-bottom-color: #6B7280;">⚠️ 5 IPM Terendah</div>', unsafe_allow_html=True)
    for index, row in bottom_ipm.iterrows():
        st.write(f"🛑 **{row['Kabupaten/Kota']}** ({row['IPM']:.2f})")
    st.markdown('</div>', unsafe_allow_html=True)

with col_info3:
    st.markdown('<div class="rank-card">', unsafe_allow_html=True)
    st.markdown('<div class="rank-title" style="border-bottom-color: #EF4444;">🚨 5 Kemiskinan Tertinggi</div>', unsafe_allow_html=True)
    for index, row in top_miskin.iterrows():
        st.write(f"🥀 **{row['Kabupaten/Kota']}** ({row['Kemiskinan (%)']:.2f}%)")
    st.markdown('</div>', unsafe_allow_html=True)

with col_info4:
    st.markdown('<div class="rank-card">', unsafe_allow_html=True)
    st.markdown('<div class="rank-title" style="border-bottom-color: #F59E0B;">💼 5 TPT Tertinggi</div>', unsafe_allow_html=True)
    for index, row in top_tpt.iterrows():
        st.write(f"🔍 **{row['Kabupaten/Kota']}** ({row['TPT (%)']:.2f}%)")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- 9. TABEL DATA INTERAKTIF ---
st.markdown("<h3 style='color: #1E3A8A;'>📋 Dataset Interaktif</h3>", unsafe_allow_html=True)
st.markdown("Gunakan tabel di bawah ini untuk mencari, menyaring, dan mengurutkan data mentah Kabupaten/Kota.")

# Konfigurasi penyajian data menggunakan streamlit dataframe container penuh
st.dataframe(
    df_filtered,
    column_config={
        "Kabupaten/Kota": st.column_config.TextColumn("Nama Kabupaten/Kota"),
        "IPM": st.column_config.NumberColumn("Indeks Pembangunan Manusia", format="%.2f"),
        "Kemiskinan (%)": st.column_config.NumberColumn("Tingkat Kemiskinan", format="%.2f%%"),
        "TPT (%)": st.column_config.NumberColumn("Tingkat Pengangguran Terbuka", format="%.2f%%")
    },
    use_container_width=True,
    hide_index=True
)

st.markdown("---")


# --- 10. RINGKASAN INSIGHT OTOMATIS ---
st.markdown("<h3 style='color: #1E3A8A;'>🤖 Ringkasan Eksekutif & Sintesis Data</h3>", unsafe_allow_html=True)

# Ekstraksi nilai tertinggi dan terendah dinamis berdasarkan filter
highest_ipm_row = df_filtered.loc[df_filtered['IPM'].idxmax()]
lowest_ipm_row = df_filtered.loc[df_filtered['IPM'].idxmin()]
highest_miskin_row = df_filtered.loc[df_filtered['Kemiskinan (%)'].idxmax()]
highest_tpt_row = df_filtered.loc[df_filtered['TPT (%)'].idxmax()]

st.info(f"""
Berikut adalah sintesis temuan utama dari kondisi pembangunan daerah berdasarkan data terpilih:
* 🌟 **IPM Tertinggi** diraih oleh **{highest_ipm_row['Kabupaten/Kota']}** dengan nilai indeks **{highest_ipm_row['IPM']:.2f}**.
* 🛑 **IPM Terendah** tercatat pada **{lowest_ipm_row['Kabupaten/Kota']}** dengan nilai indeks **{lowest_ipm_row['IPM']:.2f}**.
* 🥀 **Tingkat Kemiskinan Tertinggi** berada di **{highest_miskin_row['Kabupaten/Kota']}** yang menyentuh angka **{highest_miskin_row['Kemiskinan (%)']:.2f}%**.
* 💼 **Tingkat Pengangguran Terbuka (TPT) Tertinggi** dilaporkan di **{highest_tpt_row['Kabupaten/Kota']}** yaitu sebesar **{highest_tpt_row['TPT (%)']:.2f}%**.
""")

st.markdown("<br><br>", unsafe_allow_html=True)


# --- 11. FOOTER DASHBOARD ---
st.markdown("""
<div style="text-align: center; border-top: 1px solid #E5E7EB; padding-top: 15px; margin-top: 50px;">
    <p style="font-size: 13px; color: #6B7280; margin: 0;">🏛️ Sumber Data: Badan Pusat Statistik (BPS) Provinsi Aceh</p>
    <p style="font-size: 11px; color: #9CA3AF; margin: 5px 0 0 0;">Dibuat secara profesional menggunakan Python & Streamlit Community Cloud</p>
</div>
""", unsafe_allow_html=True)
