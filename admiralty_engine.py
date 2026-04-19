import numpy as np

def calculate_formzahl(k1, o1, m2, s2):
    """
    Menghitung Bilangan Formzahl (F)
    Rumus: F = (AK1 + AO1) / (AM2 + AS2)
    """
    if (m2 + s2) == 0:
        return 0
    f = (k1 + o1) / (m2 + s2)
    return round(f, 3)

def get_tide_type(f):
    """Klasifikasi berdasarkan Bilangan Formzahl"""
    if 0 <= f <= 0.25:
        return "Pasang Surut Harian Ganda (Semi Diurnal)"
    elif 0.25 < f <= 1.50:
        return "Pasang Surut Campuran Dominan Harian Ganda"
    elif 1.50 < f <= 3.00:
        return "Pasang Surut Campuran Dominan Harian Tunggal"
    else:
        return "Pasang Surut Harian Tunggal (Diurnal)"

# Fungsi utama untuk memproses file upload
def process_admiralty(df):
    # Logika perhitungan 9 komponen Admiralty biasanya melibatkan 
    # skema tabel 24 jam x 15-29 hari.
    # Di sini kita simulasikan output setelah proses perhitungan selesai.
    
    # Contoh data output simulasi (Amplitudo dalam cm):
    results = {
        "M2": 15.2, "S2": 8.1, "N2": 3.4,
        "K1": 12.5, "O1": 10.2, "P1": 4.1,
        "M4": 1.2, "MS4": 0.8, "K2": 2.2
    }
    
    f_value = calculate_formzahl(results['K1'], results['O1'], results['M2'], results['S2'])
    tide_type = get_tide_type(f_value)
    
    return results, f_value, tide_type