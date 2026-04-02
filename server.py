import socket
import ssl
import json
import threading
import time

HOST = ''
PORT = 5000

# -------------------------------
# SETTINGS
# -------------------------------
SAFE_DISTANCE = 20
MIN_RED_TIME = 3      # minimum RED duration
EXTEND_TIME = 2       # extension time (auto-reset)
LOOP_DELAY = 0.05     # smooth processing

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)

print(" Smart Traffic TLS Server Running...")


def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")

    secure_conn = context.wrap_socket(conn, server_side=True)

    # -------------------------------
    # RESET COUNT ON CONNECT
    # -------------------------------
    try:
        secure_conn.send(json.dumps({"signal": "RESET"}).encode())
    except:
        pass

    # -------------------------------
    # STATE VARIABLES
    # -------------------------------
    crossing_active = False
    cross_start_time = 0

    try:
        while True:
            data = secure_conn.recv(1024).decode()
            if not data:
                break

            sensor = json.loads(data)

            ir1 = sensor["ir1"]
            ir2 = sensor["ir2"]
            dist = sensor["distance"]

            # IR: 0 = object detected
            pedestrian = (ir1 == 0 or ir2 == 0)
            vehicle_close = (dist < SAFE_DISTANCE)

            signal = "GREEN"

            # -------------------------------
            # MAIN TRAFFIC LOGIC
            # -------------------------------
            if not crossing_active:

                if pedestrian and not vehicle_close:
                    print("🧍 Pedestrian detected → SAFE")

                    crossing_active = True
                    cross_start_time = time.time()
                    signal = "RED"

                elif pedestrian and vehicle_close:
                    print(" Vehicle too close → waiting")
                    signal = "GREEN"

                else:
                    signal = "GREEN"

            else:
                elapsed = time.time() - cross_start_time

                # Maintain RED for minimum duration
                if elapsed < MIN_RED_TIME:
                    signal = "RED"

                else:
                    if pedestrian:
                        print(" Extending crossing")
                        cross_start_time = time.time()  # extend
                        signal = "RED"
                    else:
                        print(" No pedestrian → GREEN")
                        crossing_active = False
                        signal = "GREEN"

            # -------------------------------
            # SEND RESPONSE
            # -------------------------------
            secure_conn.send(json.dumps({"signal": signal}).encode())

            print(f"{addr} → {sensor} → {signal}")

            time.sleep(LOOP_DELAY)

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr}")


# -------------------------------
# SERVER LOOP
# -------------------------------
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()