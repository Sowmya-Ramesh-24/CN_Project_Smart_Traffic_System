import socket
import ssl
import json
import serial
import time
import re
from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("SERVER_IP")
PORT = int(os.getenv("PORT", 5000))
UDP_PORT = int(os.getenv("UDP_PORT", 6000))
SERIAL_PORT = os.getenv("SERIAL_PORT", "COM3")
BAUD_RATE = int(os.getenv("BAUD_RATE", 115200))

# Serial connection
ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)

# TLS
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secure_sock = context.wrap_socket(sock, server_hostname=HOST)
secure_sock.connect((HOST, PORT))

print("TLS Connected")
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#  Vehicle count (ultrasonic edge detection)
vehicle_count = 0
prev_vehicle = False

#  State machine
state = "NORMAL"
state_start = time.time()

last_signal = None

# client.py (SIMPLIFIED)

while True:
    try:
        line = ser.readline().decode(errors='ignore').strip()

        if not line or "IR1:" not in line:
            continue

        parts = line.split(",")

        ir1 = int(parts[0].split(":")[1])
        ir2 = int(parts[1].split(":")[1])
        dist = float(parts[2].split(":")[1])
        vehicle_count = int(parts[3].split(":")[1])

        #  SEND RAW SENSOR DATA
        data = {
            "ir1": ir1,
            "ir2": ir2,
            "distance": dist
        }

        secure_sock.send(json.dumps(data).encode())

        #  RECEIVE DECISION
        response = secure_sock.recv(1024).decode()
        signal = json.loads(response)["signal"]

        # DISPLAY ONLY
        print(f" SIGNAL: {signal}")
        print(f" Distance: {dist} cm | Vehicle Count: {vehicle_count}")

        #  UDP LOGGING
        udp_sock.sendto(json.dumps({
            "vehicle_count": vehicle_count,
            "signal": signal
        }).encode(), (HOST, UDP_PORT))

        #  SEND TO ESP32
        ser.write((signal + "\n").encode())

        time.sleep(0.5)

    except Exception as e:
        print("Error:", e)
        time.sleep(1)