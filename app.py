import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    layout="wide",
    page_title="Dashboard Statistik Regional Aceh",
    page_icon="📊"
)

# --- Custom CSS untuk Desain Premium dan Modern ---
st.markdown("""
<style>
    /* Hero Banner Utama untuk Judul */
    .hero-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 35px 20px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(30, 58, 138, 0.15);
        margin-bottom: 30px;
    }
    .hero-title {
        color: #FFFFFF !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        margin-bottom: 10px !important;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        color: #E0F2FE !important;
        font-size: 16px !important;
        margin: 0 !important;
        opacity: 0.9;
    }

    /* Subjudul Bagian - Rata Tengah dan Menarik */
    .section-header {
        text-align: center;
        color: #1E3A8A;
        font-size: 24px;
        font-weight: 700;
        margin-top: 35px;
        margin-bottom: 20px;
        padding-bottom: 8px;
    }

    /* Styling KPI Cards */
    .kpi-box {
        background-color: #FFFFFF;
        padding: 22px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
        border: 1px solid #E2E8F0;
        border-top: 6px solid #1E3A8A;
        text-align: center;
        transition: transform 0.2s;
    }
    .kpi-box:hover {
        transform: translateY(-2px);
    }
    .kpi-label {
        font-size: 13px;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .kpi-num {
        font-size: 32px;
        color: #0F172A;
        font-weight: 700;
        margin: 0;
    }

    /* Styling Kartu Peringkat (Ekstrem) */
    .ranking-box {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
        border: 1px solid #E2E8F0;
        height: 100%;
    }
    .ranking-header {
        font-size: 16px;
        font-weight: 700;
        color: #FFFFFF;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        text-align: center;
    }

    /* Kontainer Interpretasi Model */
    .insight-box {
        background-color: #F8FAFC;
        padding: 18px;
        border-radius: 10px;
        border-left: 4px solid #3B82F6;
        margin-top: 15px;
        font-size: 14px;
        color: #334155;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)


# --- 2. FUNGSI LOAD DATA (DENGAN CACHING & ROBUST PARSING) ---
@st.cache_data(ttl=600)
def load_data():
    sheet_id = "1VBeqi4OEmoDDQU5jOeZ2Jm5ois4M3YtAzY_rTcmiBSc"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()

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

        required_cols = ['Kabupaten/Kota', 'IPM', 'Kemiskinan (%)', 'TPT (%)']
        for col in required_cols:
            if col not in df.columns:
                st.error(f"Kolom penting '{col}' tidak berhasil dipetakan.")
                st.stop()

        df.dropna(subset=['Kabupaten/Kota'], inplace=True)
        df['Kabupaten/Kota'] = df['Kabupaten/Kota'].str.strip()

        for col in ['IPM', 'Kemiskinan (%)', 'TPT (%)']:
            df[col] = df[col].astype(str).str.replace('%', '').str.replace(',', '.').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(subset=['IPM', 'Kemiskinan (%)', 'TPT (%)'], inplace=True)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data. Detail Error: {e}")
        st.stop()

df_raw = load_data()


# --- 3. FILTER INTERAKTIF DI SIDEBAR ---
st.sidebar.header("⚙️ Filter & Navigasi")
st.sidebar.write("Gunakan opsi di bawah ini untuk menyaring data.")

daftar_daerah = sorted(df_raw['Kabupaten/Kota'].unique())

if 'selected_daerah' not in st.session_state:
    st.session_state['selected_daerah'] = []

selected_daerah = st.sidebar.multiselect(
    "Pilih Kabupaten/Kota:",
    options=daftar_daerah,
    default=st.session_state['selected_daerah'],
    key="daerah_filter"
)

if st.sidebar.button("🔄 Reset Filter"):
    st.session_state['daerah_filter'] = []
    st.rerun()

if selected_daerah:
    df_filtered = df_raw[df_raw['Kabupaten/Kota'].isin(selected_daerah)].copy()
else:
    df_filtered = df_raw.copy()


# --- 4. HERO BANNER HEADER ---
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">Dashboard Statistik Regional Dan Area Kecil Aceh</h1>
    <p class="hero-subtitle">Analisis Perbandingan Kondisi Pembangunan Antar Wilayah Berdasarkan IPM, Kemiskinan, dan Pengangguran</p>
</div>
""", unsafe_allow_html=True)

