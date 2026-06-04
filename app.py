import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    layout="wide",
    page_title="Rivani Jahyanti - 2308108010024",
    page_icon="📊"
)

# --- 2. CUSTOM CSS PREMIUM ---
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
    
    /* Hero Banner Slim Layout */
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

    /* Container Banner Judul Seksional */
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

    /* Card Umum Pembungkus Grafik */
    .premium-wrapper-card {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        margin-bottom: 25px;
    }

    /* Premium KPI Cards (Kontras Cerah) */
    .kpi-gradient-card {
        padding: 22px;
        border-radius: 12px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
        display: flex;
        align-items: center;
        gap: 18px;
        transition: transform 0.2s;
        border: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 15px;
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
        font-size: 30px;
        color: #FFFFFF;
        font-weight: 800;
        margin: 0;
        line-height: 1.1;
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
    .kpi-sub-text {
        font-size: 12px;
        color: #FFFFFF;
        margin: 2px 0 0 0;
        opacity: 0.85;
        font-weight: 500;
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

# --- 3. LOAD DATA & DATA PREPROCESSING ---
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
        return df
    except Exception as e:
        st.error(f"Gagal memuat data utama. Detail: {e}")
        st.stop()

df_raw = load_data()

# --- 4. SIDEBAR DESIGN ---
with st.sidebar:
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 15px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.02);">
        <span style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">👤 Pengembang Dashboard</span>
        <p style="font-size: 14px; margin:4px 0 0 0; color:#0066C2; font-weight:700;">Rivani Jahyanti</p>
        <p style="font-size: 12px; margin:2px 0 0 0; color:#475569; font-weight:500;">NPM: 2308108010024</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔎 Filter Data")
    daftar_daerah = sorted(df_raw['Kabupaten/Kota'].unique())
    selected_daerah = st.multiselect("Cakupan Wilayah:", options=daftar_daerah, placeholder="Seluruh Kabupaten/Kota")
    
    if st.button("🔄 Atur Ulang Filter", use_container_width=True):
        st.rerun()

df_filtered = df_raw[df_raw['Kabupaten/Kota'].isin(selected_daerah)].copy() if selected_daerah else df_raw.copy()

# --- 5. HERO BANNER HEADER ---
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">DASHBOARD STATISTIK REGIONAL DAN AREA KECIL PROVINSI ACEH</h1>
    <p class="hero-subtitle">Visualisasi dan Analisis Indikator Pembangunan Daerah Tahun 2025</p>
</div>
""", unsafe_allow_html=True)

# --- 6. METRIK KPI UTAMA ---
avg_ipm = df_filtered['IPM'].mean()
avg_kemiskinan = df_filtered['Kemiskinan (%)'].mean()
avg_tpt = df_filtered['TPT (%)'].mean()

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.markdown(f"""
    <div class="kpi-gradient-card" style="background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);">
        <div class="kpi-icon-round">🎓</div>
        <div>
            <p class="kpi-label-top">Rata-Rata IPM Aceh</p>
            <p class="kpi-num-big">{avg_ipm:.2f}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
    <div class="kpi-gradient-card" style="background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);">
        <div class="kpi-icon-round">👥</div>
        <div>
            <p class="kpi-label-top">Rata-Rata Persentase Kemiskinan Aceh</p>
            <p class="kpi-num-big">{avg_kemiskinan:.2f}%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
    <div class="kpi-gradient-card" style="background: linear-gradient(135deg, #F59E0B 0%, #B45309 100%);">
        <div class="kpi-icon-round">💼</div>
        <div>
            <p class="kpi-label-top">Rata-Rata TPT Aceh</p>
            <p class="kpi-num-big">{avg_tpt:.2f}%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- 7. SEKSI RANKING KINERJA (BAR CHART) ---
st.markdown("""
<div class="section-banner-card">
    <p class="section-banner-text">📊 Perbandingan Indikator Antar Kabupaten/Kota</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "🎓 Indeks Pembangunan Manusia",
    "👥 Tingkat Kemiskinan (%)",
    "💼 Tingkat Pengangguran Terbuka (%)"
])

chart_layout_base = dict(
    font=dict(family="Inter", size=12, color="#1E293B"),
    margin=dict(l=120, r=40, t=20, b=40),
    plot_bgcolor="#F8FAFC",
    paper_bgcolor="rgba(0,0,0,0)"
)

with tab1:
    st.markdown('<div class="premium-wrapper-card">', unsafe_allow_html=True)
    df_ipm = df_filtered.sort_values(by='IPM', ascending=True)
    fig_ipm = px.bar(df_ipm, x='IPM', y='Kabupaten/Kota', orientation='h', color='IPM', color_continuous_scale='Blues', height=550)
    fig_ipm.add_vline(x=avg_ipm, line_width=2, line_dash="dash", line_color="#EF4444", annotation_text=f"Rata-rata: {avg_ipm:.2f}", annotation_position="top right")
    fig_ipm.update_layout(**chart_layout_base)
    fig_ipm.update_layout(coloraxis_showscale=False, yaxis_title=None, xaxis_title="Nilai Indeks IPM")
    st.plotly_chart(fig_ipm, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="premium-wrapper-card">', unsafe_allow_html=True)
    df_km = df_filtered.sort_values(by='Kemiskinan (%)', ascending=True)
    fig_km = px.bar(df_km, x='Kemiskinan (%)', y='Kabupaten/Kota', orientation='h', color='Kemiskinan (%)', color_continuous_scale='Reds', height=550)
    fig_km.add_vline(x=avg_kemiskinan, line_width=2, line_dash="dash", line_color="#0066C2", annotation_text=f"Rata-rata: {avg_kemiskinan:.2f}%", annotation_position="top right")
    fig_km.update_layout(**chart_layout_base)
    fig_km.update_layout(coloraxis_showscale=False, yaxis_title=None, xaxis_title="Persentase Penduduk Miskin (%)")
    st.plotly_chart(fig_km, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="premium-wrapper-card">', unsafe_allow_html=True)
    df_tpt = df_filtered.sort_values(by='TPT (%)', ascending=True)
    fig_tpt = px.bar(df_tpt, x='TPT (%)', y='Kabupaten/Kota', orientation='h', color='TPT (%)', color_continuous_scale='Oranges', height=550)
    fig_tpt.add_vline(x=avg_tpt, line_width=2, line_dash="dash", line_color="#10B981", annotation_text=f"Rata-rata: {avg_tpt:.2f}%", annotation_position="top right")
    fig_tpt.update_layout(**chart_layout_base)
    fig_tpt.update_layout(coloraxis_showscale=False, yaxis_title=None, xaxis_title="Tingkat Pengangguran Terbuka (%)")
    st.plotly_chart(fig_tpt, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# --- 8. SEKSI LINEAR CORRELATION (SCATTER PLOT) ---
st.markdown("""
<div class="section-banner-card">
    <p class="section-banner-text">📊 Analisis Korelasi dan Regresi Linier</p>
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
        x=x_line, y=y_line, mode='lines', name='Garis Tren Regresi',
        line=dict(color='#E11D48', width=3, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=x, y=y, mode='markers', name='Kabupaten/Kota',
        text=data['Kabupaten/Kota'],
        hovertemplate='<b>%{text}</b><br>'+x_col+': %{x:.2f}<br>'+y_col+': %{y:.2f}%<extra></extra>',
        marker=dict(
            size=15, 
            color=marker_color, 
            opacity=0.9, 
            line=dict(width=1.5, color='#FFFFFF')
        )
    ))
    
    fig.update_layout(
        xaxis_title=f"Indikator ({x_col})", 
        yaxis_title=f"Indikator ({y_col})",
        showlegend=True, 
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02, bgcolor="rgba(255,255,255,0.8)", bordercolor="#E2E8F0", borderwidth=1), 
        height=450,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=60, r=40, t=30, b=60)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#F1F5F9', zeroline=False, linecolor='#E2E8F0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#F1F5F9', zeroline=False, linecolor='#E2E8F0')
    
    return fig, m, c, r

