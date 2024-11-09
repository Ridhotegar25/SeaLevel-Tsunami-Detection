import pandas as pd
import os
import numpy as np
import time
from datetime import datetime, timedelta

# Konfigurasi folder output
output_folder = "./data_logs"

# Parameter konfigurasi (contoh, bisa disesuaikan)
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

def forecast(data, window_size):
    """Melakukan peramalan menggunakan regresi polinomial orde 2."""
    recent_data = data['level'].tail(window_size).reset_index(drop=True)
    X = np.array(range(len(recent_data)))
    y = recent_data.values

    coefficients = np.polyfit(X, y, 2)
    polynomial = np.poly1d(coefficients)

    next_index = len(recent_data)
    predicted_value = polynomial(next_index)

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
            # Lakukan peramalan untuk 30 dan 300 titik data terakhir
            forecast_30 = forecast(data, 30)
            forecast_300 = forecast(data, 300)

            # Hitung nilai RMS dari level data
            rms_value = calculate_rms(data['level'].values)

            # Tampilkan hasil peramalan dan RMS
            print(f"n30: {forecast_30:.2f}")
            print(f"n300: {forecast_300:.2f}")
            print(f"Rms: {rms_value:.4f}")

            # Simulasi menambahkan data ke buffer
            add_measure(datetime.utcnow(), forecast_300)  # Menggunakan forecast sebagai sensor value

        else:
            print("Tidak ada data untuk diramal.")

        time.sleep(5)  # Jeda selama 5 detik sebelum iterasi berikutnya

if __name__ == "__main__":
    main()