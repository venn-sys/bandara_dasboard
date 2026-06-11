import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# KONFIGURASI HALAMAN
# ==================================================
st.set_page_config(
    page_title="Analisis Dataset Penerbangan Bandara",
    page_icon="✈️",
    layout="wide"
)

# ==================================================
# CUSTOM CSS
# ==================================================
st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #e5e7eb;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
}

section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

section[data-testid="stSidebar"] * {
    color: white;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data
def load_data():
    df = pd.read_csv("DATASET BANDARA.csv")

    df["Tanggal_Penerbangan"] = pd.to_datetime(
        df["Tanggal_Penerbangan"],
        errors="coerce"
    )

    return df


df = load_data()

# ==================================================
# SIDEBAR FILTER
# ==================================================
st.sidebar.title("🔍 Filter Data")

kelas = st.sidebar.multiselect(
    "Kelas Kabin",
    options=df["Kelas_Kabin"].unique(),
    default=df["Kelas_Kabin"].unique()
)

status = st.sidebar.multiselect(
    "Status Penerbangan",
    options=df["Status_Penerbangan"].unique(),
    default=df["Status_Penerbangan"].unique()
)

filtered = df[
    (df["Kelas_Kabin"].isin(kelas))
    &
    (df["Status_Penerbangan"].isin(status))
]

# ==================================================
# HEADER
# ==================================================
st.title("✈️ Analisis Dataset Penerbangan Bandara")

st.markdown("""
### Dashboard Berbasis Python

Dashboard ini digunakan untuk memvisualisasikan dan menganalisis dataset penerbangan
berdasarkan jumlah tiket, pendapatan, status penerbangan, harga tiket,
kepuasan pelanggan, dan keterlambatan penerbangan.
""")

st.markdown("---")

# ==================================================
# KPI
# ==================================================
total_tiket = len(filtered)
total_pendapatan = filtered["Harga_Tiket_IDR"].sum()
avg_rating = filtered["Rating_Kepuasan"].mean()
avg_delay = filtered["Waktu_Delay_Menit"].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🎫 Total Tiket",
        f"{total_tiket:,}"
    )

with col2:
    st.metric(
        "💰 Total Pendapatan",
        f"Rp {total_pendapatan/1_000_000_000:.2f} M"
    )

with col3:
    st.metric(
        "⭐ Rata-rata Rating",
        f"{avg_rating:.2f}"
    )

with col4:
    st.metric(
        "⏱️ Rata-rata Delay",
        f"{avg_delay:.2f} Menit"
    )

# ==================================================
# RINGKASAN
# ==================================================
st.info(
    f"""
    📊 Hasil filter menunjukkan **{total_tiket:,} data penerbangan**.

    💰 Total pendapatan sebesar **Rp {total_pendapatan:,.0f}**.

    ⭐ Nilai rata-rata kepuasan pelanggan adalah **{avg_rating:.2f}**.

    ⏱️ Rata-rata keterlambatan penerbangan tercatat **{avg_delay:.2f} menit**.
    """
)

# ==================================================
# GRAFIK BARIS 1
# ==================================================
c1, c2 = st.columns(2)

with c1:

    rute = filtered["Rute"].value_counts().head(10).reset_index()
    rute.columns = ["Rute", "Jumlah"]

    fig = px.bar(
        rute,
        x="Rute",
        y="Jumlah",
        color="Jumlah",
        text="Jumlah",
        color_continuous_scale="Blues",
        title="Top 10 Rute Penerbangan"
    )

    fig.update_layout(
        xaxis_title="Rute",
        yaxis_title="Jumlah Tiket"
    )

    st.plotly_chart(fig, width="stretch")

with c2:

    fig = px.pie(
        filtered,
        names="Status_Penerbangan",
        hole=0.45,
        title="Distribusi Status Penerbangan",
        color="Status_Penerbangan",
        color_discrete_map={
            "On Time": "green",
            "Delayed": "orange",
            "Cancelled": "red"
        }
    )

    st.plotly_chart(fig, width="stretch")

# ==================================================
# GRAFIK BARIS 2
# ==================================================
c3, c4 = st.columns(2)

with c3:

    fig = px.histogram(
        filtered,
        x="Harga_Tiket_IDR",
        color="Kelas_Kabin",
        nbins=30,
        barmode="overlay",
        opacity=0.75,
        title="Distribusi Harga Tiket Berdasarkan Kelas Kabin"
    )

    fig.update_layout(
        xaxis_title="Harga Tiket (Rp)",
        yaxis_title="Frekuensi"
    )

    st.plotly_chart(fig, width="stretch")

with c4:

    fig = px.box(
        filtered,
        x="Kelas_Kabin",
        y="Harga_Tiket_IDR",
        color="Kelas_Kabin",
        title="Sebaran Harga Tiket Menurut Kelas Kabin"
    )

    fig.update_layout(
        xaxis_title="Kelas Kabin",
        yaxis_title="Harga Tiket (Rp)"
    )

    st.plotly_chart(fig, width="stretch")

# ==================================================
# TREND PENDAPATAN
# ==================================================
if not filtered["Tanggal_Penerbangan"].isna().all():

    harian = (
        filtered
        .groupby("Tanggal_Penerbangan")["Harga_Tiket_IDR"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        harian,
        x="Tanggal_Penerbangan",
        y="Harga_Tiket_IDR",
        markers=True,
        title="Tren Pendapatan Penerbangan"
    )

    fig.update_layout(
        xaxis_title="Tanggal Penerbangan",
        yaxis_title="Pendapatan (Rp)"
    )

    st.plotly_chart(fig, width="stretch")

# ==================================================
# DATA DETAIL
# ==================================================
st.markdown("---")

st.subheader("📋 Data Detail Penerbangan")

st.dataframe(
    filtered,
    width="stretch",
    hide_index=True
)