import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utide import solve, reconstruct
from datetime import datetime

# Optional dependency check
try:
    import matplotlib
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# ==========================================
# CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="MarineTide Analytics | Oceanography Pro",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
.main { background-color: #f4f7f6; font-family: 'Inter', sans-serif; }

.hero-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    padding: 30px;
    border-radius: 12px;
    color: white;
    margin-bottom: 25px;
}

.result-card {
    background-color: white;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 25px;
    border: 1px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
@st.cache_data
def generate_template():
    waktu = pd.date_range(
        start=datetime.now().strftime("%Y-%m-%d"),
        periods=24 * 30,
        freq="h"
    )

    t = np.arange(len(waktu))

    elev = (
        1.5
        + 0.6 * np.sin(2 * np.pi * t / 12.42)
        + 0.3 * np.sin(2 * np.pi * t / 12.0)
        + 0.2 * np.sin(2 * np.pi * t / 23.93)
        + 0.15 * np.sin(2 * np.pi * t / 25.82)
        + 0.02 * np.random.randn(len(t))
    )

    return pd.DataFrame({
        "Waktu": waktu,
        "Elevasi (m)": elev
    })

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("## 🌊 MarineTide")

    st.markdown("### 📂 Data Input")
    file = st.file_uploader("Upload Data (.csv / .xlsx)", type=["csv", "xlsx"])

    with st.expander("📥 Unduh Template"):
        df_temp = generate_template()
        csv = df_temp.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "template_pasut.csv")

    st.markdown("### ⚙️ Parameter")
    hari_prediksi = st.slider("Durasi Prediksi (Hari)", 1, 60, 14)
    lintang = st.number_input("Lintang", value=-6.0)

# ==========================================
# MAIN
# ==========================================
if not file:
    st.markdown("""
    <div class="hero-card">
        <h1>Sistem Pengolahan Data Pasut</h1>
        <p>Upload data untuk memulai analisis</p>
    </div>
    """, unsafe_allow_html=True)

else:
    try:
        # LOAD DATA
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        df = df.iloc[:, :2]
        df.columns = ["Waktu", "Elevasi"]
        df["Waktu"] = pd.to_datetime(df["Waktu"])
        df = df.dropna().sort_values("Waktu")

        # PROSES
        with st.spinner("Processing..."):
            t0 = df["Waktu"].min()
            t_end = df["Waktu"].max()
            epoch_obj = t0.to_pydatetime()

            time_days_obs = (df["Waktu"] - t0).dt.total_seconds() / 86400.0

            waktu_prediksi = pd.date_range(
                start=t_end,
                periods=24 * hari_prediksi,
                freq="h"
            )

            time_days_pred = (waktu_prediksi - t0).total_seconds() / 86400.0

            elev = df["Elevasi"].values.astype(float)
            mean_elev = np.mean(elev)

            coef = solve(
                time_days_obs,
                elev - mean_elev,
                lat=lintang,
                epoch=epoch_obj,
                constit=['M2','S2','N2','K1','O1','M4','MS4'],
                method='ols',
                verbose=False
            )

            recon = reconstruct(time_days_pred, coef, epoch=epoch_obj)
            model_pred = recon.h + mean_elev

        # FORMZAHL
        h = dict(zip(coef.name, coef.A))
        M2, S2 = h.get('M2', 0), h.get('S2', 0)
        K1, O1 = h.get('K1', 0), h.get('O1', 0)
        F = (K1 + O1) / (M2 + S2) if (M2 + S2) > 0 else 0

        # METRICS
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("MSL", f"{mean_elev:.2f}")
        col2.metric("M2", f"{M2:.3f}")
        col3.metric("S2", f"{S2:.3f}")
        col4.metric("K1", f"{K1:.3f}")
        col5.metric("F", f"{F:.3f}")

        # TABS
        tab_grafik, tab_data = st.tabs(["Grafik", "Data"])

        # GRAFIK
        with tab_grafik:
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df["Waktu"],
                y=df["Elevasi"],
                name="Observasi"
            ))

            fig.add_trace(go.Scatter(
                x=waktu_prediksi,
                y=model_pred,
                name="Prediksi"
            ))

            st.plotly_chart(fig, use_container_width=True)

        # DATA
        with tab_data:
            res_df = pd.DataFrame({
                "Konstanta": coef.name,
                "Amplitudo (m)": coef.A,
                "Phase": coef.g,
                "Frekuensi": coef.aux.frq
            })

            if HAS_MPL:
                styled_df = res_df.style.background_gradient(
                    cmap='Blues',
                    subset=['Amplitudo (m)']
                ).format(precision=4)
            else:
                styled_df = res_df.round(4)
                st.caption("⚠️ Matplotlib tidak tersedia")

            st.dataframe(
                styled_df,
                use_container_width=True,
                height=400
            )

    except Exception as e:
        st.error("Terjadi kesalahan pada data")
        st.exception(e)
