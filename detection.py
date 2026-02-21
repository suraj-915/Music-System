import cv2
from deepface import DeepFace
from cvzone.HandTrackingModule import HandDetector
import time

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def capture_emotion_5sec():
	"""
	Runs emotion detection for 5 seconds and returns the emotion detected at the end.
	Returns the dominant emotion as a string.
	"""
	cap = cv2.VideoCapture(0)  # Use camera 0
	if not cap.isOpened():
		print("Error: Cannot open webcam")
		return None
	
	start_time = time.time()
	duration = 5  # 5 seconds
	captured_emotion = None
	
	try:
		while True:
			ret, frame = cap.read()
			if not ret:
				break
			
			elapsed_time = time.time() - start_time
			
			# Check if 5 seconds have passed
			if elapsed_time >= duration:
				break
			
			rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			
			try:
				result = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False)
				captured_emotion = result[0]['dominant_emotion']
			except:
				pass
			
			# Draw rectangle around face
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			faces = faceCascade.detectMultiScale(gray, 1.1, 4)
			for (x, y, w, h) in faces:
				cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
			
			# Display emotion and countdown
			font = cv2.FONT_HERSHEY_SIMPLEX
			if captured_emotion and captured_emotion not in ['surprise', 'fear', 'disgust']:
				cv2.putText(frame, captured_emotion, (50, 50), font, 1, (0, 0, 255), 2, cv2.LINE_4)
			
			remaining_time = duration - elapsed_time
			cv2.putText(frame, f"Recording: {remaining_time:.1f}s", (50, 100), font, 1, (0, 255, 0), 2)
			
			cv2.imshow("Emotion Detection - Recording", frame)
			if cv2.waitKey(10) & 0xFF == ord('q'):
				break
	
	finally:
		cap.release()
		cv2.destroyAllWindows()
	
	return captured_emotion


# Original detection loop (for standalone use)
def run_detection_standalone():
	"""Runs the original detection loop with hand tracking"""
	cap = cv2.VideoCapture(0)
	if not cap.isOpened():
		cap = cv2.VideoCapture(1)
		if not cap.isOpened():
			raise IOError("Cannot open webcam")
	
	detector = HandDetector(detectionCon=0.8, maxHands=1)

	while True:
		ret, frame = cap.read()
		if not ret:
			break
		rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		
		result = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False)

		# Draw rectangle around face
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faces = faceCascade.detectMultiScale(gray, 1.1, 4)
		for (x, y, w, h) in faces:
			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

		emotion = result[0]['dominant_emotion']
		font = cv2.FONT_HERSHEY_SIMPLEX

		if emotion not in ['surprise', 'fear', 'disgust']:
			cv2.putText(frame, emotion, (50, 50), font, 1, (0, 0, 255), 2, cv2.LINE_4)

		# Initialize hand detection
		hands, img = detector.findHands(frame)
		if hands:
			ImList = hands[0]
			fingerUp = detector.fingersUp(ImList)
			print(fingerUp)

			if fingerUp == [0, 0, 0, 0, 0]:
				cv2.putText(frame, "Reset", (350, 50), font, 1, (0, 0, 255), 2)

			elif fingerUp == [1, 0, 0, 0, 0]:
				cv2.putText(frame, "Play", (350, 50), font, 1, (0, 0, 255), 2)

			elif fingerUp == [1, 1, 1, 1, 1]:
				cv2.putText(frame, "Pause", (350, 50), font, 1, (0, 0, 255), 2)
		
		cv2.imshow("Emotion and hand detection", frame)
		if cv2.waitKey(2) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()


# Run standalone if executed directly
if __name__ == "__main__":
	run_detection_standalone()






    