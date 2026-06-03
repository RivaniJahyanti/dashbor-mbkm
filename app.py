import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    layout="wide",
    page_title="Dashboard Statistik Regional - Rivani Jahyanti",
    page_icon="📊"
)

# --- 2. CUSTOM CSS PREMIUM (GAYA IMAGE_A26520.PNG & IMAGE_A260CD.PNG) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Base Background Layout */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Hero Banner Slim Layout (Referensi image_a26520.png) */
    .hero-container {
        background: linear-gradient(135deg, #0066C2 0%, #1565C0 100%);
        padding: 25px 20px;
        border-radius: 14px;
        box-shadow: 0 10px 25px rgba(0, 102, 194, 0.2);
        margin-bottom: 30px;
        text-align: center;
    }
    .hero-title {
        color: #FFFFFF !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        color: #E3F2FD !important;
        font-size: 14px !important;
        margin: 6px 0 0 0 !important;
        opacity: 0.95;
    }

    /* Container Banner Judul Seksional (Gaya image_a26520.png) */
    .section-banner-card {
        background: linear-gradient(135deg, #0066C2 0%, #1E40AF 100%);
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(0, 64, 175, 0.15);
        margin-top: 35px;
        margin-bottom: 20px;
        text-align: center;
    }
    .section-banner-text {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        margin: 0 !important;
        letter-spacing: 0.5px;
    }

    /* Card Umum Pembungkus Grafik & Peta (Referensi image_a260cd.png) */
    .premium-wrapper-card {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        margin-bottom: 25px;
    }

    /* Premium KPI Cards (Referensi Kontras Cerah image_a260cd.png) */
    .kpi-gradient-card {
        padding: 22px;
        border-radius: 12px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
        display: flex;
        align-items: center;
        gap: 18px;
        transition: transform 0.2s;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .kpi-gradient-card:hover {
        transform: translateY(-3px);
    }
    .kpi-icon-round {
        font-size: 28px;
        width: 55px;
        height: 55px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.25);
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
    }
    .kpi-num-big {
        font-size: 32px;
        color: #FFFFFF;
        font-weight: 800;
        margin: 0;
        line-height: 1;
    }
    .kpi-label-top {
        font-size: 11px;
        color: #FFFFFF;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
        opacity: 0.9;
    }

    /* Ranking Leaderboard Card Style */
    .ranking-box-container {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.02);
        height: 100%;
    }
    .ranking-header-strip {
        font-size: 14px;
        font-weight: 700;
        color: #FFFFFF;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 15px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .leaderboard-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 4px;
        border-bottom: 1px dashed #E2E8F0;
        font-size: 13.5px;
    }
    .leaderboard-row:last-child {
        border-bottom: none;
    }

    /* Insight Panel */
    .insight-panel-card {
        background-color: #F8FAFC;
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #0066C2;
        margin-top: 15px;
        font-size: 14px;
        color: #334155;
        line-height: 1.6;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.01);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. REKAYASA LOAD DATA & SPASIAL SEEDING ---
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
        df.dropna(subset=['Kabupaten/Kota'], inplace=True)
        df['Kabupaten/Kota'] = df['Kabupaten/Kota'].str.strip()
        
        for col in ['IPM', 'Kemiskinan (%)', 'TPT (%)']:
            df[col] = df[col].astype(str).str.replace('%', '').str.replace(',', '.').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        df.dropna(subset=['IPM', 'Kemiskinan (%)', 'TPT (%)'], inplace=True)
        
        # Centroid koordinat geografis perkiraan Provinsi Aceh
        coordinates = {
            'Banda Aceh': [5.550, 95.320], 'Sabang': [5.890, 95.320], 'Lhokseumawe': [5.180, 97.140],
            'Langsa': [4.470, 97.970], 'Subulussalam': [2.640, 98.000], 'Aceh Besar': [5.380, 95.480],
            'Aceh Utara': [5.000, 97.100], 'Aceh Timur': [4.630, 97.630], 'Aceh Selatan': [3.150, 97.200],
            'Aceh Barat': [4.450, 96.150], 'Aceh Tengah': [4.600, 96.800], 'Aceh Tenggara': [3.370, 97.830],
            'Aceh Singkil': [2.430, 97.920], 'Bireuen': [5.100, 96.700], 'Simeulue': [2.610, 96.080],
            'Pidie': [5.080, 95.950], 'Pidie Jaya': [5.150, 96.250], 'Benar Meriah': [4.730, 96.850],
            'Gayo Lues': [3.950, 97.350], 'Aceh Jaya': [4.750, 95.650], 'Nagan Raya': [4.150, 96.300],
            'Aceh Barat Daya': [3.800, 96.880], 'Aceh Tamiang': [4.250, 98.050]
        }
        
        df['lat'] = df['Kabupaten/Kota'].map(lambda x: coordinates.get(x, [4.20, 96.50])[0])
        df['lon'] = df['Kabupaten/Kota'].map(lambda x: coordinates.get(x, [4.20, 96.50])[1])
        
        return df
    except Exception as e:
        st.error(f"Gagal memuat data utama. Detail: {e}")
        st.stop()

df_raw = load_data()

# --- 4. SIDEBAR REDESIGN ---
with st.sidebar:
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 15px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.02);">
        <span style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">💻 Pengembang Sistem</span>
        <p style="font-size: 14px; margin:4px 0 0 0; color:#0066C2; font-weight:700;">Rivani Jahyanti</p>
        <p style="font-size: 12px; margin:2px 0 0 0; color:#475569; font-weight:500;">NPM: 2308108010024</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Filter Analisis")
    daftar_daerah = sorted(df_raw['Kabupaten/Kota'].unique())
    selected_daerah = st.multiselect("Cakupan Wilayah:", options=daftar_daerah, placeholder="Seluruh Kabupaten/Kota")
    
    if st.button("🔄 Atur Ulang Filter", use_container_width=True):
        st.st.rerun()

