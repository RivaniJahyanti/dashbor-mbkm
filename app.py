import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    layout="wide",
    page_title="Dashboard Analitik Regional Aceh",
    page_icon="📊"
)

# Custom CSS Pemoles Estetika Komponen
st.markdown("""
<style>
    /* Mengatur gaya font global dan membersihkan padding berlebih */
    html, body, [data-testid="stSidebarNav"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Menghilangkan border default st.metric bawaan agar menyatu dengan kartu custom */
    [data-testid="stMetric"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    /* Mempercantik tampilan judul tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px;
        background-color: transparent;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }

    /* Container Blok Interpretasi Jurnal */
    .interpretasi-container {
        background-color: #F8FAFC;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2563EB;
        margin-top: 12px;
        font-size: 14px;
        line-height: 1.6;
        color: #334155;
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
                st.error(f"Kolom penting '{col}' tidak berhasil dipetakan dari dokumen spreadsheet.")
                st.stop()

        df.dropna(subset=['Kabupaten/Kota'], inplace=True)
        df['Kabupaten/Kota'] = df['Kabupaten/Kota'].str.strip()

        for col in ['IPM', 'Kemiskinan (%)', 'TPT (%)']:
            df[col] = df[col].astype(str).str.replace('%', '').str.replace(',', '.').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(subset=['IPM', 'Kemiskinan (%)', 'TPT (%)'], inplace=True)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data dari Google Sheets. Detail Error: {e}")
        st.stop()

df_raw = load_data()


# --- 3. FILTER INTERAKTIF DI SIDEBAR ---
st.sidebar.markdown("### ⚙️ Panel Kontrol")
st.sidebar.caption("Saring visualisasi data berdasarkan preferensi wilayah di bawah ini.")

daftar_daerah = sorted(df_raw['Kabupaten/Kota'].unique())

if 'selected_daerah' not in st.session_state:
    st.session_state['selected_daerah'] = []

selected_daerah = st.sidebar.multiselect(
    "Pilih Wilayah Analisis:",
    options=daftar_daerah,
    default=st.session_state['selected_daerah'],
    key="daerah_filter"
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Atur Ulang Semua Filter", use_container_width=True):
    st.session_state['daerah_filter'] = []
    st.rerun()

if selected_daerah:
    df_filtered = df_raw[df_raw['Kabupaten/Kota'].isin(selected_daerah)].copy()
else:
    df_filtered = df_raw.copy()


# --- 4. HEADER DASHBOARD ---
st.markdown("<h1 style='text-align: left; color: #1E293B; font-weight: 800; margin-bottom: 2px;'>Statistik Regional & Statistik Area Kecil</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left; color: #64748B; font-size: 15px; margin-bottom: 20px;'>Evaluasi Komparatif Indikator Makro Pembangunan Provinsi Aceh Tahun 2025</p>", unsafe_allow_html=True)

# Status info jumlah wilayah yang aktif
st.caption(f"Menampilkan analisis untuk {len(df_filtered)} dari {len(df_raw)} Kabupaten / Kota")


# --- 5. INDIKATOR KINERJA UTAMA (KPI CARDS DENGAN NATIVE CONTAINER) ---
avg_ipm = df_filtered['IPM'].mean()
avg_kemiskinan = df_filtered['Kemiskinan (%)'].mean()
avg_tpt = df_filtered['TPT (%)'].mean()

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    with st.container(border=True):
        st.markdown("<span style='color: #2563EB; font-weight: bold;'>📈 Rata-rata Indeks Pembangunan</span>", unsafe_allow_html=True)
        st.metric(label="Indeks Pembangunan Manusia (IPM)", value=f"{avg_ipm:.2f}")

with col_kpi2:
    with st.container(border=True):
        st.markdown("<span style='color: #DC2626; font-weight: bold;'>🛑 Rata-rata Marjinal Wilayah</span>", unsafe_allow_html=True)
        st.metric(label="Persentase Penduduk Miskin", value=f"{avg_kemiskinan:.2f} %")

with col_kpi3:
    with st.container(border=True):
        st.markdown("<span style='color: #D97706; font-weight: bold;'>💼 Rata-rata Pengangguran</span>", unsafe_allow_html=True)
        st.metric(label="Tingkat Pengangguran Terbuka (TPT)", value=f"{avg_tpt:.2f} %")

st.markdown("<br>", unsafe_allow_html=True)


# --- 6. VISUALISASI RANKING (BAR CHARTS DENGAN POLISHING) ---
st.markdown("<h3 style='color: #1E293B; font-weight: 700;'>Peringkat Capaian Indikator Regional</h3>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📈 Indeks Pembangunan Manusia", 
    "📊 Persentase Kemiskinan", 
    "💼 Tingkat Pengangguran Terbuka"
])

with tab1:
    df_ipm_sorted = df_filtered.sort_values(by='IPM', ascending=True)
    fig_ipm = px.bar(
        df_ipm_sorted,
        x='IPM',
        y='Kabupaten/Kota',
        orientation='h',
        text='IPM',
        color='IPM',
        color_continuous_scale=['#DBEAFE', '#2563EB'],
        height=max(400, len(df_ipm_sorted) * 25)
    )
    fig_ipm.update_traces(texttemplate='%{text:.2f}', textposition='outside', marker_line_color='rgba(0,0,0,0)')
    fig_ipm.update_layout(
        yaxis=dict(title="", tickfont=dict(size=11)), 
        xaxis=dict(title="Nilai Indeks", range=[df_raw['IPM'].min() - 2, df_raw['IPM'].max() + 2]),
        coloraxis_showscale=False,
        bargap=0.25,
        margin=dict(l=10, r=40, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_ipm, use_container_width=True)

with tab2:
    df_kemiskinan_sorted = df_filtered.sort_values(by='Kemiskinan (%)', ascending=True)
    fig_kemiskinan = px.bar(
        df_kemiskinan_sorted,
        x='Kemiskinan (%)',
        y='Kabupaten/Kota',
        orientation='h',
        text='Kemiskinan (%)',
        color='Kemiskinan (%)',
        color_continuous_scale=['#FEE2E2', '#DC2626'],
        height=max(400, len(df_kemiskinan_sorted) * 25)
    )
    fig_kemiskinan.update_traces(texttemplate='%{text:.2f}%', textposition='outside', marker_line_color='rgba(0,0,0,0)')
    fig_kemiskinan.update_layout(
        yaxis=dict(title="", tickfont=dict(size=11)), 
        xaxis=dict(title="Proporsi Kemiskinan (%)", range=[0, df_raw['Kemiskinan (%)'].max() + 3]),
        coloraxis_showscale=False,
        bargap=0.25,
        margin=dict(l=10, r=40, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_kemiskinan, use_container_width=True)

with tab3:
    df_tpt_sorted = df_filtered.sort_values(by='TPT (%)', ascending=True)
    fig_tpt = px.bar(
        df_tpt_sorted,
        x='TPT (%)',
        y='Kabupaten/Kota',
        orientation='h',
        text='TPT (%)',
        color='TPT (%)',
        color_continuous_scale=['#FEF3C7', '#D97706'],
        height=max(400, len(df_tpt_sorted) * 25)
    )
    fig_tpt.update_traces(texttemplate='%{text:.2f}%', textposition='outside', marker_line_color='rgba(0,0,0,0)')
    fig_tpt.update_layout(
        yaxis=dict(title="", tickfont=dict(size=11)), 
        xaxis=dict(title="Tingkat Pengangguran (%)", range=[0, df_raw['TPT (%)'].max() + 2]),
        coloraxis_showscale=False,
        bargap=0.25,
        margin=dict(l=10, r=40, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_tpt, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)


# --- 7. ANALISIS KORELASI (SCATTER PLOTS DENGAN REGRESI) ---
st.markdown("<h3 style='color: #1E293B; font-weight: 700;'>Eksplorasi Hubungan Antar Indikator</h3>", unsafe_allow_html=True)

col_sc1, col_sc2 = st.columns(2)

def create_scatter_with_trendline(data, x_col, y_col, title, color_theme):
    x = data[x_col].values
    y = data[y_col].values
    
    m, c = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = m * x_line + c

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='markers',
        text=data['Kabupaten/Kota'],
        hovertemplate='<b>%{text}</b><br>' + x_col + ': %{x:.2f}<br>' + y_col + ': %{y:.2f}%<extra></extra>',
        marker=dict(size=10, color=color_theme, opacity=0.8, line=dict(width=1, color='#FFFFFF'))
    ))
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode='lines',
        name='Tren Linier',
        line=dict(color='#EF4444', width=2, dash='dash'),
        hoverinfo='skip'
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color='#1E293B', weight='bold')),
        xaxis=dict(title=x_col, gridcolor='#E2E8F0'),
        yaxis=dict(title=y_col, gridcolor='#E2E8F0'),
        showlegend=False,
        height=380,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor='#F8FAFC',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig, m, c

with col_sc1:
    with st.container():
        fig_sc1, m1, c1 = create_scatter_with_trendline(
            df_filtered, 'IPM', 'Kemiskinan (%)',
            'Analisis Elastisitas IPM terhadap Tingkat Kemiskinan', '#2563EB'
        )
        st.plotly_chart(fig_sc1, use_container_width=True)
        
        st.markdown(f"""
        <div class="interpretasi-container">
            <strong>Korelasi Struktural IPM & Kemiskinan:</strong><br>
            Persamaan Estimasi Linier:
            $$y = {m1:.4f}x + {c1:.4f}$$
            Arah koefisien kemiringan yang bernilai negatif mengonfirmasi secara empiris bahwa perluasan kapasitas kapabilitas manusia (IPM) berkorelasi linear dengan reduksi kemiskinan di area regional Provinsi Aceh.
        </div>
        """, unsafe_allow_html=True)

with col_sc2:
    with st.container():
        fig_sc2, m2, c2 = create_scatter_with_trendline(
            df_filtered, 'IPM', 'TPT (%)',
            'Analisis Elastisitas IPM terhadap Tingkat Pengangguran', '#D97706'
        )
        st.plotly_chart(fig_sc2, use_container_width=True)
        
        st.markdown(f"""
        <div class="interpretasi-container" style="border-left-color: #D97706;">
            <strong>Korelasi Struktural IPM & Pengangguran:</strong><br>
            Persamaan Estimasi Linier:
            $$y = {m2:.4f}x + {c2:.4f}$$
            Tipologi hubungan ini menggambarkan fenomena friksional pasar tenaga kerja regional, di mana peningkatan indeks modal manusia sering kali diiringi oleh selektivitas pencari kerja berpendidikan tinggi terhadap ketersediaan lapangan usaha.
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)


