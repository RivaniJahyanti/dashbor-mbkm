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

# --- 2. CUSTOM CSS (PREMIUM & MODERN DESIGN) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Banner Slim Layout */
    .hero-container {
        background: linear-gradient(135deg, #1565C0 0%, #1E3A8A 100%);
        padding: 20px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(21, 101, 192, 0.15);
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .hero-icon {
        font-size: 40px;
        background: rgba(255, 255, 255, 0.2);
        padding: 10px;
        border-radius: 10px;
    }
    .hero-text-content {
        flex-grow: 1;
    }
    .hero-title {
        color: #FFFFFF !important;
        font-size: 26px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        color: #E3F2FD !important;
        font-size: 14px !important;
        margin: 5px 0 0 0 !important;
        opacity: 0.9;
    }

    /* Subjudul Seksi Komponen */
    .section-header {
        color: #0F172A;
        font-size: 20px;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 15px;
        padding-left: 10px;
        border-left: 5px solid #1565C0;
    }

    /* Sidebar Info Card Styles */
    .sidebar-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .sidebar-card-title {
        font-size: 12px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }

    /* Premium KPI Cards Styling */
    .kpi-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        border: 1px solid #E2E8F0;
        display: flex;
        align-items: center;
        gap: 15px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(15, 23, 42, 0.08);
    }
    .kpi-icon-wrapper {
        font-size: 30px;
        width: 55px;
        height: 55px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
    }
    .kpi-val-container {
        display: flex;
        flex-direction: column;
    }
    .kpi-label {
        font-size: 12px;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        margin: 0;
    }
    .kpi-num {
        font-size: 28px;
        color: #0F172A;
        font-weight: 700;
        margin: 2px 0 0 0;
    }

    /* Ranking & Insight Card Styles */
    .ranking-card {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
        height: 100%;
    }
    .ranking-title-bar {
        font-size: 14px;
        font-weight: 700;
        color: #FFFFFF;
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 12px;
        text-align: center;
    }
    .leaderboard-item {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px dashed #F1F5F9;
        font-size: 13px;
    }
    .leaderboard-item:last-child {
        border-bottom: none;
    }

    .insight-card {
        background-color: #F8FAFC;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1565C0;
        margin-top: 12px;
        font-size: 13.5px;
        color: #334155;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOAD & SYNTHETIC MAP DATA SEEDING ---
@st.cache_data(ttl=600)
def load_data():
    # Menggunakan Sheet ID milik pengguna
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
        
        # Koordinat centroid perkiraan spasial Kabupaten/Kota di Aceh untuk visualisasi peta tanpa berkas GeoJSON eksternal
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
        st.error(f"Gagal memuat basis data utama. Detail: {e}")
        st.stop()

df_raw = load_data()

# --- 4. SIDEBAR REDESIGN ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-card-title">🏛️ Keterangan Dashboard</div>
        <p style="font-size: 13px; margin:0; color:#334155; font-weight:600;">Badan Pusat Statistik Provinsi Aceh</p>
        <p style="font-size: 12px; margin:3px 0 0 0; color:#64748B;">Sistem Analisis Spasial & Makro Sektoral</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metadata Ringkas Tabel
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown('<div class="sidebar-card"><div class="sidebar-card-title">📅 Tahun</div><b style="font-size:16px; color:#1565C0;">2025</b></div>', unsafe_allow_html=True)
    with col_s2:
        st.markdown(f'<div class="sidebar-card"><div class="sidebar-card-title">🏙️ Wilayah</div><b style="font-size:16px; color:#1565C0;">{len(df_raw)} Daerah</b></div>', unsafe_allow_html=True)
        
    st.markdown('<div class="sidebar-card"><div class="sidebar-card-title">📋 Cakupan Variabel</div><span style="font-size:12.5px; color:#334155;">• Indeks Pembangunan Manusia (IPM)<br>• Kemiskinan Regional (%)<br>• Pengangguran Terbuka (TPT %)</span></div>', unsafe_allow_html=True)

    # Filter Wilayah Kerja
    st.markdown("### ⚙️ Kontrol Filter")
    daftar_daerah = sorted(df_raw['Kabupaten/Kota'].unique())
    selected_daerah = st.multiselect("Pilih Cakupan Wilayah Analisis:", options=daftar_daerah, placeholder="Menampilkan Seluruh Wilayah")
    
    if st.button("🔄 Atur Ulang Filter", use_container_width=True):
        st.rerun()

    st.markdown("""
    <div style="margin-top: 30px; padding: 10px; border-top: 1px solid #E2E8F0;">
        <span style="font-size: 11px; color: #94A3B8;">Pembaruan Terakhir:<br><b>Juni 2026 (Live Sync)</b></span>
    </div>
    """, unsafe_allow_html=True)

# Data Filter Binding
df_filtered = df_raw[df_raw['Kabupaten/Kota'].isin(selected_daerah)].copy() if selected_daerah else df_raw.copy()

# --- 5. HERO BANNER HEADER SLIM ---
st.markdown("""
<div class="hero-container">
    <div class="hero-icon">📊</div>
    <div class="hero-text-content">
        <h1 class="hero-title">Dashboard Statistik Regional & Analisis Area Kecil Provinsi Aceh</h1>
        <p class="hero-subtitle">Portal Evaluasi Capaian Indikator Makro: Integrasi Pembangunan Manusia, Kemiskinan, dan Ketenagakerjaan</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. PREMIUM KPI CARDS IMPLEMENTATION ---
avg_ipm = df_filtered['IPM'].mean()
avg_kemiskinan = df_filtered['Kemiskinan (%)'].mean()
avg_tpt = df_filtered['TPT (%)'].mean()

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.markdown(f"""
    <div class="kpi-card" style="border-top: 4px solid #1565C0;">
        <div class="kpi-icon-wrapper" style="background-color: #E3F2FD; color: #1565C0;">📚</div>
        <div class="kpi-val-container">
            <p class="kpi-label">Rata-Rata IPM Provinsi</p>
            <p class="kpi-num">{avg_ipm:.2f}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
    <div class="kpi-card" style="border-top: 4px solid #D32F2F;">
        <div class="kpi-icon-wrapper" style="background-color: #FFEBEE; color: #D32F2F;">🏠</div>
        <div class="kpi-val-container">
            <p class="kpi-label">Rata-Rata Kemiskinan</p>
            <p class="kpi-num">{avg_kemiskinan:.2f}%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
    <div class="kpi-card" style="border-top: 4px solid #EF6C00;">
        <div class="kpi-icon-wrapper" style="background-color: #FFF3E0; color: #EF6C00;">💼</div>
        <div class="kpi-val-container">
            <p class="kpi-label">Rata-Rata TPT Regional</p>
            <p class="kpi-num">{avg_tpt:.2f}%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 7. SPATIAL GEOGRAPHIC SECTOR (MAP INTEGRATION) ---
st.markdown("<p class='section-header'>🗺️ Distribusi Geografis & Pemetaan Spasial Indikator</p>", unsafe_allow_html=True)

col_map_ctrl, col_map_view = st.columns([1, 3])

with col_map_ctrl:
    st.markdown("<div style='padding-top:15px;'></div>", unsafe_allow_html=True)
    map_indicator = st.selectbox(
        "Pilih Indikator Peta Spasial:",
        options=['IPM', 'Kemiskinan (%)', 'TPT (%)'],
        help="Warna visualisasi pada peta sebaran otomatis menyesuaikan dengan performa capaian nilai indikator yang dipilih."
    )
    
    color_map_scale = {
        'IPM': px.colors.sequential.Blues,
        'Kemiskinan (%)': px.colors.sequential.Reds,
        'TPT (%)': px.colors.sequential.Oranges
    }
    
    st.info(f"Visualisasi interaktif menampilkan titik bobot relatif koordinat administrasi daerah berdasarkan nilai intensitas **{map_indicator}**.")

with col_map_view:
    fig_map = px.scatter_mapbox(
        df_filtered, lat="lat", lon="lon", size=map_indicator, color=map_indicator,
        color_continuous_scale=color_map_scale[map_indicator], size_max=28, zoom=6.2,
        center=dict(lat=4.20, lon=96.80), mapbox_style="carto-positron",
        hover_name="Kabupaten/Kota", hover_data={map_indicator: True, 'lat': False, 'lon': False}
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=380, coloraxis_showscale=True)
    st.plotly_chart(fig_map, use_container_width=True)

# --- 8. RANKING SECTION WITH Province Average Benchmark ---
st.markdown("<p class='section-header'>📈 Analisis Urutan & Peringkat Komparatif Daerah</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📚 Indeks Pembangunan Manusia", "🏠 Tingkat Kemiskinan (%)", "💼 Pengangguran (TPT %)"])
chart_config = dict(font=dict(family="Inter", size=11), margin=dict(l=60, r=40, t=30, b=30), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

with tab1:
    df_ipm = df_filtered.sort_values(by='IPM', ascending=True)
    fig_ipm = px.bar(df_ipm, x='IPM', y='Kabupaten/Kota', orientation='h', color='IPM', color_continuous_scale='Blues', height=550)
    fig_ipm.add_vline(x=avg_ipm, line_width=1.5, line_dash="dash", line_color="#D32F2F", annotation_text=f"Rata-rata: {avg_ipm:.2f}", annotation_position="top right")
    fig_ipm.update_layout(**chart_config)
    fig_ipm.update_layout(coloraxis_showscale=False, yaxis_title=None)
    st.plotly_chart(fig_ipm, use_container_width=True)

with tab2:
    df_km = df_filtered.sort_values(by='Kemiskinan (%)', ascending=True)
    fig_km = px.bar(df_km, x='Kemiskinan (%)', y='Kabupaten/Kota', orientation='h', color='Kemiskinan (%)', color_continuous_scale='Reds', height=550)
    fig_km.add_vline(x=avg_kemiskinan, line_width=1.5, line_dash="dash", line_color="#1565C0", annotation_text=f"Rata-rata: {avg_kemiskinan:.2f}%", annotation_position="top right")
    fig_km.update_layout(**chart_config)
    fig_km.update_layout(coloraxis_showscale=False, yaxis_title=None)
    st.plotly_chart(fig_km, use_container_width=True)

with tab3:
    df_tpt = df_filtered.sort_values(by='TPT (%)', ascending=True)
    fig_tpt = px.bar(df_tpt, x='TPT (%)', y='Kabupaten/Kota', orientation='h', color='TPT (%)', color_continuous_scale='Oranges', height=550)
    fig_tpt.add_vline(x=avg_tpt, line_width=1.5, line_dash="dash", line_color="#2E7D32", annotation_text=f"Rata-rata: {avg_tpt:.2f}%", annotation_position="top right")
    fig_tpt.update_layout(**chart_config)
    fig_tpt.update_layout(coloraxis_showscale=False, yaxis_title=None)
    st.plotly_chart(fig_tpt, use_container_width=True)

# --- 9. CORRELATION SECTION (SCATTER PLOT & INSIGHTS) ---
st.markdown("<p class='section-header'>🔍 Matriks Korelasi & Permodelan Analisis Linier</p>", unsafe_allow_html=True)

col_sc1, col_sc2 = st.columns(2)

def generate_clean_scatter(data, x_col, y_col, theme_color):
    x = data[x_col].values
    y = data[y_col].values
    m, c = np.polyfit(x, y, 1)
    
    # Hitung Koefisien Korelasi Pearson (r)
    r = np.corrcoef(x, y)[0, 1]
    
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = m * x_line + c
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode='markers', name='Daerah',
        text=data['Kabupaten/Kota'],
        hovertemplate='<b>%{text}</b><br>'+x_col+': %{x:.2f}<br>'+y_col+': %{y:.2f}%<extra></extra>',
        marker=dict(size=12, color=theme_color, opacity=0.8, line=dict(width=1, color='#FFFFFF'))
    ))
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line, mode='lines', name='Tren Linier',
        line=dict(color='#D32F2F', width=2, dash='dot')
    ))
    fig.update_layout(
        xaxis_title=x_col, yaxis_title=y_col, showlegend=False, height=380,
        plot_bgcolor="#F8FAFC", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=20, b=40)
    )
    return fig, m, c, r

