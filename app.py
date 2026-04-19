import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utide import solve, reconstruct
from datetime import datetime

# Cek ketersediaan Matplotlib untuk styling tabel
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

# --- CUSTOM CSS FOR ELEGANT MARINE THEME ---
st.markdown("""
    <style>
    /* Global Background & Fonts */
    .main { background-color: #f4f7f6; font-family: 'Inter', sans-serif; }
    
    /* Header Gradient Card */
    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 30px; 
        border-radius: 12px; 
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric Cards Styling */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #2563eb;
        text-align: center;
    }
    [data-testid="stMetricLabel"] { font-weight: 600; color: #475569; font-size: 14px; }
    [data-testid="stMetricValue"] { color: #0f172a; font-weight: 800; font-size: 24px; }
    
    /* Custom Result Card */
    .result-card {
        background-color: white; 
        padding: 25px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
        border: 1px solid #e2e8f0;
    }
    
    /* Sidebar Styling Tweak */
    .css-1d391kg { background-color: #ffffff; }
    
    /* Button Styling */
    .stButton>button { 
        background-color: #1e3a8a; 
        color: white; 
        font-weight: 600; 
        border-radius: 8px; 
        transition: all 0.3s;
    }
    .stButton>button:hover { background-color: #1e40af; border-color: #1e40af; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
@st.cache_data
def generate_template():
    # Menggunakan freq="h" (kecil) agar kompatibel dengan Pandas versi terbaru
    waktu = pd.date_range(start=datetime.now().strftime("%Y-%m-%d"), periods=24*30, freq="h")
    t = np.arange(len(waktu))
    elev = 1.5 + 0.6*np.sin(2*np.pi*t/12.42) + 0.3*np.sin(2*np.pi*t/12.0) + \
           0.2*np.sin(2*np.pi*t/23.93) + 0.15*np.sin(2*np.pi*t/25.82) + 0.02*np.random.randn(len(t))
    return pd.DataFrame({"Waktu": waktu, "Elevasi (m)": elev})

# ==========================================
# SIDEBAR CONTROL PANEL
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #0f172a; margin-top: 10px; font-weight: 800;">🌊 MarineTide</h2>
            <p style="color: #64748b; font-size: 14px; margin-top: -10px;">Data Processing Engine</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 📂 Data Input")
    file = st.file_uploader("Upload Data (.csv / .xlsx)", type=["csv", "xlsx"])
    
    with st.expander("📥 Unduh Template Format"):
        st.caption("Gunakan format ini agar terbaca oleh sistem pengolahan.")
        df_temp = generate_template()
        csv = df_temp.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download template_pasut.csv", data=csv, file_name="template_pasut.csv", mime="text/csv")

    st.divider()
    
    st.markdown("### ⚙️ Parameter Analisis")
    hari_prediksi = st.slider("Durasi Prediksi (Hari)", 1, 60, 14, help="Menentukan berapa lama ke depan data pasut akan diprediksi.")
    lintang = st.number_input("Lintang Lokasi (Latitude)", value=-6.0, step=0.1, format="%.2f", help="Koordinat lintang stasiun pengamatan.")
    
    st.markdown("""
        <div style="margin-top: 50px; text-align: center; font-size: 12px; color: #94a3b8;">
            &copy; 2026 Marine Data Analytics
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# MAIN DASHBOARD CONTENT
# ==========================================

# 1. Hero Section
if not file:
    st.markdown("""
        <div class="hero-card">
            <h1 style="margin: 0; font-size: 36px; font-weight: 800;">Sistem Pengolahan Data Pasang Surut</h1>
            <p style="margin: 10px 0 0 0; font-size: 18px; color: #cbd5e1; font-weight: 300;">
                Platform analisis harmonik dan klasifikasi Formzahl dengan tingkat presisi tinggi.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Berikan angka agar kolom kiri lebih lebar dari kolom kanan
    col1, col2 = st.columns() 
    
    with col1:
        st.info("👋 **Memulai Analisis:** Silakan unggah data observasi muka air laut (minimal 29 hari untuk hasil yang merepresentasikan siklus penuh) pada panel sebelah kiri.")
    with col2:
        st.success("💡 **Format yang didukung:** File CSV atau Excel dengan dua kolom utama: 'Waktu' dan 'Elevasi'.")
        
else:
    # 2. Header Status when File Uploaded
    st.markdown("""
        <div class="hero-card" style="padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="margin: 0; font-size: 24px; font-weight: 700;">Dashboard Analisis Harmonik</h2>
                    <p style="margin: 0; color: #cbd5e1; font-size: 14px;">Memproses data observasi...</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    try:
        # --- DATA PROCESSING ---
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        df = df.iloc[:, :2]
        df.columns = ["Waktu", "Elevasi"]
        df["Waktu"] = pd.to_datetime(df["Waktu"])
        df = df.dropna().sort_values("Waktu")

        with st.spinner("⏳ Menjalankan algoritma Least Squares untuk ekstraksi konstanta..."):
            t0 = df["Waktu"].min()
            t_end = df["Waktu"].max()
            epoch_obj = t0.to_pydatetime()
            
            time_days_obs = (df["Waktu"] - t0).dt.total_seconds().values / 86400.0
            # Pastikan menggunakan freq="h" di sini
            waktu_prediksi = pd.date_range(start=t_end, periods=24 * hari_prediksi, freq="h")
            time_days_pred = (waktu_prediksi - t0).total_seconds().values / 86400.0
            
            elev = df["Elevasi"].values.astype(float)
            mean_elev = np.mean(elev)
            
            # Memastikan constituen utama masuk untuk perhitungan Formzahl
            coef = solve(time_days_obs, elev - mean_elev, lat=lintang, epoch=epoch_obj,
                         constit=['M2','S2','N2','K1','O1','M4','MS4'],
                         method='ols', conf_int='linear', verbose=False)

            recon_future = reconstruct(time_days_pred, coef, epoch=epoch_obj, verbose=False)
            model_pred = recon_future.h + mean_elev

        # --- HASIL & PERHITUNGAN FORMZAHL ---
        h = dict(zip(coef.name, coef.A))
        M2, S2, K1, O1 = h.get('M2', 0), h.get('S2', 0), h.get('K1', 0), h.get('O1', 0)
        
        # Mencegah division by zero
        F = (K1 + O1) / (M2 + S2) if (M2 + S2) > 0 else 0

        # --- METRIK UTAMA ---
        st.markdown("<h3 style='color: #0f172a; font-weight: 700; font-size: 20px; margin-bottom: 15px;'>📌 Parameter Ekstraksi Utama</h3>", unsafe_allow_html=True)
        
        m1, m2, m3, m4, m5 = st.columns(5) 
        m1.metric("Mean Sea Level", f"{mean_elev:.2f} m")
        m2.metric("Amplitudo M2", f"{M2:.3f} m")
        m3.metric("Amplitudo S2", f"{S2:.3f} m")
        m4.metric("Amplitudo K1", f"{K1:.3f} m")
        
        f_color = "normal" if F <= 3.0 else "inverse"
        m5.metric("Bilangan Formzahl", f"{F:.3f}", delta_color=f_color)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- TABS PENYAJIAN DATA ---
        tab_grafik, tab_data = st.tabs(["📊 Visualisasi & Klasifikasi", "📋 Komponen Harmonik"])

        with tab_grafik:
            # KLASIFIKASI PASUT
            if F <= 0.25:
                tipe = "Harian Ganda (Semi-Diurnal)"
                desk = "Terjadi dua kali pasang dan dua kali surut dalam sehari dengan tinggi yang hampir sama."
                warna = "#0284c7" # Light Blue
                bg_warna = "#e0f2fe"
            elif F <= 1.50:
                tipe = "Campuran Condong Harian Ganda"
                desk = "Terjadi dua kali pasang dan dua kali surut, namun tinggi dan intervalnya berbeda secara signifikan."
                warna = "#059669" # Emerald
                bg_warna = "#d1fae5"
            elif F <= 3.0:
                tipe = "Campuran Condong Harian Tunggal"
                desk = "Umumnya satu kali pasang dan satu kali surut, tetapi sesekali terjadi dua kali pasang/surut."
                warna = "#d97706" # Amber
                bg_warna = "#fef3c7"
            else:
                tipe = "Harian Tunggal (Diurnal)"
                desk = "Hanya terjadi satu kali pasang dan satu kali surut dalam periode 24 jam."
                warna = "#dc2626" # Red
                bg_warna = "#fee2e2"

            # Tampilan Klasifikasi Formzahl
            st.markdown(f"""
                <div class="result-card" style="border-left: 6px solid {warna}; background-color: {bg_warna};">
                    <p style="margin:0; font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 1px;">Hasil Klasifikasi Tipe Pasut</p>
                    <h3 style="margin:5px 0 10px 0; color: {warna}; font-weight: 800; font-size: 24px;">{tipe}</h3>
                    <p style="margin:0; color: #334155; font-size: 15px; font-weight: 400;">{desk}</p>
                </div>
            """, unsafe_allow_html=True)

            # --- PLOTLY CHART OCEANGORAPHY STYLE ---
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df["Waktu"], y=df["Elevasi"], 
                name='Data Observasi', 
                mode='lines',
                line=dict(color='#94a3b8', width=1.5),
                opacity=0.7
            ))
            
            fig.add_trace(go.Scatter(
                x=waktu_prediksi, y=model_pred, 
                name='Prediksi Model (utide)', 
                mode='lines',
                line=dict(color='#2563eb', width=2),
                fill='tozeroy',
                fillcolor='rgba(37, 99, 235, 0.1)'
            ))
            
            fig.update_layout(
                title=dict(text="Kurva Elevasi Muka Air Laut", font=dict(size=18, color='#0f172a', family='Inter')),
                hovermode="x unified",
                height=500, 
                margin=dict(l=20, r=20, t=60, b=20), 
                template="plotly_white",
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor='rgba(255, 255, 255, 0.8)', bordercolor='#e2e8f0', borderwidth=1
                ),
                xaxis=dict(title="Waktu (Timestamp)", gridcolor='#f1f5f9', linecolor='#cbd5e1'),
                yaxis=dict(title="Elevasi (Meter)", gridcolor='#f1f5f9', linecolor='#cbd5e1', zeroline=True, zerolinecolor='#cbd5e1')
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab_data:
            st.markdown("<h4 style='color: #0f172a; margin-bottom: 15px;'>Data Ekstraksi Konstanta Harmonik</h4>", unsafe_allow_html=True)
            res_df = pd.DataFrame({
                "Konstanta": coef.name, 
                "Amplitudo (m)": coef.A, 
                "Phase Lags (deg)": coef.g,
                "Frekuensi (cph)": coef.aux.frq
            })
            
            # Menggunakan HAS_MPL check untuk keamanan render dataframe
            if HAS_MPL:
                styled_df = res_df.style.background_gradient(cmap='Blues', subset=['Amplitudo (m)']).format(precision=4)
                st.dataframe(styled_df, use_container_width=True, height=400)
            else:
                st.dataframe(res_df.round(4), use_container_width=True, height=400)

    except Exception as e:
        st.error("Terjadi kesalahan pembacaan data. Pastikan format kolom CSV/Excel sesuai dengan template dan data cukup panjang (min. 15-29 hari).")
        st.exception(e)
