import cv2
import threading
import time
import subprocess
import os
import numpy as np
import logging
from multiprocessing import Value
from threading import Lock
from threading import Thread
from collections import deque
from queue import Queue

#Webcam
from picamera2 import Picamera2
from libcamera import controls

#Librerie
from detection import Tensorflow
from arduino_lib import Arduino
from rpi_lib import Raspberry
from mqtt_lib import MQTTConnection

#Web-UI
from flask import Flask, render_template, Response
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# Distanza Misurata con Sensore ad Ultrasuoni
distance = Value('d',0.0)
distance_lock = Lock()

# Distanza Misurata con Sensore ad Ultrasuoni
prediction_json = Value('d',0.0)
prediction_lock = Lock()

# Code dei frame
frame_queue = deque(maxlen=15) #Webcam
tf_queue = deque(maxlen=15) #Tensorflow Output
img_queue = deque(maxlen=15) #Web Output

tf_instance = Tensorflow()
arduino = Arduino("/dev/ttyACM0", 9600, 1, 1)
raspberry = Raspberry()

topic_alert = "/alert/"
topic_auto = "/smartcar/"
vehicle_id = "ROVER"

#mqtt = MQTTConnection("192.168.1.2", "8000", topic_alert, topic_auto, vehicle_id)

# Metodi per l'aggiunta dei frame alle relative code
def add_frame(frame):
	global frame_queue
	frame_queue.append(frame)
	
def get_latest_frame():
	global frame_queue
	return frame_queue[-1] if frame_queue else None
	
def add_tf_frame(frame):
	global tf_queue
	tf_queue.append(frame)
	
def get_latest_tf_frame():
	global tf_queue
	return tf_queue[-1] if tf_queue else None

def add_image(img):
	global img_queue
	img_queue.append(img)
	
def get_latest_image():
	global img_queue
	return img_queue[-1] if img_queue else None
	
#Coda Prediction
  
# Contatore FPS
counter, fps = 0, 0
start_time = time.time()
frame_counter = 1
contatore_media = 0
somma_tempi_frame = 0
media_frame = 0

# Inizializzazione Camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# Funzione per acquisire i frame dalla webcam e aggiungerli al buffer
def capture_frames():
	while True:
		frame=picam2.capture_array()
		add_frame(frame)    
	picam2.stop()

# Funzione per aggiornare lo stato del veicolo
def update_vehicle_status():
	while True:
		with distance_lock:
			distance.value = round(raspberry.measure_distance(), 2)
		time.sleep(0.5)
	picam2.stop()
		
# Funzione per processare le immagini con OpenCV
def cv2Lines():
	
	green_color = (0, 255, 0, 50)  # BGR colore verde
	red_color = (0, 0, 255, 50)  # BGR colore verde
	orange_color = (0, 125, 255, 50)  # BGR colore verde
	yellow_color = (0, 255, 255, 50) # BGR colore giallo    
							   
	linee_rosse = [((77,356),(563,356)), #Orizzontale 
					((0,480),(77,356)), #Basso Sinistra
					((640,480),(563,356))] #Basso Destra
					
	linee_arancio = [((180,186),(460,186)), #Orizzontale 
					((77,356),(180,186)),  #Basso Sinistra
					((460,186),(563,356))] #Basso Destra
					
	linee_verdi = [((230,106),(410,106)),
					((180,186),(230,106)),
					((410,106),(460,186))]

	while True:
		
		if len(tf_queue) > 0:
			frame = get_latest_tf_frame()

			#Linea Safe Area
			for line in linee_rosse:
				pt1, pt2 = line
				#cv2.line(overlay, pt1, pt2, red_color, thickness=thickness)
				image_with_line = cv2.line(frame, pt1, pt2, red_color, thickness=2)#, lineType=cv2.LINE_AA)

			for line in linee_arancio:
				pt1, pt2 = line
				#cv2.line(overlay, pt1, pt2, orange_color, thickness=thickness)
				image_with_line = cv2.line(frame, pt1, pt2, orange_color, thickness=2)#, lineType=cv2.LINE_AA)   

			for line in linee_verdi:
				pt1, pt2 = line
				#cv2.line(overlay, pt1, pt2, green_color, thickness=thickness)
				image_with_line = cv2.line(frame, pt1, pt2, green_color, thickness=2)#, lineType=cv2.LINE_AA)      
			 
			add_image(image_with_line) #Aggiungo il frame alla coda delle immagini modificate
		else:
			continue

