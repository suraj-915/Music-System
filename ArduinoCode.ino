#include <Wire.h>               
#include "SoftwareSerial.h"
#include "DFRobotDFPlayerMini.h"
#include "MAX30105.h"           
#include "LiquidCrystal_I2C.h"


SoftwareSerial mp3(10, 11); // RX, TX
DFRobotDFPlayerMini dfplayer;

MAX30105 particleSensor;
LiquidCrystal_I2C lcd(0x27, 16, 2);

#define playButton 4
#define pauseButton 7
#define recButton 8
#define potPin A0

int currentVolume = 15; 
int lastPotValue = -1;

String currentTrackName = "Jukebox Ready";
long lastLcdScrollTime = 0;
int scrollIndex = 0;
const int LCD_UPDATE_RATE_MS = 300; // Speed we're scrolling at

// Button Debouncing
long lastPlayPress = 0;
long lastPausePress = 0;
long lastRecPress = 0;
const long DEBOUNCE_DELAY_MS = 50;


void setup() {
  Serial.begin(115200);
  mp3.begin(9600);
  Wire.begin();

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Emotion Jukebox");
  lcd.setCursor(0, 1);
  lcd.print("Booting...");

  if (!dfplayer.begin(mp3)) {
    Serial.println("DFPlayer not found!");
    lcd.clear();
    lcd.print("DFPlayer Error");
    while (true);
  }
  dfplayer.volume(currentVolume);

  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102 not found!");
    lcd.clear();
    lcd.print("Sensor Error");
    while (true);
  }
  particleSensor.setup();

  pinMode(playButton, INPUT_PULLUP);
  pinMode(pauseButton, INPUT_PULLUP);
  pinMode(recButton, INPUT_PULLUP);

  delay(1000);
  
  Serial.println("Ready.");
  lcd.clear();
  handleLcdDisplay(); // Show default "Jukebox Ready" and volume
}

void loop() {
  handleSerialCommands(); // Check for commands from PC
  handleButtons();        // Check for physical button presses
  handleVolume();         // Check potentiometer
  handleSensor();         // Read sensor, send data to PC
  handleLcdDisplay();     // Update the LCD screen (scrolling)
}


// =================================================================
//   HELPER FUNCTIONS
// =================================================================

/**
 * Task 1: Check for commands from PC
 * "PLAY:1" - Plays track 1
 * "PLAY"   - Resumes play
 * "PAUSE"  - Pauses play
 * "NAME:..." - Sets the track name on the LCD
 */
void handleSerialCommands() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); // Remove any extra whitespace

    if (cmd.startsWith("PLAY:")) {
      int trackNum = cmd.substring(5).toInt();
      dfplayer.play(trackNum);
      Serial.print("Playing track: ");
      Serial.println(trackNum);

    } else if (cmd == "PLAY") {
      dfplayer.start(); // Resume
      Serial.println("Resuming play");

    } else if (cmd == "PAUSE") {
      dfplayer.pause();
      Serial.println("Paused");

    } else if (cmd.startsWith("NAME:")) {
      currentTrackName = cmd.substring(5);
      scrollIndex = 0; // Reset scroll for new name
      Serial.print("Set track name: ");
      Serial.println(currentTrackName);
    }
  }
}

/**
 * Task 2: Check for physical button presses
 * Uses millis() for non-blocking debounce
 */
void handleButtons() {
  long now = millis();

  // Play/Resume Button
  if (digitalRead(playButton) == LOW && (now - lastPlayPress > DEBOUNCE_DELAY_MS)) {
    lastPlayPress = now;
    dfplayer.start(); // Resume
    Serial.println("Play button pressed");
  }

  // Pause Button
  if (digitalRead(pauseButton) == LOW && (now - lastPausePress > DEBOUNCE_DELAY_MS)) {
    lastPausePress = now;
    dfplayer.pause();
    Serial.println("Pause button pressed");
  }

  // Record Button
  if (digitalRead(recButton) == LOW && (now - lastRecPress > DEBOUNCE_DELAY_MS)) {
    lastRecPress = now;
    Serial.println("REC_BUTTON_PRESSED"); // Send command to Python
  }
}

/**
 * Task 3: Read potentiometer and set volume
 * Only updates when the *mapped* volume level changes.
 */
void handleVolume() {
  // Read pot value (0-1023)
  int potValue = analogRead(potPin);

  // Check if it's a significant change (avoids jitter)
  if (abs(potValue - lastPotValue) > 4) {
    lastPotValue = potValue;

    // Map to DFPlayer volume (0-30)
    int newVolume = map(potValue, 0, 1023, 0, 30);

    // Only update if the volume level actually changed
    if (newVolume != currentVolume) {
      currentVolume = newVolume;
      dfplayer.volume(currentVolume);
    }
  }
}

/**
 * Task 4: Read sensor and send *only IR data* to PC
 * This is what your Python script expects.
 */
void handleSensor() {
  particleSensor.check(); // Check for new data

  while (particleSensor.available()) {
    // Send *only* the IR value, followed by a newline.
    Serial.println(particleSensor.getFIFOIR());
    
    // Move to the next sample in the buffer
    particleSensor.nextSample();
  }
}

/**
 * Task 5: Update LCD with track name and volume
 * Rate-limited to not slow down the loop.
 * Handles scrolling for long track names.
 */
void handleLcdDisplay() {
  // Only update the LCD at a fixed rate
  if (millis() - lastLcdScrollTime < LCD_UPDATE_RATE_MS) {
    return; // Not time to update yet
  }
  lastLcdScrollTime = millis();

  // --- Update Line 1 (Track Name) ---
  lcd.setCursor(0, 0);
  if (currentTrackName.length() <= 16) {
    // Name is short, no scroll needed
    String nameStr = currentTrackName;
    nameStr.concat("                "); // Add padding
    lcd.print(nameStr.substring(0, 16));
    scrollIndex = 0; // Not scrolling

  } else {
    // Name is long, scroll it
    String scrollText = currentTrackName + "   "; // Add 3 spaces for wrap
    int len = scrollText.length();
    
    // Create the 16-char string to display
    String displayStr = scrollText.substring(scrollIndex) + scrollText.substring(0, scrollIndex);
    lcd.print(displayStr.substring(0, 16));

    // Move scroll index for next time
    scrollIndex++;
    if (scrollIndex >= len) {
      scrollIndex = 0; // Loop back to start
    }
  }

  // --- Update Line 2 (Volume) ---
  lcd.setCursor(0, 1);
  String volStr = "Volume: " + String(currentVolume);
  volStr.concat("                "); // Add padding to clear old text
  lcd.print(volStr.substring(0, 16));
	