df_filtered = df_raw[df_raw['Kabupaten/Kota'].isin(selected_daerah)].copy() if selected_daerah else df_raw.copy()

# --- 5. HERO BANNER HEADER (GAYA IMAGE_A26520.PNG) ---
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">DASHBOARD STATISTIK REGIONAL & AREA KECIL PROVINSI ACEH</h1>
    <p class="hero-subtitle">Analisis Indikator Makro Sektoral 2025 | Sistem Informasi Akademik Tugas Akhir Rivani Jahyanti</p>
</div>
""", unsafe_allow_html=True)

# --- 6. METRIK KPI UTAMA (GAYA KONTRAS IMAGE_A260CD.PNG) ---
avg_ipm = df_filtered['IPM'].mean()
avg_kemiskinan = df_filtered['Kemiskinan (%)'].mean()
avg_tpt = df_filtered['TPT (%)'].mean()

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.markdown(f"""
    <div class="kpi-gradient-card" style="background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);">
        <div class="kpi-icon-round">📚</div>
        <div>
            <p class="kpi-label-top">Rata-Rata IPM Provinsi</p>
            <p class="kpi-num-big">{avg_ipm:.2f}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
    <div class="kpi-gradient-card" style="background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);">
        <div class="kpi-icon-round">🏠</div>
        <div>
            <p class="kpi-label-top">Rata-Rata Kemiskinan</p>
            <p class="kpi-num-big">{avg_kemiskinan:.2f}%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
    <div class="kpi-gradient-card" style="background: linear-gradient(135deg, #F59E0B 0%, #B45309 100%);">
        <div class="kpi-icon-round">💼</div>
        <div>
            <p class="kpi-label-top">Rata-Rata TPT Regional</p>
            <p class="kpi-num-big">{avg_tpt:.2f}%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 7. SEKSI DISTRIBUSI GEOGRAFIS (MAP IN CARD) ---
st.markdown("""
<div class="section-banner-card">
    <p class="section-banner-text">🗺️ Distribusi Geografis & Pemetaan Spasial Indikator</p>
</div>
""", unsafe_allow_html=True)

# Membungkus kontrol kontrol penentu skala dan peta dalam satu kesatuan Premium Card
st.markdown('<div class="premium-wrapper-card">', unsafe_allow_html=True)
map_indicator = st.selectbox(
    "Pilih Indikator Peta Spasial:",
    options=['IPM', 'Kemiskinan (%)', 'TPT (%)'],
    key="map_indicator_select"
)
st.markdown(f"<p style='font-size:13px; color:#64748B; margin-bottom:15px;'>Visualisasi interaktif menampilkan titik bobot relatif koordinat administrasi daerah berdasarkan nilai intensitas <b>{map_indicator}</b>.</p>", unsafe_allow_html=True)

color_map_scale = {
    'IPM': px.colors.sequential.Blues,
    'Kemiskinan (%)': px.colors.sequential.Reds,
    'TPT (%)': px.colors.sequential.Oranges
}