# --- 8. KARTU INFORMASI DAERAH EKSTREM (DENGAN LAYOUT GAJIH NATIVE) ---
st.markdown("<h3 style='color: #1E293B; font-weight: 700;'>Identifikasi Klaster Wilayah Ekstrem</h3>", unsafe_allow_html=True)

col_info1, col_info2, col_info3, col_info4 = st.columns(4)

top_ipm = df_filtered.nlargest(5, 'IPM')
bottom_ipm = df_filtered.nsmallest(5, 'IPM')
top_miskin = df_filtered.nlargest(5, 'Kemiskinan (%)')
top_tpt = df_filtered.nlargest(5, 'TPT (%)')

with col_info1:
    with st.container(border=True):
        st.markdown("<p style='font-size:13px; color:#64748B; font-weight:bold; text-transform:uppercase; margin-bottom:8px;'>🌟 5 IPM Tertinggi</p>", unsafe_allow_html=True)
        for idx, row in top_ipm.iterrows():
            st.markdown(f"<p style='margin:4px 0; font-size:14px; color:#1E293B;'>{row['Kabupaten/Kota']} <span style='color:#2563EB; font-weight:600;'>({row['IPM']:.2f})</span></p>", unsafe_allow_html=True)

with col_info2:
    with st.container(border=True):
        st.markdown("<p style='font-size:13px; color:#64748B; font-weight:bold; text-transform:uppercase; margin-bottom:8px;'>⚠️ 5 IPM Terendah</p>", unsafe_allow_html=True)
        for idx, row in bottom_ipm.iterrows():
            st.markdown(f"<p style='margin:4px 0; font-size:14px; color:#1E293B;'>{row['Kabupaten/Kota']} <span style='color:#475569; font-weight:600;'>({row['IPM']:.2f})</span></p>", unsafe_allow_html=True)