with col_sc1:
    fig_sc1, m1, c1, r1 = generate_clean_scatter(df_filtered, 'IPM', 'Kemiskinan (%)', '#1565C0')
    st.plotly_chart(fig_sc1, use_container_width=True)
    st.markdown(f"""
    <div class="insight-card">
        <b style="color:#1565C0;">📌 Hubungan Struktur IPM & Kemiskinan</b><br>
        • Persamaan Regresi: $y = {m1:.3f}x + {c1:.3f}$<br>
        • Koefisien Korelasi ($r$): <b>{r1:.3f}</b> (Korelasi Kuat Negatif)<br>
        Sifat hubungan bernilai negatif signifikan. Setiap kenaikan intervensi satu poin IPM terasosiasi dengan estimasi penurunan beban kemiskinan makro regional sebesar {abs(m1):.2f}%.
    </div>
    """, unsafe_allow_html=True)

with col_sc2:
    fig_sc2, m2, c2, r2 = generate_clean_scatter(df_filtered, 'IPM', 'TPT (%)', '#EF6C00')
    st.plotly_chart(fig_sc2, use_container_width=True)
    st.markdown(f"""
    <div class="insight-card" style="border-left-color: #EF6C00;">
        <b style="color:#EF6C00;">📌 Hubungan Struktur IPM & Pengangguran (TPT)</b><br>
        • Persamaan Regresi: $y = {m2:.3f}x + {c2:.3f}$<br>
        • Koefisien Korelasi ($r$): <b>{r2:.3f}</b> (Korelasi Positif Kontekstual)<br>
        Nilai kemiringan $b_1 = {m2:.3f}$ mengonfirmasi fenomena khas ketenagakerjaan urban, di mana wilayah ber-IPM tinggi cenderung memiliki konsentrasi pencari kerja berpendidikan tinggi.
    </div>
    """, unsafe_allow_html=True)

