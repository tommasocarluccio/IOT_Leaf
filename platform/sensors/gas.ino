int sensor = A8;
// Set the initialsensorValue to 0
int sensorValue = 0;
void setup() {
  pinMode(sensor,INPUT);
  Serial.begin(9600);
}

void loop() {
  // Read 
  sensorValue = (analogRead(sensor));
  Serial.println(sensorValue,DEC);
  delay(1000);

}