with col_info3:
    with st.container(border=True):
        st.markdown("<p style='font-size:13px; color:#64748B; font-weight:bold; text-transform:uppercase; margin-bottom:8px;'>🚨 5 Kemiskinan Tertinggi</p>", unsafe_allow_html=True)
        for idx, row in top_miskin.iterrows():
            st.markdown(f"<p style='margin:4px 0; font-size:14px; color:#1E293B;'>{row['Kabupaten/Kota']} <span style='color:#DC2626; font-weight:600;'>({row['Kemiskinan (%)']:.2f}%)</span></p>", unsafe_allow_html=True)

with col_info4:
    with st.container(border=True):
        st.markdown("<p style='font-size:13px; color:#64748B; font-weight:bold; text-transform:uppercase; margin-bottom:8px;'>💼 5 TPT Tertinggi</p>", unsafe_allow_html=True)
        for idx, row in top_tpt.iterrows():
            st.markdown(f"<p style='margin:4px 0; font-size:14px; color:#1E293B;'>{row['Kabupaten/Kota']} <span style='color:#D97706; font-weight:600;'>({row['TPT (%)']:.2f}%)</span></p>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)


# --- 9. TABEL DATA INTERAKTIF ---
st.markdown("<h3 style='color: #1E293B; font-weight: 700;'>Dataset Interaktif Wilayah</h3>", unsafe_allow_html=True)

st.dataframe(
    df_filtered,
    column_config={
        "Kabupaten/Kota": st.column_config.TextColumn("Nama Wilayah"),
        "IPM": st.column_config.NumberColumn("Indeks Pembangunan Manusia (IPM)", format="%.2f"),
        "Kemiskinan (%)": st.column_config.NumberColumn("Tingkat Kemiskinan Regional", format="%.2f%%"),
        "TPT (%)": st.column_config.NumberColumn("Tingkat Pengangguran Terbuka", format="%.2f%%")
    },
    use_container_width=True,
    hide_index=True
)

st.markdown("<br>", unsafe_allow_html=True)


# --- 10. RINGKASAN INSIGHT OTOMATIS ---
highest_ipm_row = df_filtered.loc[df_filtered['IPM'].idxmax()]
lowest_ipm_row = df_filtered.loc[df_filtered['IPM'].idxmin()]
highest_miskin_row = df_filtered.loc[df_filtered['Kemiskinan (%)'].idxmax()]
highest_tpt_row = df_filtered.loc[df_filtered['TPT (%)'].idxmax()]

st.info(f"""
Sintesis Eksekutif Kondisi Pembangunan Makro Regional:
* Capaian Indeks Pembangunan Manusia tertinggi dicatatkan oleh wilayah {highest_ipm_row['Kabupaten/Kota']} dengan nilai indeks {highest_ipm_row['IPM']:.2f}.
* Nilai minimum Indeks Pembangunan Manusia berada pada wilayah {lowest_ipm_row['Kabupaten/Kota']} dengan nilai indeks {lowest_ipm_row['IPM']:.2f}.
* Tantangan pengentasan kemiskinan tertinggi teridentifikasi di wilayah {highest_miskin_row['Kabupaten/Kota']} dengan proporsi populasi miskin sebesar {highest_miskin_row['Kemiskinan (%)']:.2f}%.
* Tekanan pasar kerja berupa Tingkat Pengangguran Terbuka tertinggi berada di wilayah {highest_tpt_row['Kabupaten/Kota']} dengan rasio sebesar {highest_tpt_row['TPT (%)']:.2f}%.
""")


# --- 11. FOOTER DASHBOARD ---
st.markdown("""
<div style="text-align: center; border-top: 1px solid #E2E8F0; padding-top: 20px; margin-top: 60px; padding-bottom: 20px;">
    <p style="font-size: 13px; color: #64748B; margin: 0;">Sumber Informasi Teknis: Badan Pusat Statistik Provinsi Aceh</p>
    <p style="font-size: 11px; color: #94A3B8; margin: 4px 0 0 0;">Infrastruktur Aplikasi Berbasis Python, Plotly, dan Streamlit Engine</p>
</div>
""", unsafe_allow_html=True)