# Model 1: IPM vs Kemiskinan
st.markdown('<div class="premium-wrapper-card">', unsafe_allow_html=True)
fig_sc1, m1, c1, r1 = generate_premium_scatter(df_filtered, 'IPM', 'Kemiskinan (%)', '#0284C7')
st.plotly_chart(fig_sc1, use_container_width=True)
st.markdown(f"""
<div class="insight-panel-card">
    <b style="color:#0369A1; font-size:15px;">📊 Interpretasi Hubungan IPM dan Kemiskinan</b><br>
    • <b>Persamaan Model Regresi:</b> y = {m1:.4f}x + {c1:.4f} <br>
    • <b>Koefisien Korelasi Pearson (r):</b> <b>{r1:.4f}</b> (Korelasi Negatif Kuat)<br>
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
    <b style="color:#B45309; font-size:15px;">📊 Interpretasi Hubungan IPM dan Tingkat Pengangguran Terbuka</b><br>
    • <b>Persamaan Model Regresi:</b> y = {m2:.4f}x + {c2:.4f} <br>
    • <b>Koefisien Korelasi Pearson (r):</b> <b>{r2:.4f}</b> (Korelasi Positif Kontekstual)<br>
    <span style="color:#475569;">Nilai parameter kemiringan positif sebesar {m2:.4f} mencerminkan karakteristik penyerapan tenaga kerja terdidik di wilayah urban dengan karakteristik capaian IPM yang tinggi.</span>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# --- 9. SEKSI KLASTERISASI EKSTREM (PREMIUM KPI CARDS) ---
st.markdown("""
<div class="section-banner-card">
    <p class="section-banner-text">📌 Indikator Daerah dengan Nilai Ekstrem</p>
</div>
""", unsafe_allow_html=True)

col_l1, col_l2, col_l3, col_l4 = st.columns(4)

with col_l1:
    st.markdown("""
    <div class="kpi-gradient-card" style="background: linear-gradient(135deg, #10B981 0%, #047857 100%); height: 110px;">
        <div class="kpi-icon-round">📈</div>
        <div>
            <p class="kpi-label-top">IPM Tertinggi</p>
            <p class="kpi-num-big">89.55</p>
            <p class="kpi-sub-text">Kota Banda Aceh</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_l2:
    st.markdown("""
    <div class="kpi-gradient-card" style="background: linear-gradient(135deg, #64748B 0%, #334155 100%); height: 110px;">
        <div class="kpi-icon-round">📉</div>
        <div>
            <p class="kpi-label-top">IPM Terendah</p>
            <p class="kpi-num-big">71.63</p>
            <p class="kpi-sub-text">Kota Subulussalam</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_l3:
    st.markdown("""
    <div class="kpi-gradient-card" style="background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%); height: 110px;">
        <div class="kpi-icon-round">👥</div>
        <div>
            <p class="kpi-label-top">Kemiskinan Tertinggi</p>
            <p class="kpi-num-big">17.07%</p>
            <p class="kpi-sub-text">Aceh Singkil</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_l4:
    st.markdown("""
    <div class="kpi-gradient-card" style="background: linear-gradient(135deg, #F59E0B 0%, #B45309 100%); height: 110px;">
        <div class="kpi-icon-round">💼</div>
        <div>
            <p class="kpi-label-top">TPT Tertinggi</p>
            <p class="kpi-num-big">8.24%</p>
            <p class="kpi-sub-text">Kota Lhokseumawe</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- 10. BASE DATA EDITOR ---
st.markdown("""
<div class="section-banner-card">
    <p class="section-banner-text">🗂️ Tabel Data Statistik Regional</p>
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


# --- 11. RINGKASAN EKSEKUTIF CARD ---
st.markdown("""
<div class="section-banner-card">
    <p class="section-banner-text">📄 Ringkasan Eksekutif dan Temuan Utama</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background-color:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:25px; box-shadow:0 8px 24px rgba(0,0,0,0.03);">
    <h4 style="margin-top:0; color:#0066C2; font-size:16px; font-weight:700;">
        📊 Temuan Utama Analisis Statistik:
    </h4>
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


# --- 12. PROFESSIONAL FOOTER ---
st.markdown("""
<div style="text-align: center; border-top: 1px solid #E2E8F0; padding-top: 25px; margin-top: 60px;">
    <p style="font-size: 14px; color: #1E293B; font-weight:700; margin: 0;">📊 Dashboard Statistik Regional dan Area Kecil Provinsi Aceh - Tahun Data 2025</p>
    <p style="font-size: 12px; color: #0066C2; font-weight:600; margin: 5px 0 0 0;">Dashboard Statistik Interaktif oleh: Rivani Jahyanti | NPM: 2308108010024</p>
    <p style="font-size: 11px; color: #94A3B8; margin: 3px 0 0 0;">Sumber Data Resmi: Badan Pusat Statistik (BPS)</p>
</div>
""", unsafe_allow_html=True)
