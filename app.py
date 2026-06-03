import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. PAGE CONFIG ---
st.set_page_config(
    layout="wide",
    page_title="Aceh Regional Stats",
    page_icon="🏛️",
    initial_sidebar_state="expanded"
)

# --- Inject CSS dari file eksternal ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# --- Inject Google Fonts + Custom CSS tambahan ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


# --- 2. LOAD DATA ---
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
                st.error(f"Kolom penting '{col}' tidak ditemukan.")
                st.stop()

        df.dropna(subset=['Kabupaten/Kota'], inplace=True)
        df['Kabupaten/Kota'] = df['Kabupaten/Kota'].str.strip()

        for col in ['IPM', 'Kemiskinan (%)', 'TPT (%)']:
            df[col] = df[col].astype(str).str.replace('%', '').str.replace(',', '.').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(subset=['IPM', 'Kemiskinan (%)', 'TPT (%)'], inplace=True)
        return df

    except Exception as e:
        st.error(f"Gagal memuat data. Detail: {e}")
        st.stop()


df_raw = load_data()


# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-logo">🏛️</div>
        <div>
            <div class="sidebar-title">ACEH STATS</div>
            <div class="sidebar-subtitle">Regional Analytics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-label">FILTER DATA</div>', unsafe_allow_html=True)

    daftar_daerah = sorted(df_raw['Kabupaten/Kota'].unique())

    if 'selected_daerah' not in st.session_state:
        st.session_state['selected_daerah'] = []

    selected_daerah = st.multiselect(
        "Pilih Kabupaten/Kota:",
        options=daftar_daerah,
        default=st.session_state['selected_daerah'],
        key="daerah_filter",
        placeholder="Semua daerah ditampilkan..."
    )

    if st.button("↺  Reset Filter", use_container_width=True):
        st.session_state['daerah_filter'] = []
        st.rerun()

    st.markdown('<div class="sidebar-section-label">TAMPILAN GRAFIK</div>', unsafe_allow_html=True)
    chart_style = st.radio(
        "Mode warna grafik:",
        ["Gradient", "Solid", "Monokrom"],
        horizontal=False
    )

    show_trendline = st.toggle("Tampilkan Garis Tren", value=True)
    show_labels = st.toggle("Label Nilai pada Bar", value=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px; color:#94a3b8; text-align:center; line-height:1.6;">
        Sumber: BPS Provinsi Aceh<br>
        Dibuat dengan Python & Streamlit
    </div>
    """, unsafe_allow_html=True)


# Filter logic
if selected_daerah:
    df_filtered = df_raw[df_raw['Kabupaten/Kota'].isin(selected_daerah)].copy()
else:
    df_filtered = df_raw.copy()


# --- Fungsi warna berdasarkan pilihan ---
def get_color_scale(indicator, style):
    scales = {
        "Gradient": {"IPM": "Blues", "Kemiskinan (%)": "Reds", "TPT (%)": "Oranges"},
        "Solid": {"IPM": [[0, "#1e40af"], [1, "#1e40af"]],
                  "Kemiskinan (%)": [[0, "#dc2626"], [1, "#dc2626"]],
                  "TPT (%)": [[0, "#d97706"], [1, "#d97706"]]},
        "Monokrom": {"IPM": "Greys", "Kemiskinan (%)": "Greys", "TPT (%)": "Greys"}
    }
    return scales.get(style, scales["Gradient"]).get(indicator, "Blues")


# --- 4. HEADER UTAMA ---
total_filtered = len(df_filtered)
total_all = len(df_raw)

st.markdown(f"""
<div class="main-header">
    <div class="header-eyebrow">PROVINSI ACEH • INDONESIA</div>
    <h1 class="header-title">Dashboard Statistik<br><span class="header-accent">Regional & Area Kecil</span></h1>
    <p class="header-desc">Analisis komparatif kondisi pembangunan wilayah berdasarkan IPM, Kemiskinan, dan Tingkat Pengangguran Terbuka (TPT)</p>
    <div class="header-badge">
        Menampilkan <strong>{total_filtered}</strong> dari <strong>{total_all}</strong> Kabupaten/Kota
    </div>
</div>
""", unsafe_allow_html=True)


# --- 5. KPI CARDS ---
avg_ipm = df_filtered['IPM'].mean()
avg_kemiskinan = df_filtered['Kemiskinan (%)'].mean()
avg_tpt = df_filtered['TPT (%)'].mean()

max_ipm_row = df_filtered.loc[df_filtered['IPM'].idxmax()]
min_ipm_row = df_filtered.loc[df_filtered['IPM'].idxmin()]
max_miskin_row = df_filtered.loc[df_filtered['Kemiskinan (%)'].idxmax()]
max_tpt_row = df_filtered.loc[df_filtered['TPT (%)'].idxmax()]

col1, col2, col3, col4, col5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.2])

with col1:
    st.markdown(f"""
    <div class="kpi-card kpi-blue">
        <div class="kpi-icon">📈</div>
        <div class="kpi-label">RATA-RATA IPM</div>
        <div class="kpi-value">{avg_ipm:.2f}</div>
        <div class="kpi-sub">↑ Tertinggi: <b>{max_ipm_row['Kabupaten/Kota']}</b> ({max_ipm_row['IPM']:.2f})</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card kpi-red">
        <div class="kpi-icon">🏚️</div>
        <div class="kpi-label">RATA-RATA KEMISKINAN</div>
        <div class="kpi-value">{avg_kemiskinan:.2f}<span class="kpi-unit">%</span></div>
        <div class="kpi-sub">↑ Tertinggi: <b>{max_miskin_row['Kabupaten/Kota']}</b> ({max_miskin_row['Kemiskinan (%)']:.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card kpi-amber">
        <div class="kpi-icon">💼</div>
        <div class="kpi-label">RATA-RATA TPT</div>
        <div class="kpi-value">{avg_tpt:.2f}<span class="kpi-unit">%</span></div>
        <div class="kpi-sub">↑ Tertinggi: <b>{max_tpt_row['Kabupaten/Kota']}</b> ({max_tpt_row['TPT (%)']:.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card kpi-green">
        <div class="kpi-icon">🌟</div>
        <div class="kpi-label">IPM TERTINGGI</div>
        <div class="kpi-value-sm">{max_ipm_row['Kabupaten/Kota']}</div>
        <div class="kpi-sub">Nilai IPM: <b>{max_ipm_row['IPM']:.2f}</b></div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card kpi-slate">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-label">IPM TERENDAH</div>
        <div class="kpi-value-sm">{min_ipm_row['Kabupaten/Kota']}</div>
        <div class="kpi-sub">Nilai IPM: <b>{min_ipm_row['IPM']:.2f}</b></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- 6. CHART SECTION ---
st.markdown('<div class="section-header"><span class="section-number">01</span> Urutan & Peringkat Indikator</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊  Indeks Pembangunan Manusia (IPM)", "🛑  Tingkat Kemiskinan (%)", "💼  Tingkat Pengangguran (TPT %)"])

plotly_layout_base = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="DM Sans, sans-serif", color="#e2e8f0"),
    title_font=dict(family="Syne, sans-serif", size=18, color="#f8fafc"),
    margin=dict(l=20, r=120, t=50, b=20),
    xaxis=dict(gridcolor='rgba(148,163,184,0.1)', zerolinecolor='rgba(148,163,184,0.2)'),
    yaxis=dict(gridcolor='rgba(0,0,0,0)', tickfont=dict(size=11))
)

with tab1:
    df_sorted = df_filtered.sort_values('IPM', ascending=True)
    fig = px.bar(
        df_sorted, x='IPM', y='Kabupaten/Kota', orientation='h',
        text='IPM' if show_labels else None,
        color='IPM',
        color_continuous_scale=get_color_scale("IPM", chart_style),
        height=max(500, len(df_sorted) * 28)
    )
    fig.update_traces(
        texttemplate='%{text:.2f}' if show_labels else None,
        textposition='outside',
        textfont=dict(size=10, color="#94a3b8"),
        marker_line_width=0
    )
    fig.update_layout(**plotly_layout_base,
        title="Peringkat Indeks Pembangunan Manusia (IPM)",
        coloraxis_showscale=False,
        xaxis_title="Indeks IPM",
        yaxis_title=""
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    df_sorted = df_filtered.sort_values('Kemiskinan (%)', ascending=True)
    fig = px.bar(
        df_sorted, x='Kemiskinan (%)', y='Kabupaten/Kota', orientation='h',
        text='Kemiskinan (%)' if show_labels else None,
        color='Kemiskinan (%)',
        color_continuous_scale=get_color_scale("Kemiskinan (%)", chart_style),
        height=max(500, len(df_sorted) * 28)
    )
    fig.update_traces(
        texttemplate='%{text:.2f}%' if show_labels else None,
        textposition='outside',
        textfont=dict(size=10, color="#94a3b8"),
        marker_line_width=0
    )
    fig.update_layout(**plotly_layout_base,
        title="Persentase Tingkat Kemiskinan per Kabupaten/Kota",
        coloraxis_showscale=False,
        xaxis_title="Persentase (%)",
        yaxis_title=""
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    df_sorted = df_filtered.sort_values('TPT (%)', ascending=True)
    fig = px.bar(
        df_sorted, x='TPT (%)', y='Kabupaten/Kota', orientation='h',
        text='TPT (%)' if show_labels else None,
        color='TPT (%)',
        color_continuous_scale=get_color_scale("TPT (%)", chart_style),
        height=max(500, len(df_sorted) * 28)
    )
    fig.update_traces(
        texttemplate='%{text:.2f}%' if show_labels else None,
        textposition='outside',
        textfont=dict(size=10, color="#94a3b8"),
        marker_line_width=0
    )
    fig.update_layout(**plotly_layout_base,
        title="Tingkat Pengangguran Terbuka (TPT) per Kabupaten/Kota",
        coloraxis_showscale=False,
        xaxis_title="Persentase (%)",
        yaxis_title=""
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- 7. SCATTER / KORELASI ---
st.markdown('<div class="section-header"><span class="section-number">02</span> Analisis Korelasi Antar Indikator</div>', unsafe_allow_html=True)

col_sc1, col_sc2 = st.columns(2)

def create_scatter(data, x_col, y_col, color_pt, color_line, title):
    x = data[x_col].values
    y = data[y_col].values

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='markers+text',
        text=data['Kabupaten/Kota'],
        textposition="top center",
        textfont=dict(size=9, color="rgba(148,163,184,0.7)"),
        hovertemplate='<b>%{text}</b><br>' + x_col + ': %{x:.2f}<br>' + y_col + ': %{y:.2f}<extra></extra>',
        name='Daerah',
        marker=dict(
            size=14,
            color=x,
            colorscale=[[0, color_pt + "60"], [1, color_pt]],
            showscale=False,
            line=dict(width=1.5, color='rgba(255,255,255,0.3)')
        )
    ))

    if show_trendline and len(x) > 1:
        m, c = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = m * x_line + c
        r = np.corrcoef(x, y)[0, 1]

        fig.add_trace(go.Scatter(
            x=x_line, y=y_line,
            mode='lines',
            name=f'Tren (r={r:.2f})',
            line=dict(color=color_line, width=2.5, dash='dot')
        ))

        # Anotasi korelasi
        fig.add_annotation(
            x=0.97, y=0.97, xref="paper", yref="paper",
            text=f"<b>r = {r:.3f}</b>",
            showarrow=False,
            font=dict(size=14, color=color_pt),
            bgcolor="rgba(15,23,42,0.8)",
            bordercolor=color_pt,
            borderwidth=1,
            borderpad=6
        )

    fig.update_layout(
        **plotly_layout_base,
        title=title,
        xaxis_title=x_col,
        yaxis_title=y_col,
        height=480,
        showlegend=False
    )
    return fig

with col_sc1:
    fig1 = create_scatter(df_filtered, 'IPM', 'Kemiskinan (%)', '#3b82f6', '#93c5fd', 'IPM vs Kemiskinan')
    st.plotly_chart(fig1, use_container_width=True)

    x = df_filtered['IPM'].values
    y = df_filtered['Kemiskinan (%)'].values
    if len(x) > 1:
        m, c = np.polyfit(x, y, 1)
        r = np.corrcoef(x, y)[0, 1]
        arah = "negatif (berlawanan)" if m < 0 else "positif (searah)"
        kekuatan = "sangat kuat" if abs(r) > 0.7 else ("cukup kuat" if abs(r) > 0.4 else "lemah")
        st.markdown(f"""
        <div class="insight-box insight-blue">
            <div class="insight-label">📐 Model Regresi</div>
            <div class="insight-formula">ŷ = {m:.4f}x + ({c:.4f})</div>
            <hr class="insight-divider">
            <div class="insight-text">
                Korelasi bersifat <strong>{arah}</strong> dengan kekuatan <strong>{kekuatan}</strong> (r = {r:.3f}).
                Setiap kenaikan 1 poin IPM diperkirakan mengubah kemiskinan sebesar <strong>{abs(m):.2f}%</strong>.
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_sc2:
    fig2 = create_scatter(df_filtered, 'IPM', 'TPT (%)', '#f59e0b', '#fcd34d', 'IPM vs Pengangguran (TPT)')
    st.plotly_chart(fig2, use_container_width=True)

    x = df_filtered['IPM'].values
    y = df_filtered['TPT (%)'].values
    if len(x) > 1:
        m, c = np.polyfit(x, y, 1)
        r = np.corrcoef(x, y)[0, 1]
        arah = "negatif (berlawanan)" if m < 0 else "positif (searah)"
        kekuatan = "sangat kuat" if abs(r) > 0.7 else ("cukup kuat" if abs(r) > 0.4 else "lemah")
        st.markdown(f"""
        <div class="insight-box insight-amber">
            <div class="insight-label">📐 Model Regresi</div>
            <div class="insight-formula">ŷ = {m:.4f}x + ({c:.4f})</div>
            <hr class="insight-divider">
            <div class="insight-text">
                Korelasi bersifat <strong>{arah}</strong> dengan kekuatan <strong>{kekuatan}</strong> (r = {r:.3f}).
                Koefisien slope <strong>{m:.4f}</strong> mencerminkan elastisitas penyerapan tenaga kerja terdidik di wilayah Aceh.
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- 8. SCATTER MATRIX BONUS ---
st.markdown('<div class="section-header"><span class="section-number">03</span> Distribusi & Persebaran Data</div>', unsafe_allow_html=True)

col_d1, col_d2 = st.columns([1.6, 1])

with col_d1:
    # Bubble chart: IPM (x) vs Kemiskinan (y), ukuran = TPT
    fig_bubble = go.Figure()
    fig_bubble.add_trace(go.Scatter(
        x=df_filtered['IPM'],
        y=df_filtered['Kemiskinan (%)'],
        mode='markers+text',
        text=df_filtered['Kabupaten/Kota'],
        textposition='top center',
        textfont=dict(size=8.5, color='rgba(148,163,184,0.6)'),
        hovertemplate='<b>%{text}</b><br>IPM: %{x:.2f}<br>Kemiskinan: %{y:.2f}%<br>TPT: %{marker.size:.2f}%<extra></extra>',
        marker=dict(
            size=df_filtered['TPT (%)'],
            sizemode='area',
            sizeref=2. * df_filtered['TPT (%)'].max() / (40.**2),
            sizemin=6,
            color=df_filtered['IPM'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="IPM",
                tickfont=dict(color="#94a3b8"),
                title_font=dict(color="#94a3b8")
            ),
            line=dict(width=1, color='rgba(255,255,255,0.2)')
        )
    ))
    fig_bubble.update_layout(
        **plotly_layout_base,
        title="Bubble Chart: IPM vs Kemiskinan (Ukuran = TPT)",
        xaxis_title="Indeks Pembangunan Manusia (IPM)",
        yaxis_title="Tingkat Kemiskinan (%)",
        height=500
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

with col_d2:
    # Radar / statistik ringkasan
    stats_data = {
        'Indikator': ['IPM', 'Kemiskinan (%)', 'TPT (%)'],
        'Min': [df_filtered['IPM'].min(), df_filtered['Kemiskinan (%)'].min(), df_filtered['TPT (%)'].min()],
        'Max': [df_filtered['IPM'].max(), df_filtered['Kemiskinan (%)'].max(), df_filtered['TPT (%)'].max()],
        'Rata-rata': [df_filtered['IPM'].mean(), df_filtered['Kemiskinan (%)'].mean(), df_filtered['TPT (%)'].mean()],
        'Std Dev': [df_filtered['IPM'].std(), df_filtered['Kemiskinan (%)'].std(), df_filtered['TPT (%)'].std()]
    }

    st.markdown("""<div class="stats-table-wrapper">
        <div class="stats-table-title">📊 Statistik Deskriptif</div>
    """, unsafe_allow_html=True)

    for i, ind in enumerate(stats_data['Indikator']):
        unit = "" if ind == "IPM" else "%"
        color_cls = ["stat-blue", "stat-red", "stat-amber"][i]
        st.markdown(f"""
        <div class="stat-block {color_cls}">
            <div class="stat-name">{ind}</div>
            <div class="stat-row">
                <span class="stat-badge">Min</span><span class="stat-val">{stats_data['Min'][i]:.2f}{unit}</span>
                <span class="stat-badge">Max</span><span class="stat-val">{stats_data['Max'][i]:.2f}{unit}</span>
            </div>
            <div class="stat-row">
                <span class="stat-badge">Avg</span><span class="stat-val">{stats_data['Rata-rata'][i]:.2f}{unit}</span>
                <span class="stat-badge">σ</span><span class="stat-val">{stats_data['Std Dev'][i]:.2f}{unit}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- 9. LEADERBOARD SECTION ---
st.markdown('<div class="section-header"><span class="section-number">04</span> Daerah Berkinerja Ekstrem</div>', unsafe_allow_html=True)

col_r1, col_r2, col_r3, col_r4 = st.columns(4)

def render_rank_card(title, icon, color, rows, col_name, unit="", reverse=False):
    items_html = ""
    medals = ["🥇", "🥈", "🥉", "④", "⑤"]
    for i, (_, row) in enumerate(rows.iterrows()):
        val = f"{row[col_name]:.2f}{unit}"
        items_html += f"""
        <div class="rank-item">
            <span class="rank-medal">{medals[i]}</span>
            <div class="rank-info">
                <div class="rank-name">{row['Kabupaten/Kota']}</div>
                <div class="rank-val" style="color:{color}">{val}</div>
            </div>
        </div>
        """
    return f"""
    <div class="rank-card-new" style="border-top: 3px solid {color}">
        <div class="rank-card-header">{icon} {title}</div>
        {items_html}
    </div>
    """

with col_r1:
    top5 = df_filtered.nlargest(5, 'IPM')
    st.markdown(render_rank_card("Top IPM", "🌟", "#3b82f6", top5, "IPM"), unsafe_allow_html=True)

with col_r2:
    bot5 = df_filtered.nsmallest(5, 'IPM')
    st.markdown(render_rank_card("IPM Terendah", "⚠️", "#64748b", bot5, "IPM"), unsafe_allow_html=True)

with col_r3:
    top_miskin = df_filtered.nlargest(5, 'Kemiskinan (%)')
    st.markdown(render_rank_card("Kemiskinan Tertinggi", "🚨", "#ef4444", top_miskin, "Kemiskinan (%)", "%"), unsafe_allow_html=True)

with col_r4:
    top_tpt = df_filtered.nlargest(5, 'TPT (%)')
    st.markdown(render_rank_card("TPT Tertinggi", "💼", "#f59e0b", top_tpt, "TPT (%)", "%"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- 10. DATA TABLE ---
st.markdown('<div class="section-header"><span class="section-number">05</span> Dataset Interaktif</div>', unsafe_allow_html=True)

# Tambah kolom skor komposit sederhana
df_display = df_filtered.copy()
df_display['Skor Komposit*'] = (
    (df_display['IPM'] / df_display['IPM'].max() * 0.5) +
    ((1 - df_display['Kemiskinan (%)'] / df_display['Kemiskinan (%)'].max()) * 0.3) +
    ((1 - df_display['TPT (%)'] / df_display['TPT (%)'].max()) * 0.2)
).round(4)

df_display = df_display.sort_values('Skor Komposit*', ascending=False).reset_index(drop=True)

st.dataframe(
    df_display,
    column_config={
        "Kabupaten/Kota": st.column_config.TextColumn("📍 Kabupaten/Kota", width="medium"),
        "IPM": st.column_config.ProgressColumn("📈 IPM", format="%.2f", min_value=0, max_value=100),
        "Kemiskinan (%)": st.column_config.ProgressColumn("🏚️ Kemiskinan (%)", format="%.2f%%", min_value=0, max_value=50),
        "TPT (%)": st.column_config.ProgressColumn("💼 TPT (%)", format="%.2f%%", min_value=0, max_value=20),
        "Skor Komposit*": st.column_config.NumberColumn("⭐ Skor Komposit", format="%.4f", help="*Skor gabungan: 50% IPM + 30% non-Kemiskinan + 20% non-TPT")
    },
    use_container_width=True,
    hide_index=False,
    height=420
)

st.markdown("""
<div style="font-size:11px; color:#64748b; margin-top:6px;">
    * Skor Komposit = Gabungan IPM (bobot 50%), kebalikan Kemiskinan (30%), dan kebalikan TPT (20%). Nilai lebih tinggi = kondisi pembangunan lebih baik.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- 11. RINGKASAN EKSEKUTIF ---
st.markdown('<div class="section-header"><span class="section-number">06</span> Ringkasan Eksekutif</div>', unsafe_allow_html=True)

highest_ipm_row = df_filtered.loc[df_filtered['IPM'].idxmax()]
lowest_ipm_row = df_filtered.loc[df_filtered['IPM'].idxmin()]
highest_miskin_row = df_filtered.loc[df_filtered['Kemiskinan (%)'].idxmax()]
highest_tpt_row = df_filtered.loc[df_filtered['TPT (%)'].idxmax()]
gap_ipm = highest_ipm_row['IPM'] - lowest_ipm_row['IPM']

col_e1, col_e2 = st.columns(2)

with col_e1:
    st.markdown(f"""
    <div class="exec-card">
        <div class="exec-title">📋 Temuan Utama</div>
        <ul class="exec-list">
            <li>Rentang IPM antar kabupaten/kota mencapai <strong>{gap_ipm:.2f} poin</strong>, menunjukkan disparitas pembangunan yang signifikan.</li>
            <li><strong>{highest_ipm_row['Kabupaten/Kota']}</strong> memimpin dengan IPM tertinggi ({highest_ipm_row['IPM']:.2f}), sementara <strong>{lowest_ipm_row['Kabupaten/Kota']}</strong> mencatat IPM terendah ({lowest_ipm_row['IPM']:.2f}).</li>
            <li><strong>{highest_miskin_row['Kabupaten/Kota']}</strong> memiliki beban kemiskinan tertinggi ({highest_miskin_row['Kemiskinan (%)']:.2f}%), memerlukan intervensi kebijakan prioritas.</li>
            <li><strong>{highest_tpt_row['Kabupaten/Kota']}</strong> mencatat TPT tertinggi ({highest_tpt_row['TPT (%)']:.2f}%), mengindikasikan tekanan pasar tenaga kerja lokal.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_e2:
    st.markdown(f"""
    <div class="exec-card">
        <div class="exec-title">💡 Rekomendasi Kebijakan</div>
        <ul class="exec-list">
            <li>Fokuskan program pengentasan kemiskinan dan peningkatan IPM di daerah dengan skor komposit terendah melalui pendekatan area kecil (small area estimation).</li>
            <li>Perkuat program vokasi dan pelatihan kerja di kabupaten dengan TPT tinggi untuk mempercepat penyerapan tenaga kerja.</li>
            <li>Dorong pemerataan akses layanan dasar (pendidikan & kesehatan) untuk mempersempit gap IPM antar wilayah.</li>
            <li>Manfaatkan kekuatan daerah IPM tinggi sebagai pusat pertumbuhan ekonomi regional yang dapat menarik investasi.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# --- FOOTER ---
st.markdown("""
<div class="footer">
    <div class="footer-brand">ACEH REGIONAL STATS</div>
    <div class="footer-info">
        Sumber data: <strong>Badan Pusat Statistik (BPS) Provinsi Aceh</strong> &nbsp;|&nbsp;
        Dibangun dengan <strong>Python · Streamlit · Plotly</strong>
    </div>
    <div class="footer-note">Dashboard ini bersifat analitis dan tidak merepresentasikan posisi resmi pemerintah.</div>
</div>
""", unsafe_allow_html=True)
