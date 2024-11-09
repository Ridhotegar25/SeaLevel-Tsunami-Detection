import time
from datetime import datetime
import serial
import os

# Konfigurasi default (sesuaikan dengan pengaturan ESP32 dan Raspberry Pi)
serial_port = '/dev/ttyUSB0'   # Ubah sesuai port yang digunakan
baud_rate = 9600               # Sesuaikan dengan baud rate ESP32
min_value = 0.0                # Nilai minimum untuk data sensor
max_value = 10.0               # Nilai maksimum untuk data sensor
output_folder = "./data_logs"  # Folder output untuk menyimpan file log

# Pastikan folder output ada
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def read_sensor_data():
    print("---------------------------------------------------")
    print("Starting reading sensor")
    print(f"Opening {serial_port} at baud rate {baud_rate}")
    print("---------------------------------------------------")

    # Inisialisasi serial
    ser = serial.Serial(serial_port, baudrate=baud_rate,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS)

    time.sleep(1)
    print("Data Echo Mode Enabled")
    measure = ''

    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    # Baca data dari serial
                    data = ser.read().decode('utf-8')
                except:
                    data = ''

                # Jika karakter yang diterima adalah '\r', proses data
                if data == '\r':
                    try:
                        measure = measure.replace('\n', '')

                        # Pisahkan nilai berdasarkan koma dan ambil nilai pertama
                        try:
                            first_value = measure.split(',')[0]
                            measure_float = float(first_value) / 100  # convert cm to m
                        except (ValueError, IndexError):
                            print("Invalid data format:", measure)
                            measure = ''
                            continue

                        # Periksa apakah nilai berada dalam rentang yang valid
                        if min_value <= measure_float <= max_value:
                            t_now = datetime.now().replace(microsecond=0)  # Menghilangkan milidetik

                            # Simpan data ke file log
                            file_name = os.path.join(output_folder, f"AllData_{t_now.strftime('%d-%m-%Y')}.log")
                            with open(file_name, 'a') as file:
                                file.write(f"{t_now}, {measure_float}\n")
                            print(f"{t_now}, {measure_float}")  # Tampilkan data

                        measure = ''  # Reset nilai measure setelah diproses

                    except TypeError as e:
                        print(f"Error in data measurement: {measure} | Error: {e}")
                        measure = ''  # Reset nilai measure jika terjadi error

                else:
                    measure += data

    except serial.SerialException as e:
        print("Serial error:", e)
    except KeyboardInterrupt:
        print("Exiting Program")
    except TypeError as e:
        print("Error Occurred, Exiting Program:", e)
    finally:
        ser.close()  # Tutup koneksi serial

# Jalankan fungsi
read_sensor_data()