st.write(f"Menampilkan data untuk {len(df_filtered)} dari {len(df_raw)} Kabupaten/Kota di Provinsi Aceh")


# --- 5. INDIKATOR KINERJA UTAMA (KPI CARDS) ---
avg_ipm = df_filtered['IPM'].mean()
avg_kemiskinan = df_filtered['Kemiskinan (%)'].mean()
avg_tpt = df_filtered['TPT (%)'].mean()

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.markdown(f"""
    <div class="kpi-box">
        <p class="kpi-label">Rata-Rata IPM Aceh</p>
        <p class="kpi-num">{avg_ipm:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
    <div class="kpi-box" style="border-top-color: #EF4444;">
        <p class="kpi-label">Rata-Rata Kemiskinan</p>
        <p class="kpi-num">{avg_kemiskinan:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
    <div class="kpi-box" style="border-top-color: #F59E0B;">
        <p class="kpi-label">Rata-Rata TPT</p>
        <p class="kpi-num">{avg_tpt:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)


# --- 6. VISUALISASI RANKING (BAR CHARTS) ---
st.markdown("<p class='section-header'>📈 Urutan Dan Peringkat Indikator Pembangunan</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Indeks Pembangunan Manusia (IPM)", "Tingkat Kemiskinan (%)", "Tingkat Pengangguran Terbuka (TPT %)"])

# Konfigurasi Font Chart agar Serasi
chart_layout_config = dict(
    font=dict(family="sans-serif", size=12),
    margin=dict(l=50, r=30, t=40, b=40),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)"
)

with tab1:
    df_ipm_sorted = df_filtered.sort_values(by='IPM', ascending=True)
    fig_ipm = px.bar(
        df_ipm_sorted, x='IPM', y='Kabupaten/Kota', orientation='h', text='IPM',
        color='IPM', color_continuous_scale='Blues', height=600
    )
    fig_ipm.update_traces(texttemplate='%{text:.2f}', textposition='outside', marker_line_width=0)
    fig_ipm.update_layout(**chart_layout_config)
    fig_ipm.update_layout(yaxis_title="", xaxis_title="Indeks", coloraxis_showscale=False)
    st.plotly_chart(fig_ipm, use_container_width=True)

with tab2:
    df_kemiskinan_sorted = df_filtered.sort_values(by='Kemiskinan (%)', ascending=True)
    fig_kemiskinan = px.bar(
        df_kemiskinan_sorted, x='Kemiskinan (%)', y='Kabupaten/Kota', orientation='h', text='Kemiskinan (%)',
        color='Kemiskinan (%)', color_continuous_scale='Reds', height=600
    )
    fig_kemiskinan.update_traces(texttemplate='%{text:.2f}%', textposition='outside', marker_line_width=0)
    fig_kemiskinan.update_layout(**chart_layout_config)
    fig_kemiskinan.update_layout(yaxis_title="", xaxis_title="Persentase (%)", coloraxis_showscale=False)
    st.plotly_chart(fig_kemiskinan, use_container_width=True)

with tab3:
    df_tpt_sorted = df_filtered.sort_values(by='TPT (%)', ascending=True)
    fig_tpt = px.bar(
        df_tpt_sorted, x='TPT (%)', y='Kabupaten/Kota', orientation='h', text='TPT (%)',
        color='TPT (%)', color_continuous_scale='Oranges', height=600
    )
    fig_tpt.update_traces(texttemplate='%{text:.2f}%', textposition='outside', marker_line_width=0)
    fig_tpt.update_layout(**chart_layout_config)
    fig_tpt.update_layout(yaxis_title="", xaxis_title="Persentase (%)", coloraxis_showscale=False)
    st.plotly_chart(fig_tpt, use_container_width=True)


# --- 7. ANALISIS KORELASI (SCATTER PLOTS DENGAN REGRESI MANUAL) ---
st.markdown("<p class='section-header'>🔍 Analisis Hubungan Antar Indikator Regional</p>", unsafe_allow_html=True)

col_sc1, col_sc2 = st.columns(2)

def create_scatter_with_trendline(data, x_col, y_col, title, color_theme):
    x = data[x_col].values
    y = data[y_col].values
    m, c = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = m * x_line + c

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode='markers+text', text=data['Kabupaten/Kota'],
        textposition="top center", hoverinfo='text+x+y',
        marker=dict(size=11, color=color_theme, opacity=0.85, line=dict(width=1, color='#FFFFFF'))
    ))
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line, mode='lines',
        line=dict(color='#EF4444', width=2, dash='dash')
    ))
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center'),
        xaxis_title=x_col, yaxis_title=y_col,
        showlegend=False, height=450,
        plot_bgcolor="#F8FAFC", paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig, m, c

with col_sc1:
    fig_sc1, m1, c1 = create_scatter_with_trendline(df_filtered, 'IPM', 'Kemiskinan (%)', 'Korelasi Antara IPM Dan Tingkat Kemiskinan', '#1E3A8A')
    st.plotly_chart(fig_sc1, use_container_width=True)
    st.markdown(f"""
    <div class="insight-box">
        <strong>Model Analisis Linier:</strong><br>
        Persamaan Regresi: $y = {m1:.4f}x + {c1:.4f}$<br>
        Hubungan indikator bernilai negatif. Setiap kenaikan satu poin IPM berkontribusi pada penurunan kemiskinan sebesar {abs(m1):.2f}%. Peningkatan kapasitas manusia terbukti efektif mengurangi beban kemiskinan regional.
    </div>
    """, unsafe_allow_html=True)

with col_sc2:
    fig_sc2, m2, c2 = create_scatter_with_trendline(df_filtered, 'IPM', 'TPT (%)', 'Korelasi Antara IPM Dan Tingkat Pengangguran', '#EA580C')
    st.plotly_chart(fig_sc2, use_container_width=True)
    st.markdown(f"""
    <div class="insight-box" style="border-left-color: #EA580C;">
        <strong>Model Analisis Linier:</strong><br>
        Persamaan Regresi: $y = {m2:.4f}x + {c2:.4f}$<br>
        Arah tren kemiringan sebesar {m2:.4f} mencerminkan karakteristik penyerapan tenaga kerja terdidik di wilayah urban dengan karakteristik capaian IPM yang tinggi.
    </div>
    """, unsafe_allow_html=True)


# --- 8. KARTU INFORMASI DAERAH EKSTREM (TOP & BOTTOM) ---
st.markdown("<p class='section-header'>🏆 Sorotan Daerah Berkinerja Ekstrem</p>", unsafe_allow_html=True)

col_info1, col_info2, col_info3, col_info4 = st.columns(4)
top_ipm = df_filtered.nlargest(5, 'IPM')
bottom_ipm = df_filtered.nsmallest(5, 'IPM')
top_miskin = df_filtered.nlargest(5, 'Kemiskinan (%)')
top_tpt = df_filtered.nlargest(5, 'TPT (%)')

with col_info1:
    st.markdown('<div class="ranking-box">', unsafe_allow_html=True)
    st.markdown('<div class="ranking-header" style="background-color: #1E3A8A;">🌟 5 IPM Tertinggi</div>', unsafe_allow_html=True)
    for idx, row in top_ipm.iterrows():
        st.write(f"🏆 {row['Kabupaten/Kota']} ({row['IPM']:.2f})")
    st.markdown('</div>', unsafe_allow_html=True)

with col_info2:
    st.markdown('<div class="ranking-box">', unsafe_allow_html=True)
    st.markdown('<div class="ranking-header" style="background-color: #64748B;">⚠️ 5 IPM Terendah</div>', unsafe_allow_html=True)
    for idx, row in bottom_ipm.iterrows():
        st.write(f"🛑 {row['Kabupaten/Kota']} ({row['IPM']:.2f})")
    st.markdown('</div>', unsafe_allow_html=True)

with col_info3:
    st.markdown('<div class="ranking-box">', unsafe_allow_html=True)
    st.markdown('<div class="ranking-header" style="background-color: #EF4444;">🚨 5 Kemiskinan Tertinggi</div>', unsafe_allow_html=True)
    for idx, row in top_miskin.iterrows():
        st.write(f"🥀 {row['Kabupaten/Kota']} ({row['Kemiskinan (%)']:.2f}%)")
    st.markdown('</div>', unsafe_allow_html=True)

with col_info4:
    st.markdown('<div class="ranking-box">', unsafe_allow_html=True)
    st.markdown('<div class="ranking-header" style="background-color: #F59E0B;">💼 5 TPT Tertinggi</div>', unsafe_allow_html=True)
    for idx, row in top_tpt.iterrows():
        st.write(f"🔍 {row['Kabupaten/Kota']} ({row['TPT (%)']:.2f}%)")
    st.markdown('</div>', unsafe_allow_html=True)


# --- 9. TABEL DATA INTERAKTIF ---
st.markdown("<p class='section-header'>📋 Basis Data Regional Interaktif</p>", unsafe_allow_html=True)

st.dataframe(
    df_filtered,
    column_config={
        "Kabupaten/Kota": st.column_config.TextColumn("Nama Kabupaten / Kota"),
        "IPM": st.column_config.NumberColumn("Indeks Pembangunan Manusia", format="%.2f"),
        "Kemiskinan (%)": st.column_config.NumberColumn("Tingkat Kemiskinan", format="%.2f%%"),
        "TPT (%)": st.column_config.NumberColumn("Tingkat Pengangguran Terbuka", format="%.2f%%")
    },
    use_container_width=True,
    hide_index=True
)


# --- 10. RINGKASAN INSIGHT OTOMATIS ---
st.markdown("<p class='section-header'>🤖 Ringkasan Eksekutif Dan Sintesis Data</p>", unsafe_allow_html=True)

highest_ipm_row = df_filtered.loc[df_filtered['IPM'].idxmax()]
lowest_ipm_row = df_filtered.loc[df_filtered['IPM'].idxmin()]
highest_miskin_row = df_filtered.loc[df_filtered['Kemiskinan (%)'].idxmax()]
highest_tpt_row = df_filtered.loc[df_filtered['TPT (%)'].idxmax()]

st.info(f"""
Berikut Nilai Ekstrem Yang Teridentifikasi Berdasarkan Data Terpilih:
- Capaian Indeks Pembangunan Manusia tertinggi berada di wilayah {highest_ipm_row['Kabupaten/Kota']} senilai {highest_ipm_row['IPM']:.2f}.
- Capaian Indeks Pembangunan Manusia minimum berada di wilayah {lowest_ipm_row['Kabupaten/Kota']} senilai {lowest_ipm_row['IPM']:.2f}.
- Tingkat persentase kemiskinan tertinggi tercatat pada wilayah {highest_miskin_row['Kabupaten/Kota']} mencapai angka {highest_miskin_row['Kemiskinan (%)']:.2f}%.
- Tingkat pengangguran terbuka tertinggi didapatkan pada wilayah {highest_tpt_row['Kabupaten/Kota']} sebesar {highest_tpt_row['TPT (%)']:.2f}%.
""")


# --- 11. FOOTER ---
st.markdown("""
<div style="text-align: center; border-top: 1px solid #E2E8F0; padding-top: 20px; margin-top: 50px;">
    <p style="font-size: 13px; color: #64748B; margin: 0;">🏛️ Sumber Data Resmi: Badan Pusat Statistik Provinsi Aceh</p>
    <p style="font-size: 11px; color: #94A3B8; margin: 5px 0 0 0;">Dikembangkan Menggunakan Kerangka Kerja Python Dan Streamlit</p>
</div>
""", unsafe_allow_html=True)
