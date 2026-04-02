import socket
import json
import csv
import time
import os
from dotenv import load_dotenv
import os

load_dotenv()
UDP_IP = "0.0.0.0"
UDP_PORT = int(os.getenv("UDP_PORT", 6000))
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("UDP Analytics Server Running...")

start_time = time.time()

# Create CSV
if not os.path.exists("traffic_log.csv"):
    with open("traffic_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Vehicle Number", "Time Passed (s)", "Signal"])

while True:
    data, addr = sock.recvfrom(1024)

    try:
        parsed = json.loads(data.decode())

        vehicle = parsed.get("vehicle_count", 0)
        signal = parsed.get("signal", "UNKNOWN")

        elapsed = round(time.time() - start_time, 2)

        print(f"{elapsed}s → Vehicle {vehicle} → {signal}")

        with open("traffic_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([vehicle, elapsed, signal])

    except Exception as e:
        print("Error:", e)