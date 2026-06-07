#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

const int RED = 2;
const int BLUE = 3;
const int GREEN = 4;
const int YELLOW = 5;
const int BUZZER = 6;

String data = "";
bool isSOS = false;
unsigned long previousMillis = 0;
const int interval = 300;
bool redState = false;

void setup() {
  Serial.begin(9600);

  pinMode(RED, OUTPUT);
  pinMode(BLUE, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(YELLOW, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  lcd.init();
  lcd.backlight();
}

void loop() {

  while (Serial.available()) {
    char c = Serial.read();
    data += c;

    if (c == '\n') {
      int sep = data.indexOf(':');

      if (sep != -1) {
        String gesture = data.substring(0, sep);
        String conf = data.substring(sep + 1);

        gesture.trim();
        conf.trim();

        handleGesture(gesture, conf);
      }

      data = "";
    }
  }

  if (isSOS) {
    if (millis() - previousMillis >= interval) {
      previousMillis = millis();
      redState = !redState;
      digitalWrite(RED, redState);
      digitalWrite(BUZZER, redState);
    }
  }
}

void handleGesture(String gesture, String conf) {

  digitalWrite(RED, LOW);
  digitalWrite(BLUE, LOW);
  digitalWrite(GREEN, LOW);
  digitalWrite(YELLOW, LOW);
  digitalWrite(BUZZER, LOW);

  isSOS = false;

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(gesture);
  lcd.setCursor(0,1);
  lcd.print(conf + "%");

  if (gesture.equals("1")) {
    digitalWrite(YELLOW, HIGH);
    digitalWrite(BLUE, HIGH);
  }
  else if (gesture.equals("2")) {
    digitalWrite(GREEN, HIGH);
    digitalWrite(RED, HIGH);
  }
  else if (gesture.equals("3")) {
    digitalWrite(RED, HIGH);
    digitalWrite(BLUE, HIGH);
    digitalWrite(GREEN, HIGH);
    digitalWrite(YELLOW, HIGH);
  }
  else if (gesture.equals("Heart")) {
    digitalWrite(YELLOW, HIGH);
  }
  else if (gesture.equals("Ok")) {
    digitalWrite(GREEN, HIGH);
  }
  else if (gesture.equals("thankYou")) {
    digitalWrite(BLUE, HIGH);
  }
  else if (gesture.equals("SOS")) {
    digitalWrite(RED, HIGH);
    isSOS = true;
  }
}
