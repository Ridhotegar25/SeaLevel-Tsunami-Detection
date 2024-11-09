import pandas as pd
import os
import numpy as np
import time
from datetime import datetime, timedelta

# Konfigurasi folder output
output_folder = "./data_logs"

# Parameter konfigurasi
max300 = 300
max30 = 30
DtAverage = 5.0  # Interval dalam detik
initialized = False

# Inisialisasi buffer
x300 = [0.0] * (max300 + 1)
y300 = [0.0] * (max300 + 1)

def load_data(file_name):
    """Membaca data dari file log dan mengembalikannya sebagai DataFrame."""
    file_path = os.path.join(output_folder, file_name)
    if os.path.exists(file_path):
        data = pd.read_csv(file_path, header=None, names=['timestamp', 'level'], parse_dates=['timestamp'])
        return data
    else:
        print(f"File {file_name} tidak ditemukan di {output_folder}.")
        return None

def select_recent_data(data, max_points, max_minutes):
    """Memilih data berdasarkan jumlah titik maksimum atau batas waktu maksimum."""
    end_time = data['timestamp'].max()
    start_time = end_time - timedelta(minutes=max_minutes)
    recent_data = data[data['timestamp'] >= start_time].tail(max_points)
    return recent_data

def forecast(data, future_index=1):
    """Melakukan peramalan menggunakan regresi polinomial orde 2."""
    X = np.array(range(len(data)))
    y = data['level'].values

    # Fit data dengan polinomial orde 2
    coefficients = np.polyfit(X, y, 2)
    polynomial = np.poly1d(coefficients)

    # Prediksi untuk nilai masa depan berdasarkan indeks berikutnya
    predicted_value = polynomial(len(data) + future_index)

    return predicted_value

def calculate_rms(data):
    """Menghitung nilai RMS dari data level."""
    if len(data) == 0:
        return 0.0
    mean_value = np.mean(data)
    rms_value = np.sqrt(np.mean((data - mean_value) ** 2))
    return rms_value

def add_measure(time0, sensorValue):
    global initialized, x300, y300

    if not initialized:
        print('Initializing data buffer.')
        for k in range(max300 + 1):
            x300[k] = time0 - timedelta(seconds=(max300 - k) * DtAverage)
            y300[k] = sensorValue + np.random.random() * 0.001  # Simulasi data
        initialized = True

    # Update buffer with new sensor value
    y300[:-1] = y300[1:]  # Shift data
    y300[-1] = sensorValue  # Add new value
    x300[:-1] = x300[1:]  # Shift timestamps
    x300[-1] = time0  # Add new timestamp

def main():
    while True:  # Loop tak terbatas
        # Nama file log yang ingin dibaca berdasarkan tanggal hari ini
        today = datetime.utcnow().strftime('%d-%m-%Y')
        file_name = f"SeaLevelData_{today}.txt"

        # Load data dari file
        data = load_data(file_name)
        if data is not None:
            # Seleksi data untuk dua skenario
            data_30_150 = select_recent_data(data, max30, 150)
            data_300_1500 = select_recent_data(data, max300, 1500)

            # Lakukan peramalan untuk masing-masing skenario
            forecast_30_150 = forecast(data_30_150)
            forecast_300_1500 = forecast(data_300_1500)

            # Hitung nilai RMS dari data masing-masing skenario
            rms_30_150 = calculate_rms(data_30_150['level'].values)
            rms_300_1500 = calculate_rms(data_300_1500['level'].values)

            # Tampilkan hasil peramalan dan RMS
            print(f"n30: {forecast_30_150:.2f}")
            print(f"n300: {forecast_300_1500:.2f}")
            print(f"RMS: {rms_30_150:.4f}")


            # Simulasi menambahkan data ke buffer
            add_measure(datetime.utcnow(), forecast_300_1500)  # Menggunakan forecast sebagai sensor value

        else:
            print("Tidak ada data untuk diramal.")

        time.sleep(5)  # Jeda selama 5 detik sebelum iterasi berikutnya

if __name__ == "__main__":
    main()
