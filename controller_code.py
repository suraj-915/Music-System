# getting the values for bpm and rr
import serial
import serial.tools.list_ports
import random
import numpy
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
import time
from playsound import playsound
from detection import capture_emotion_5sec


ports = serial.tools.list_ports.comports()
arduinoport = ''

for port in ports:
	if 'arduino' in port.description.lower() or 'arduino' in port.manufacturer.lower():
		arduinoport = port.device


con = serial.Serial(arduinoport, 115200, timeout = 1)

# Button state tracking
button1_pressed = False
button2_pressed = False
button3_pressed = False
music_playing = False
detected_emotion = None

# Emotion-Arousal Song Map with Song IDs
emotion_map = {
	'happy': {
		'low_arousal': [{'0001':'Banana pancakes'}, {'0002':'Holocene'},{'0003':'Anisuthide Yaako Indu'}],  # Contentment playlist
		'medium_arousal': [{'0004':'Walking on Sunshine'}, {'0005':'Life Is a Highway'},{'0006':'Ondu Malebillu'}],  # Good Vibes playlist
		'high_arousal': [{'0007':'Santhosakke'}, {'0008':'FE!N'},{'0009':'Dont Stop Me Now'}]  # Euphoric playlist
	},
	'sad': {
		'low_arousal': [{'0010':'Moonlight Sonata'}, {'0011':'Weightless '}, {'0012':'Ninnindale '}],  # Reflective playlist
		'medium_arousal': [{'0013':'Teardrop '}, {'0014':'Creep '}, {'0015':'Ee Manase'}],  # Brooding playlist
		'high_arousal': [{'0016':'Pink Noise'}, {'0017':'Weightless '}, {'0018':''}]  # THE PANIC STATE playlist
	},
	'angry': {
		'low_arousal': [{'0019':'Come As You Are'}, {'0020':'Blue on Black'},{'0021':'Karunaada Thayi – Huccha'}], # Frustrated / Simmering playlist
		'medium_arousal': [{'0022':'Lose Yourself'}, {'0023':'Back in Black'},{'0024':'Chali Chali – Duniya Vijay'}],  # Venting playlist
		'high_arousal': [{'0025':'Duality '}, {'0026':'Break Stuff'}, {'0027':'Why This Kolaveri Di'}]  # Catharsis playlist
	},
	'neutral': {
		'low_arousal': [{'0028':'beats to relax/study to'}, {'0029':'Lujon'}, {'0030':'Munjaane Manjalli'}],  # Focus / Chill playlist
		'medium_arousal': [{'0031':'Get Lucky'}, {'0032':'Redbone '}, {'0033':'Marali Manasaagide'}],  # Cruising / Background playlist
		'high_arousal': [{'0034':'Opus '}, {'0035':'Experience (Starkey Remix)'}, {'0036':'Belakina Kavithe – Instrumental '}]  # THE STRESS STATE playlist
	}
}

def get_arousal_level(arousal_score):
	"""Categorize arousal score into low, medium, or high arousal"""
	if arousal_score < 0.33:
		return 'low_arousal'
	elif arousal_score < 0.66:
		return 'medium_arousal'
	else:
		return 'high_arousal'

def get_song_ids(emotion, arousal_score):
	"""Get song IDs based on emotion and arousal score"""
	emotion_key = emotion.lower() if emotion else None
	
	# Handle emotions not in our map
	if emotion_key not in emotion_map:
		emotion_key = None
	
	# Get arousal level
	arousal_level = get_arousal_level(arousal_score)
	
	# Get song IDs
	song_ids = emotion_map[emotion_key][arousal_level]
	
	return {
		'song_ids': song_ids
	}

# Music control functions 
def play_music(song_info=None):
    global music_playing
    music_playing = True

    if song_info:
        # Select ONE random track from the given song_ids list
        song_id = random.choice(song_info['song_ids'])
        

        print(f"   Selected Emotion Playlist: {song_info['emotion'].upper()}")
        print(f"   Arousal Level: {song_info['arousal_level'].upper()}")
        print(f"   Playing Track ID: {song_id}")

        song_details = song_id[list(song_id.keys())[0]]
        # ---------------------------------------
        #  SEND TRACK ID TO ARDUINO / DFPLAYER
        # ---------------------------------------
        #command = f"PLAY:{song_id}\n"
		
        con.write(song_id.encode('utf-8'))
        con.write(song_details.encode('utf-8'))
    

    else:
        pass
       # print("Music: PLAY")
       # con.write(b"PLAY\n")
		

