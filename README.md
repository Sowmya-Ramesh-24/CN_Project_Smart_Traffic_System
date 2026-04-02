### Smart School Zone Traffic Control System 
This project dynamically controls traffic signals based on pedestrian presence and vehicle proximity to improve safety and efficiency 

## Objective
To design and implement a real time traffic system that 
 - Detects the presence of pedestrians using IR sensors
 - Measures vehicle proximity and distance using IR sensors
 - Makes traffic light control decisions on a central server
 - Ensures safe pedestrian crossing

---
## System Architecture
```text
            ┌──────────────────────┐
            │      SERVER          │
            │  (Decision Engine)   │
            └─────────┬────────────┘
                      │ TLS (Secure)
                      ▼
            ┌──────────────────────┐
            │    Python Client     │
            │ (Communication Layer)│
            └─────────┬────────────┘
                      │ Serial
                      ▼
            ┌──────────────────────┐
            │        ESP32         │
            │  (Sensor + Actuator) │
            └─────────┬────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                 ▼
    IR (S1)        IR (S2)         Ultrasonic (S3)
    Pedestrians    Pedestrians       Vehicles 
                      │
                      ▼
               Traffic Lights
           (RED / YELLOW / GREEN)
```

---
## Circuit  Logic
S1 and S2 (IR Sensors)
  -  Detect pedestrians waiting to cross
  -  Output LOW (0) when object detected

S3 (Ultrasonic Sensor) 
  - Measures distance of incoming vehicles

--- 
## Traffic Control Logic
1. If **pedestrian is detected via S1 or S2**
    - checks vehicle distance using S3
      
2. If **road is safe (no close vehicle)**:
   - Turn signal → RED
   - Allow crossing

3. Maintain RED for minimum time

4. After time expires:
   - Recheck pedestrians:
     - If still present → extend RED
     - Else → switch to  GREEN

5. If vehicle is too close:
   - Keep signal GREEN (safety priority)
  
--- 
## System Design
1. Centralized Server Logic
- All decisions handled by server
- Enables scalability and upgrades

2. Distributed System
- ESP32 → sensing + execution
- Client → communication bridge
- Server → intelligence

3. Safety-First Approach
- Vehicle proximity overrides pedestrian trigger
- Prevents unsafe signal switching

---
## Technologies Used
- **ESP32 (Arduino C++)**
- **Python (Sockets, SSL, JSON, TLS)**
- **UDP (Traffic logging)**
- **TLS Encryption**

--- 
 Two machines required:
  - **Server Machine** → runs server code (`servers/`)
  - **Client Machine** → runs `client.py` (connected to ESP32)

---

## Network Setup
- Both machines must be on the **same network**
- Recommended: use **laptop hotspot**
  - Start hotspot on server machine
  - Connect client machine to it

---

## Find Server IP
On server machine:
 Windows:
```bash
ipconfig
```
Mac/ Linux:
```bash
ifconfig
```
look for IPv4 Address → 192.168.x.x

---
## Generate TLS certificate
# Install Openssl
| Operating System | Installation Steps | Verify Installation |
|-----------------|------------------|---------------------|
| **Windows** | Download from: https://slproweb.com/products/Win32OpenSSL.html<br>Install and ensure OpenSSL is added to PATH | `openssl version` |
| **Mac (Homebrew)** | `brew install openssl` | `openssl version` |
| **Linux (Ubuntu/Debian)** | `sudo apt update`<br>`sudo apt install openssl` | `openssl version` |

generate certificates on server running machine 
```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```
place inside
servers/
├── cert.pem
├── key.pem

---
## Run server on server machine
- create .env inside servers using .env.example
- and then run
``` bash
cd servers
python server.py
python udp_server.py
```
---
## Run client on client machine
- create .env using .env.example
```text
  SERVER_IP=192.168.x.x  ->  Replace with server machine IP
  PORT=5000
  UDP_PORT=6000
```
- and then run
``` bash
python client.py
```
--- 
## Hardware Connection
Upload Code to ESP32
1. Connect ESP32 via USB  
2. Open `traffic_control.ino` in Arduino IDE  
3. Select:
   - Board → ESP32 Dev Module  
   - Port → (your ESP32 port)  
4. Click **Upload**

---
## Communication Flow
ESP32 → Serial → Python Client → Server → Python Client → ESP32|

