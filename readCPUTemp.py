import time

def get_cpu_temperature():
    # Read the temperature from the system file
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as temp_file:
        # Read the temperature in millidegrees Celsius
        temp_milli_c = int(temp_file.read().strip())

        # Convert to degrees Celsius
        temp_celsius = temp_milli_c / 1000.0
        
        return temp_celsius  # Mengembalikan nilai suhu

if __name__ == "__main__":
    while True:
        cpu_temp = get_cpu_temperature()
        if cpu_temp is not None:
            print(f"{cpu_temp:.2f}")
        time.sleep(5)  # Menunggu 1 detik sebelum membaca suhu lagi