# Funzione per generare i frame per la Web UI
def generate_frames():
	while True:
		if len(img_queue) > 0:
			frame = get_latest_image() #Prendo l'ultima immagine
			ret, buffer = cv2.imencode('.jpg', frame) #Effettuo l'encoding dell'immagine
			if ret:
				yield (b'--frame\r\n'
					   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
		else:
			continue

def detection():
	global frame_counter,somma_tempi_frame, media_frame, contatore_media
	while True:
		if len(frame_queue) > 0:
			inizio = round(time.time()*1000)
			#print(inizio, "- App Main > Avvio detection del frame n.", frame_counter)
			frame = get_latest_frame()
			detected = tf_instance.detect(frame)
			fine = round(time.time()*1000)
			ms = fine-inizio
			somma_tempi_frame = somma_tempi_frame + ms
			if(contatore_media % 10 == 0):
				media_frame = round(somma_tempi_frame/10)
				somma_tempi_frame = 0
				contatore_media = 0
			logging.info(fine, "- App Main > Fine detection del frame - Tempo impiegato:", ms,"ms - Tempo medio:", media_frame , "ms") 
			#print(fine, "- App Main > Fine detection del frame - Tempo impiegato:", ms,"ms - Tempo medio:", media_frame , "ms")
			image = tf_instance.get_latest_image()
			add_tf_frame(image)
			json=tf_instance.get_predictions()
			t_prediction = round(time.time()*1000)
			t_final = t_prediction - fine
			#print(t_prediction, "- App Main > Elaboro prediction del frame n.", frame_counter, "- Tempo impiegato:", t_final, "ms")
			frame_counter = frame_counter+1 
			contatore_media = contatore_media+1
			if(detected):
				print(json)
		else:
			#logging.warning('Coda dei frame vuota') 
			#print(round(time.time()*1000), "- App Main > Coda dei frame vuota")
			continue

	#picam2.stop()

	

# Homepage
@app.route('/')
def index():
	return render_template('index.html')

# API per ottenere il flusso video        
@app.route('/video_feed')
def video_feed():
	return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

# API per ottenere la distanza
@app.route('/get_distance', methods=['GET'])
def get_distance():
	global distance, distance_lock
	
	#distance_value = raspberry.measure_distance()

	with distance_lock:
		distance_value = distance.value
		
	return str(distance_value)
	
# API per ottenere la distanza
@app.route('/get_predictions', methods=['GET'])
def get_predictions():
	global prediction_json, prediction_lock

	with prediction_lock:
		predicted_objects = prediction_json.value
		
	return str(predicted_objects)    

	
def run_flask_app():
	app.run(host='0.0.0.0', port=5000) 

# Main
if __name__ == "__main__":
	
	# Avvia i thread
	capture_thread = threading.Thread(target=capture_frames)
	detection_thread = threading.Thread(target=detection)
	status_thread = threading.Thread(target=update_vehicle_status)
	cv2_thread = threading.Thread(target=cv2Lines)
	flask_thread = threading.Thread(target=run_flask_app)
	flask_thread.start()
	status_thread.start()
	capture_thread.start()   
	time.sleep(0.1)
	detection_thread.start()
	time.sleep(0.1)
	cv2_thread.start()
	
	status_thread.join()
	detection_thread.join()
	cv2_thread.join()
	flask_thread.join()