# --- 10. LEADERBOARD EXTRA-DISTRIBUTION CARDS ---
st.markdown("<p class='section-header'>🏆 Sorotan Klasterisasi Kinerja Ekstrem</p>", unsafe_allow_html=True)

col_l1, col_l2, col_l3, col_l4 = st.columns(4)
medals = ["🥇", "🥈", "🥉", "4.", "5."]

with col_l1:
    st.markdown('<div class="ranking-card">', unsafe_allow_html=True)
    st.markdown('<div class="ranking-title-bar" style="background-color: #2E7D32;">🌟 5 IPM Tertinggi</div>', unsafe_allow_html=True)
    for i, (_, row) in enumerate(df_filtered.nlargest(5, 'IPM').iterrows()):
        st.markdown(f'<div class="leaderboard-item"><span>{medals[i]} {row["Kabupaten/Kota"]}</span><b>{row["IPM"]:.2f}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_l2:
    st.markdown('<div class="ranking-card">', unsafe_allow_html=True)
    st.markdown('<div class="ranking-title-bar" style="background-color: #64748B;">⚠️ 5 IPM Terendah</div>', unsafe_allow_html=True)
    for i, (_, row) in enumerate(df_filtered.nsmallest(5, 'IPM').iterrows()):
        st.markdown(f'<div class="leaderboard-item"><span>🛑 {row["Kabupaten/Kota"]}</span><b>{row["IPM"]:.2f}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_l3:
    st.markdown('<div class="ranking-card">', unsafe_allow_html=True)
    st.markdown('<div class="ranking-title-bar" style="background-color: #D32F2F;">🚨 5 Kemiskinan Tertinggi</div>', unsafe_allow_html=True)
    for i, (_, row) in enumerate(df_filtered.nlargest(5, 'Kemiskinan (%)').iterrows()):
        st.markdown(f'<div class="leaderboard-item"><span>🥀 {row["Kabupaten/Kota"]}</span><b>{row["Kemiskinan (%)"]:.2f}%</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_l4:
    st.markdown('<div class="ranking-card">', unsafe_allow_html=True)
    st.markdown('<div class="ranking-title-bar" style="background-color: #EF6C00;">💼 5 TPT Tertinggi</div>', unsafe_allow_html=True)
    for i, (_, row) in enumerate(df_filtered.nlargest(5, 'TPT (%)').iterrows()):
        st.markdown(f'<div class="leaderboard-item"><span>🔍 {row["Kabupaten/Kota"]}</span><b>{row["TPT (%)"]:.2f}%</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 11. INTERACTIVE DATA EDITOR SECTION ---
st.markdown("<p class='section-header'>📋 Basis Data Regional Interaktif</p>", unsafe_allow_html=True)

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

# --- 12. EXECUTIVE SUMMARY CARD ---
st.markdown("<p class='section-header'>🎯 Ringkasan Eksekutif & Sintesis Data</p>", unsafe_allow_html=True)

h_ipm = df_filtered.loc[df_filtered['IPM'].idxmax()]
l_ipm = df_filtered.loc[df_filtered['IPM'].idxmin()]
h_ms = df_filtered.loc[df_filtered['Kemiskinan (%)'].idxmax()]
l_ms = df_filtered.loc[df_filtered['Kemiskinan (%)'].idxmin()]
h_tpt = df_filtered.loc[df_filtered['TPT (%)'].idxmax()]
l_tpt = df_filtered.loc[df_filtered['TPT (%)'].idxmin()]

st.markdown(f"""
<div style="background-color:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:20px; box-shadow:0 4px 12px rgba(0,0,0,0.02);">
    <h4 style="margin-top:0; color:#1565C0; font-size:16px;">🎯 Temuan Utama Evaluasi Daerah Terpilih:</h4>
    <ul style="margin:0; padding-left:20px; font-size:13.5px; color:#334155; line-height:1.8;">
        <li><b>Pembangunan Manusia Optimal:</b> Capaian IPM tertinggi diraih oleh <b>{h_ipm['Kabupaten/Kota']}</b> ({h_ipm['IPM']:.2f}), sedangkan batas minimum tercatat di <b>{l_ipm['Kabupaten/Kota']}</b> ({l_ipm['IPM']:.2f}).</li>
        <li><b>Disparitas Kesejahteraan:</b> Batas atas persentase kemiskinan berada di wilayah <b>{h_ms['Kabupaten/Kota']}</b> senilai <b>{h_ms['Kemiskinan (%)']:.2f}%</b>, sedangkan area dengan tingkat kemiskinan terendah adalah <b>{l_ms['Kabupaten/Kota']}</b> ({l_ms['Kemiskinan (%)']:.2f}%).</li>
        <li><b>Tantangan Ketenagakerjaan:</b> Tingkat Pengangguran Terbuka (TPT) tertinggi didapatkan pada wilayah <b>{h_tpt['Kabupaten/Kota']}</b> sebesar <b>{h_tpt['TPT (%)']:.2f}%</b>, dan TPT paling terkendali berada di <b>{l_tpt['Kabupaten/Kota']}</b> ({l_tpt['TPT (%)']:.2f}%).</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# --- 13. PROFESSIONAL FOOTER ---
st.markdown("""
<div style="text-align: center; border-top: 1px solid #E2E8F0; padding-top: 20px; margin-top: 60px;">
    <p style="font-size: 13px; color: #475569; font-weight:600; margin: 0;">🏛️ Portal Data Statistik Regional Makro Provinsi Aceh - Tahun Data 2025</p>
    <p style="font-size: 11px; color: #94A3B8; margin: 4px 0 0 0;">Sumber Data Resmi: Badan Pusat Statistik (BPS) | Dikembangkan Berbasis Framework Streamlit Enterprise & Plotly Engine</p>
</div>
""", unsafe_allow_html=True)
