import serial, time
ser = serial.Serial('/dev/cu.usbserial-110', 115200, timeout=1)
time.sleep(3)  # Wait for boot
lines = []
start = time.time()
while time.time() - start < 10:  # Read for 10 seconds
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if line:
        lines.append(line)
        print(line)
ser.close()
