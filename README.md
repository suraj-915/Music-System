# 🎵 Emotion Jukebox: Biometric & Vision-Based Music Controller

An intelligent music delivery system that selects tracks based on your physiological state and facial expressions. The system integrates real-time heart rate/respiration data with computer vision to map your mood to a custom arousal-based playlist.

## 🚀 Key Features
* **Dual-Mode Emotion Capture:**
    * **Computer Vision:** Analyzes facial expressions to detect dominant emotions like Happy, Sad, or Angry.
    * **Biometric Arousal:** Uses a `MAX30105` sensor to calculate BPM and Respiration Rate via FFT analysis.
* **Dynamic Music Mapping:** Maps emotions and arousal scores into nine distinct states for personalized playback.
* **Physical & Software Controls:** Features a hardware dashboard with an I2C LCD, physical buttons for playback, and a potentiometer for volume.
* **Real-time Feedback:** Scrolling LCD display shows current track names and volume levels dynamically.

## 🛠️ Hardware Requirements
* **Microcontroller:** Arduino Uno R3
* **Sensors:** `MAX30105` Pulse Oximeter & Heart-Rate SensorPotentiometer for volume control 
* **Audio:**`DFPlayer Mini` MP3 Module 
* **Display:** `16x2 LCD` with I2C Backpack 
* **Input:** 3x Tactile Push Buttons (Play, Pause, Record) 


## 📊 Logic & Signal Processing
The system calculates an **Arousal Score** by processing the IR data from the heart rate sensor:

1. **FFT Processing:** Performs a Fast Fourier Transform on a 10-second sample window to find peak frequencies.
2. **Scoring Formula:**
   $$Arousal = (0.4 \times BPM) + (0.6 \times RespirationRate)$$
3. **Song Selection:** Python selects a random track from a categorized dictionary based on detected emotion and arousal.

## 🕹️ Usage Instructions

### 1. System Initialization
* Connect the Arduino to your PC via USB.
* Ensure the `MAX30105` sensor is placed securely on your fingertip.
* Run the Python script: `python controller_code.py`.
* The LCD will display **"Emotion Jukebox: Booting..."** followed by **"Jukebox Ready"**.

### 2. Capturing Your Mood
* **Step 1:** Press the **Record Button**.
* **Step 2:** Look into your webcam. The system will record and analyze your facial expressions for **5 seconds**.
* **Step 3:** The dominant emotion will be identified and used for song selection.

### 3. Music Playback
* Once an emotion is detected, the Python script calculates your arousal level.
* The system automatically selects a matching track and sends the command to the **DFPlayer Mini**.
* Use the **Play/Pause buttons** (Pins 4 and 7) for manual control.
* Adjust the **Potentiometer** (Pin A0) to change the volume in real-time.

### 4. Monitoring
* View the **16x2 LCD** to see the current track name and volume level.
* Check the **Python Terminal** for detailed logs on BPM and the selected playlist category.
