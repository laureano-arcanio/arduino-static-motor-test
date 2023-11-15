
#include "HX711.h"
#include <SPI.h>
#include <SD.h>

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

HX711 scale;
File root;
File dataFile;

String filename;
int transducerVoltage = 0;
float force = 0;
unsigned long millisAtCurrentLoop = 0;
unsigned long millisAtIgnitionStart = 0;
unsigned long millisAtCountDownStart = 0;
bool hasHeaders = false;
int startButtonPushCount = 0;

// Pins
const int SD_CHIP_SELECT = 4;
const int FIRE_PIN = 5;  // Salida de Relay para ignicion
const int START_BUTTON_PIN = 6; // Boton de inicio (con pull down R)
const int LED_1_PIN = 7; // Led 1
const int LED_2_PIN = 8; // Led 2 no realmente usado
const int TRANSDUCER_ANALOG_PIN = A0; // Pin analogico al transductor, en mi caso 0 a 5v -> 0  a 2000 psi
// Celda de carga 
const float LOAD_CELL_CALIBRATION_FACTOR = 98.2;
// DT -> PIN 2
// SCK -> PIN 3
// Hay que conectar el pin 15 del chip H711X a VCC para que el sampling sea de 80Hz en vez de 10Hz
// Memoria SD por el bus SPI 

const int FIRE_DURATION = 5000;
const long int MAX_BURNING_TIME = 120000; // 2 Mins
const long int COUNTDOWN_DURATION = 30000; // Esperar 30 segundos antes de ignicion

const unsigned short STATUS_ERROR = 10;
const unsigned short STATUS_READY = 20;
const unsigned short STATUS_COUNTDOWN = 30;
const unsigned short STATUS_IGNITION = 40;
const unsigned short STATUS_BURNING = 60;
const unsigned short STATUS_FINISHED = 70;
unsigned short status = STATUS_READY;

void setup() {
  Serial.begin(57600);

  pinMode(START_BUTTON_PIN, INPUT);
  pinMode(LED_1_PIN, OUTPUT);
  pinMode(LED_2_PIN, OUTPUT);
  pinMode(FIRE_PIN, OUTPUT);

  Serial.println("Checkeando la tarjeta de memoria");
  if (!SD.begin(SD_CHIP_SELECT))
  {
    Serial.println("Card failed, or not present");
    status = STATUS_ERROR;
  }
  else
  {
    root = SD.open("/");
    filename = getFileName(root, 0);
    status = STATUS_READY;
  }
  
  Serial.println("Nombre de archivo: " + filename);
  Serial.println("Calibracion de la balanza");
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale(LOAD_CELL_CALIBRATION_FACTOR);
  delay(500);
  scale.tare();
  if (status > STATUS_ERROR) {
    digitalWrite(LED_1_PIN, HIGH);
    digitalWrite(LED_2_PIN, HIGH);
  }
  
  digitalWrite(FIRE_PIN, LOW);
}

String getFileName(File dir, int numTabs)
{
  unsigned int fileCount = 0;
  while (true)
  {
    File entry = dir.openNextFile();
    if (!entry)
    {
      break;
    }
    fileCount++;
    entry.close();
  }
  return "STATIC_" + String(fileCount) + ".csv";
}

void sdDataLogger() {

  dataFile = SD.open(filename, FILE_WRITE);
  if (hasHeaders == false) {
    // CSV format:
    // Millis from init, Status, Force, Transducer Value
    dataFile.println("Ms\tStatus\tF\tV");
    hasHeaders = true;
  }
  dataFile.print(millisAtCurrentLoop);
  dataFile.print("\t");
  dataFile.print(status);
  dataFile.print("\t");
  dataFile.print(force);
  dataFile.print("\t");
  dataFile.print(transducerVoltage);
  dataFile.print("\n");
  dataFile.close();
}
  

void loop() {
  millisAtCurrentLoop = millis();
  int buttonLevel = digitalRead(START_BUTTON_PIN);

  if (status == STATUS_READY) {
    Serial.println("Esperando secuencua de Ignicion");
    
    if (buttonLevel == HIGH) {
      Serial.println("Iniciando cuenta regresiva");
      status = STATUS_COUNTDOWN;
      millisAtCountDownStart = millisAtCurrentLoop;
    }
    delay(100);
  }

  if (status == STATUS_COUNTDOWN ){
    Serial.println("Contando");
    digitalWrite(LED_1_PIN, LOW);
    digitalWrite(LED_2_PIN, LOW);
    delay(500);
    digitalWrite(LED_1_PIN, HIGH);
    digitalWrite(LED_2_PIN, HIGH);
    delay(500);
  }
  
  if (status == STATUS_COUNTDOWN and millisAtCurrentLoop - millisAtCountDownStart >= COUNTDOWN_DURATION) {
    Serial.println("Cuenta regresiva finalizada");
    status = STATUS_IGNITION;
    millisAtIgnitionStart = millisAtCurrentLoop;
  } 
    
  if (status > STATUS_COUNTDOWN and status < STATUS_FINISHED) {
  
    if (status == STATUS_IGNITION and millisAtCurrentLoop - millisAtIgnitionStart < FIRE_DURATION) {
      digitalWrite(FIRE_PIN, HIGH);
      Serial.println("Ignicion");
    } else {
      digitalWrite(FIRE_PIN, LOW);
      status = STATUS_BURNING;
      Serial.println("Ignicion finalizada");
    }
    transducerVoltage = analogRead(TRANSDUCER_ANALOG_PIN);
    force = scale.get_units(1);
//  float pressure = ((transducerVoltage * (5.0 / 1023.0)) * 2000) / 5;
    
   
//  Serial.print(millisAtCurrentLoop);
//  Serial.print("\t");
//  Serial.print(status);
//  Serial.print("\t");
//  Serial.print(force);
//  Serial.print("\t");
//  Serial.print(transducerVoltage);
//  Serial.print("\n");
    Serial.println(millisAtCurrentLoop - millisAtIgnitionStart);
    Serial.println(MAX_BURNING_TIME);
    if (millisAtCurrentLoop - millisAtIgnitionStart > MAX_BURNING_TIME) {
      status = STATUS_FINISHED;
      Serial.println("Secuencia Completada");
    }
    sdDataLogger();
  }

  if (status == STATUS_FINISHED) {
    digitalWrite(LED_1_PIN, LOW);
    digitalWrite(LED_2_PIN, LOW);
    delay(100);
    digitalWrite(LED_1_PIN, HIGH);
    digitalWrite(LED_2_PIN, HIGH);
    delay(500);
  }
}