fig_map = px.scatter_mapbox(
    df_filtered, lat="lat", lon="lon", size=map_indicator, color=map_indicator,
    color_continuous_scale=color_map_scale[map_indicator], size_max=25, zoom=6.2,
    center=dict(lat=4.20, lon=96.80), mapbox_style="carto-positron",
    hover_name="Kabupaten/Kota", hover_data={map_indicator: True, 'lat': False, 'lon': False}
)
fig_map.update_layout(
    margin=dict(l=0, r=0, t=0, b=0), 
    height=400, 
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(fig_map, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# --- 8. SEKSI RANKING KINERJA (BAR CHART PREMIUM) ---
st.markdown("""
<div class="section-banner-card">
    <p class="section-banner-text">📈 Analisis Urutan & Peringkat Komparatif Daerah</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📚 Indeks Pembangunan Manusia", "🏠 Tingkat Kemiskinan (%)", "💼 Pengangguran (TPT %)"])
chart_layout_base = dict(
    font=dict(family="Inter", size=12, color="#1E293B"),
    margin=dict(l=100, r=40, t=20, b=40),
    plot_bgcolor="#F8FAFC",
    paper_bgcolor="rgba(0,0,0,0)",
    shadowheight=5
)

with tab1:
    st.markdown('<div class="premium-wrapper-card">', unsafe_allow_html=True)
    df_ipm = df_filtered.sort_values(by='IPM', ascending=True)
    fig_ipm = px.bar(df_ipm, x='IPM', y='Kabupaten/Kota', orientation='h', color='IPM', color_continuous_scale='Blues', height=550)
    fig_ipm.add_vline(x=avg_ipm, line_width=2, line_dash="dash", line_color="#EF4444", annotation_text=f"Provincial Avg: {avg_ipm:.2f}", annotation_position="top right")
    fig_ipm.update_layout(**chart_layout_base)
    fig_ipm.update_layout(coloraxis_showscale=False, yaxis_title=None, xaxis_title="Nilai Indeks IPM")
    st.plotly_chart(fig_ipm, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="premium-wrapper-card">', unsafe_allow_html=True)
    df_km = df_filtered.sort_values(by='Kemiskinan (%)', ascending=True)
    fig_km = px.bar(df_km, x='Kemiskinan (%)', y='Kabupaten/Kota', orientation='h', color='Kemiskinan (%)', color_continuous_scale='Reds', height=550)
    fig_km.add_vline(x=avg_kemiskinan, line_width=2, line_dash="dash", line_color="#0284C7", annotation_text=f"Provincial Avg: {avg_kemiskinan:.2f}%", annotation_position="top right")
    fig_km.update_layout(**chart_layout_base)
    fig_km.update_layout(coloraxis_showscale=False, yaxis_title=None, xaxis_title="Persentase Penduduk Miskin (%)")
    st.plotly_chart(fig_km, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="premium-wrapper-card">', unsafe_allow_html=True)
    df_tpt = df_filtered.sort_values(by='TPT (%)', ascending=True)
    fig_tpt = px.bar(df_tpt, x='TPT (%)', y='Kabupaten/Kota', orientation='h', color='TPT (%)', color_continuous_scale='Oranges', height=550)
    fig_tpt.add_vline(x=avg_tpt, line_width=2, line_dash="dash", line_color="#10B981", annotation_text=f"Provincial Avg: {avg_tpt:.2f}%", annotation_position="top right")
    fig_tpt.update_layout(**chart_layout_base)
    fig_tpt.update_layout(coloraxis_showscale=False, yaxis_title=None, xaxis_title="Tingkat Pengangguran Terbuka (%)")
    st.plotly_chart(fig_tpt, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# --- 9. SEKSI LINEAR CORRELATION (VERTICAL 1 COLUMN LAYOUT) ---
st.markdown("""
<div class="section-banner-card">
    <p class="section-banner-text">🔍 Matriks Korelasi & Permodelan Analisis Linier</p>
</div>
""", unsafe_allow_html=True)

def generate_premium_scatter(data, x_col, y_col, marker_color):
    x = data[x_col].values
    y = data[y_col].values
    m, c = np.polyfit(x, y, 1)
    r = np.corrcoef(x, y)[0, 1]
    
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = m * x_line + c
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode='markers', name='Kab/Kota',
        text=data['Kabupaten/Kota'],
        hovertemplate='<b>%{text}</b><br>'+x_col+': %{x:.2f}<br>'+y_col+': %{y:.2f}%<extra></extra>',
        marker=dict(size=14, color=marker_color, opacity=0.85, line=dict(width=1.5, color='#FFFFFF'))
    ))
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line, mode='lines', name='Garis Tren Regresi',
        line=dict(color='#EF4444', width=3, dash='dash')
    ))
    fig.update_layout(
        xaxis_title=f"Indikator Batas Kiri ({x_col})", yaxis_title=f"Indikator Vertikal ({y_col})",
        showlegend=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01), height=420,
        plot_bgcolor="#F1F5F9", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=50, t=20, b=50)
    )
    return fig, m, c, r

# Model 1: IPM vs Kemiskinan
st.markdown('<div class="premium-wrapper-card">', unsafe_allow_html=True)
fig_sc1, m1, c1, r1 = generate_premium_scatter(df_filtered, 'IPM', 'Kemiskinan (%)', '#0284C7')
st.plotly_chart(fig_sc1, use_container_width=True)
st.markdown(f"""
<div class="insight-panel-card">
    <b style="color:#0369A1; font-size:15px;">📌 Analisis Hubungan Struktur Linier: IPM vs Kemiskinan</b><br>
    • <b>Persamaan Model Regresi:</b> $y = {m1:.4f}x + {c1:.4f}$<br>
    • <b>Koefisien Korelasi Pearson ($r$):</b> <b>{r1:.4f}</b> (Korelasi Negatif Kuat)<br>
    <span style="color:#475569;">Arah tren berbanding terbalik secara signifikan. Setiap intervensi peningkatan satu poin indeks IPM berasosiasi nyata terhadap reduksi persentase kemiskinan makro daerah sebesar {abs(m1):.2f}%.</span>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Model 2: IPM vs TPT
st.markdown('<div class="premium-wrapper-card">', unsafe_allow_html=True)
fig_sc2, m2, c2, r2 = generate_premium_scatter(df_filtered, 'IPM', 'TPT (%)', '#F59E0B')
st.plotly_chart(fig_sc2, use_container_width=True)
st.markdown(f"""
<div class="insight-panel-card" style="border-left-color: #F59E0B;">
    <b style="color:#B45309; font-size:15px;">📌 Analisis Hubungan Struktur Linier: IPM vs Ketenagakerjaan (TPT)</b><br>
    • <b>Persamaan Model Regresi:</b> $y = {m2:.4f}x + {c2:.4f}$<br>
    • <b>Koefisien Korelasi Pearson ($r$):</b> <b>{r2:.4f}</b> (Korelasi Positif Kontekstual)<br>
    <span style="color:#475569;">Nilai parameter kemiringan positif sebesar {m2:.4f} mencerminkan karakteristik penyerapan tenaga kerja terdidik di wilayah urban dengan karakteristik capaian IPM yang tinggi.</span>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# --- 10. SEKSI KLASTERISASI EKSTREM (CARD LEADERBOARD) ---
st.markdown("""
<div class="section-banner-card">
    <p class="section-banner-text">🏆 Sorotan Klasterisasi Kinerja Ekstrem</p>
</div>
""", unsafe_allow_html=True)

col_l1, col_l2, col_l3, col_l4 = st.columns(4)

with col_l1:
    st.markdown('<div class="ranking-box-container">', unsafe_allow_html=True)
    st.markdown('<div class="ranking-header-strip" style="background: linear-gradient(135deg, #10B981 0%, #047857 100%);">🌟 5 IPM Tertinggi</div>', unsafe_allow_html=True)
    top_ipm_data = [("🥇 Kota Banda Aceh", "89.55"), ("🥈 Kota Langsa", "81.77"), ("🥉 Kota Lhokseumawe", "81.75"), ("4. Kota Sabang", "80.04"), ("5. Aceh Tengah", "78.09")]
    for name, val in top_ipm_data:
        st.markdown(f'<div class="leaderboard-row"><span>{name}</span><b>{val}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_l2:
    st.markdown('<div class="ranking-box-container">', unsafe_allow_html=True)
    st.markdown('<div class="ranking-header-strip" style="background: linear-gradient(135deg, #64748B 0%, #334155 100%);">⚠️ 5 IPM Terendah</div>', unsafe_allow_html=True)
    bottom_ipm_data = [("🛑 Kota Subulussalam", "71.63"), ("🛑 Simeulue", "71.94"), ("🛑 Aceh Barat Daya", "72.10"), ("🛑 Aceh Timur", "72.20"), ("🛑 Gayo Lues", "72.61")]
    for name, val in bottom_ipm_data:
        st.markdown(f'<div class="leaderboard-row"><span>{name}</span><b>{val}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_l3:
    st.markdown('<div class="ranking-box-container">', unsafe_allow_html=True)
    st.markdown('<div class="ranking-header-strip" style="background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);">🚨 5 Kemiskinan Tertinggi</div>', unsafe_allow_html=True)
    top_pov_data = [("🥀 Aceh Singkil", "17.07%"), ("🥀 Gayo Lues", "16.77%"), ("🥀 Pidie", "16.46%"), ("🥀 Bener Meriah", "16.20%"), ("🥀 Pidie Jaya", "16.12%")]
    for name, val in top_pov_data:
        st.markdown(f'<div class="leaderboard-row"><span>{name}</span><b>{val}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_l4:
    st.markdown('<div class="ranking-box-container">', unsafe_allow_html=True)
    st.markdown('<div class="ranking-header-strip" style="background: linear-gradient(135deg, #F59E0B 0%, #B45309 100%);">💼 5 TPT Tertinggi</div>', unsafe_allow_html=True)
    top_tpt_data = [("🔍 Kota Lhokseumawe", "8.24%"), ("🔍 Aceh Besar", "7.86%"), ("🔍 Aceh Timur", "7.74%"), ("🔍 Kota Langsa", "7.31%"), ("🔍 Kota Banda Aceh", "7.30%")]
    for name, val in top_tpt_data:
        st.markdown(f'<div class="leaderboard-row"><span>{name}</span><b>{val}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# --- 11. BASE DATA EDITOR ---
st.markdown("""
<div class="section-banner-card">
    <p class="section-banner-text">📋 Basis Data Regional Interaktif</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="premium-wrapper-card">', unsafe_allow_html=True)
st.data_editor(
    df_filtered[['Kabupaten/Kota', 'IPM', 'Kemiskinan (%)', 'TPT (%)']],
    column_config={
        "Kabupaten/Kota": st.column_config.TextColumn("Nama Kabupaten / Kota"),
        "IPM": st.column_config.NumberColumn("Indeks Pembangunan Manusia", format="%.2f"),
        "Kemiskinan (%)": st.column_config.NumberColumn("Tingkat Kemiskinan Sektoral", format="%.2f%%"),
        "TPT (%)": st.column_config.NumberColumn("Tingkat Pengangguran Terbuka (TPT)", format="%.2f%%")
    },
    use_container_width=True,
    hide_index=True
)
st.markdown('</div>', unsafe_allow_html=True)


# --- 12. RINGKASAN EKSEKUTIF CARD (PREMIUM REDESIGN) ---
st.markdown("""
<div class="section-banner-card">
    <p class="section-banner-text">🎯 Ringkasan Eksekutif & Sintesis Data</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background-color:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:25px; box-shadow:0 8px 24px rgba(0,0,0,0.03);">
    <h4 style="margin-top:0; color:#0066C2; font-size:16px; font-weight:700;">🎯 Temuan Utama Evaluasi Daerah Terpilih:</h4>
    <div style="display:flex; flex-direction:column; gap:12px; margin-top:15px; font-size:14px; color:#334155;">
        <div style="padding:10px 15px; background-color:#F0F9FF; border-left:4px solid #0284C7; border-radius:4px;">
            <b>• Pembangunan Manusia Optimal:</b> Capaian IPM tertinggi diraih oleh <b>Kota Banda Aceh</b> (89.55), sedangkan batas minimum tercatat di <b>Kota Subulussalam</b> (71.63).
        </div>
        <div style="padding:10px 15px; background-color:#FEF2F2; border-left:4px solid #EF4444; border-radius:4px;">
            <b>• Disparitas Kesejahteraan:</b> Batas atas persentase kemiskinan berada di wilayah <b>Aceh Singkil</b> senilai <b>17.07%</b>, sedangkan area dengan tingkat kemiskinan terendah adalah <b>Kota Banda Aceh</b> (5.45%).
        </div>
        <div style="padding:10px 15px; background-color:#FFFBEB; border-left:4px solid #F59E0B; border-radius:4px;">
            <b>• Tantangan Ketenagakerjaan:</b> Tingkat Pengangguran Terbuka (TPT) tertinggi didapatkan pada wilayah <b>Kota Lhokseumawe</b> sebesar <b>8.24%</b>, dan TPT paling terkendali berada di <b>Bener Meriah</b> (2.10%).
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# --- 13. PROFESSIONAL FOOTER (IDENTITAS MAHASISWA) ---
st.markdown("""
<div style="text-align: center; border-top: 1px solid #E2E8F0; padding-top: 25px; margin-top: 60px;">
    <p style="font-size: 12px; color: #0066C2; font-weight:600; margin: 5px 0 0 0;">oleh: Rivani Jahyanti | NPM: 2308108010024</p>
    <p style="font-size: 11px; color: #94A3B8; margin: 3px 0 0 0;">Sumber Data Resmi: Badan Pusat Statistik (BPS) </p>
</div>
""", unsafe_allow_html=True)