def pause_music():
    global music_playing
    music_playing = False

    print("Music: PAUSE")
    con.write(b"PAUSE\n")

def record_emotion():
	global detected_emotion
	print("Recording emotion for 5 seconds...")
	detected_emotion = capture_emotion_5sec()  # Calls detection.py function
	print(f"Emotion detected: {detected_emotion}")
	return detected_emotion



SampleRate = 50			# How often we're taking values from the Arduino per second, pulse sensor must have the same value
SampleWindow = 10			# How long in seconds each window of calculation will be
SampleNum = SampleRate * SampleWindow 	# Number of Samples we'll be analysing

RespirationRange = [0.1,0.5]		# For 6 to 30 Breaths/min (multiply by 60)
BPMRange = [0.8,2.5]			# For 48 to 150BPM	   (multiply by 60)

DataSet = []

try:
	while True:
		record = con.readline().decode('utf-8').strip()
		if record:
			# Check if it's a button input (B1, B2, B3) or sensor data
			if record.startswith('B1'):
				# Button 1: Play music (set flag to waiting for release)
				button1_pressed = True
				
			elif record.startswith('B1_RELEASE'):
				# Button 1 released: activate function
				if button1_pressed:
					# Get song recommendation if emotion was captured
					if detected_emotion is not None and 'arousal_score' in globals():
						song_info = get_song_ids(detected_emotion, arousal_score)
						print(f"\n--- Song Selection ---")
						print(f"Emotion: {song_info['emotion'].upper()}")
						print(f"Arousal Score: {song_info['arousal_score']:.2f}")
						print(f"Arousal Level: {song_info['arousal_level'].upper()}")
						print(f"Song IDs: {', '.join(song_info['song_ids'])}")
						print("---------------------\n")
						play_music(song_info)
					else:
						play_music()
				button1_pressed = False
				
			elif record.startswith('B2'):
				# Button 2: Pause music (set flag to waiting for release)
				button2_pressed = True
				
			elif record.startswith('B2_RELEASE'):
				# Button 2 released: activate function
				if button2_pressed:
					pause_music()
				button2_pressed = False
				
			elif record.startswith('B3'):
				# Button 3: Record emotion (set flag to waiting for release)
				button3_pressed = True
				
			elif record.startswith('B3_RELEASE'):
				# Button 3 released: activate function
				if button3_pressed:
					# Run emotion detection for 5 seconds
					record_emotion()
				button3_pressed = False
			
			# Try to process as sensor data (BPM and RR) regardless of button input
			try:
				DataSet.append(int(record))
				if len(DataSet) > SampleNum:
					DataSet.pop(0)
				if len(DataSet) == SampleNum:

					DetrendedData = numpy.array(DataSet) - numpy.mean(DataSet)		# Finding variance about the mean
					freqStrength = fft(DetrendedData)					# Finds the strength of the frequencies
					freqSample = fftfreq(SampleNum, 1 / SampleRate)				# Creates a list of frequencies, from 0.1Hz to 2.5Hz
					PositiveFrequencies = numpy.where(freqSample > 0)
				
					PositivefreqStrength = numpy.abs(freqStrength[PositiveFrequencies])
					PositivefreqSample = freqSample[PositiveFrequencies]

					peaks, junkdata = find_peaks(PositivefreqStrength, height=numpy.max(PositivefreqStrength) * 0.1)	# Unpacks data from find_peaks				
					RespirationRate = 0	# Both readings will be read per second, not per minute
					BPRate = 0		# Same here
				
					for peak in peaks:
						freq = PositivefreqSample[peak]
					
					if freq >= RespirationRange[0] and freq <= RespirationRange[1]:
						RespirationRate = freq * 60

					if freq >= BPMRange[0] and freq <= BPMRange[1]:
						BPRate = freq * 60
				
				arousal_score = 0.4*BPRate + 0.6*RespirationRate
				
				
			except ValueError:
				pass	# Not the values we require, moving on
except KeyboardInterrupt:
	print("Operations stopped.")
	con.close()
	

