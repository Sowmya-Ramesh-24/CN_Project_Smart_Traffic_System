// ==========================================
// SMART TRAFFIC SYSTEM (SERVER CONTROLLED)
// ESP32 ONLY EXECUTES COMMANDS
// ==========================================

// ----------- PIN DEFINITIONS -----------
#define IR1_PIN     14
#define IR2_PIN     27

#define TRIG_PIN    26
#define ECHO_PIN    25

#define RED_PIN     18
#define YELLOW_PIN  19
#define GREEN_PIN   21

// ----------- SETTINGS -----------
unsigned long lastSendTime = 0;
int vehicleCount = 0;

// ==========================================
// ULTRASONIC DISTANCE
// ==========================================
float getDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);

  if (duration == 0) return 999.0;

  return duration * 0.0343 / 2.0;
}

// ==========================================
// TRAFFIC LIGHT CONTROL
// ==========================================
void setTrafficLight(String signal) {

  if (signal == "RED") {
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(YELLOW_PIN, LOW);
    digitalWrite(GREEN_PIN, LOW);
  }
  else if (signal == "YELLOW") {
    digitalWrite(RED_PIN, LOW);
    digitalWrite(YELLOW_PIN, HIGH);
    digitalWrite(GREEN_PIN, LOW);
  }
  else { // GREEN
    digitalWrite(RED_PIN, LOW);
    digitalWrite(YELLOW_PIN, LOW);
    digitalWrite(GREEN_PIN, HIGH);
  }
}

// ==========================================
// SETUP
// ==========================================
void setup() {
  Serial.begin(115200);

  pinMode(IR1_PIN, INPUT);
  pinMode(IR2_PIN, INPUT);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(RED_PIN, OUTPUT);
  pinMode(YELLOW_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);

  // Default state
  setTrafficLight("GREEN");

  Serial.println("ESP32 READY (CLIENT MODE)");
}

// ==========================================
// LOOP
// ==========================================
void loop() {

  float distance = getDistanceCM();

  int ir1 = digitalRead(IR1_PIN);
  int ir2 = digitalRead(IR2_PIN);

  // Optional vehicle count logic
  if (distance < 20) {
    vehicleCount++;
  }

  // SEND SENSOR DATA TO PYTHON CLIENT
  Serial.print("IR1:");
  Serial.print(ir1);
  Serial.print(",IR2:");
  Serial.print(ir2);
  Serial.print(",DIST:");
  Serial.print(distance);
  Serial.print(",COUNT:");
  Serial.println(vehicleCount);

  // RECEIVE SIGNAL FROM SERVER (via client.py)
  if (Serial.available()) {
    String signal = Serial.readStringUntil('\n');
    signal.trim();

    Serial.print("Received Signal: ");
    Serial.println(signal);

    setTrafficLight(signal);
  }

  delay(500);
}