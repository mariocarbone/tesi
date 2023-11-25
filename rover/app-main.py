import cv2
import threading
import time
import subprocess
import os
import numpy as np
import logging
#from distancesensor import get_distance_value

from multiprocessing import Process, Value
from threading import Lock
from threading import Thread
from collections import deque
from queue import Queue

#Webcam
from picamera2 import Picamera2
from libcamera import controls

#Librerie
from detection import Tensorflow
from control_lib import Vehicle_Control
from mqtt_lib import MQTTConnection
from alert_lib import Alert
from rpi_lib import Raspberry

#Web-UI
from flask import Flask, render_template, jsonify, Response
from flask_cors import CORS
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
CORS(app)

# Variabili di utilità
stop_threads = False

# Inizializzazione Camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# MQTT TOPIC & INFO
# Broker MQTT e Topic
broker_address = "192.168.1.6"
broker_port = 1883
topic_alert = "/alert/"
topic_auto = "/smartcar/"
topic_rsu = "/rsu/"
vehicle_id = "ROVER"

mqtt = MQTTConnection(broker_address, broker_port, topic_alert, topic_auto, vehicle_id)

# Istanze Moduli
tf_instance = Tensorflow()
vehicle_control = Vehicle_Control()
rpi = Raspberry()
alert_instance = Alert(vehicle_id, vehicle_control, rpi, mqtt)

# Stato del veicolo
status_json = {}
status_lock = Lock()

# Prediction trovate su frame
prediction_json = {}
prediction_lock = Lock()

# Code dei frame
frame_queue = deque(maxlen=15) #Webcam
tf_queue = deque(maxlen=15) #Tensorflow Output
img_queue = deque(maxlen=15) #Web Output

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
  
# Contatore FPS
start_time = time.time()
frame_counter = 1
contatore_media = 0
somma_tempi_frame = 0
media_frame = 0

# Funzione per acquisire i frame dalla webcam e aggiungerli al buffer
def capture_frames():
	global stop_threads
	while not stop_threads:
		frame = picam2.capture_array()
		add_frame(frame)
	picam2.stop()

# Funzione per aggiornare lo stato del veicolo
def update_vehicle_status():
	global status_json, vehicle_control, stop_threads#, mqtt
	while not stop_threads:
		vehicle_control.update_status()
		#with status_lock:
		status_json = vehicle_control.status
		#mqtt.send_vehicle_status(status_json)
		time.sleep(0.2)

def update_other_aps():
	global rpi, stop_threads
	while not stop_threads:
		rpi.update_other_aps()
		time.sleep(1)

# Funzione per effettuare object detection sui frame della coda
def detection():
	global frame_counter,somma_tempi_frame, media_frame, contatore_media,prediction_json, prediction_lock, stop_threads, alert_instance
	while not stop_threads:
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
				#with prediction_lock:
				prediction_json = json
				alert_instance.process_predictions(prediction_json)
		else:
			#logging.warning('Coda dei frame vuota') 
			#print(round(time.time()*1000), "- App Main > Coda dei frame vuota")
			continue

# Funzione per processare le immagini con OpenCV ed aggiungere linee
def cv2Lines():
	global stop_threads
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

	while not stop_threads:
		
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
	global stop_threads
	while not stop_threads:
		#if len(img_queue) > 0:
		if len(tf_queue) > 0:
			frame = get_latest_tf_frame() #Prendo l'ultima immagine
			ret, buffer = cv2.imencode('.jpg', frame) #Effettuo l'encoding dell'immagine
			if ret:
				yield (b'--frame\r\n'
					   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
		else:
			continue

# Funzione per l'avvio di flask
def run_flask_app():
	global stop_threads
	app.run(host='0.0.0.0', port=5000, debug=not stop_threads, use_reloader=False)

# Homepage
@app.route('/')
def index():
	return render_template('index.html')

# API per ottenere il flusso video        
@app.route('/video_feed')
def video_feed():
	return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

# API per ottenere lo stato 
@app.route('/get_status', methods=['GET'])
def get_status():
	global status_json#, status_lock
	status_obj = vehicle_control.status
	return jsonify(status_obj)  
	
# API per ottenere le prediction
@app.route('/get_predictions', methods=['GET'])
def get_predictions():
	global prediction_json#, prediction_lock

	#with prediction_lock:
	predicted_objects = prediction_json
		
	return jsonify(predicted_objects)    

# API per ottenere informazioni su raspberry pi 
@app.route('/pi/get_info', methods=['GET'])
def get_connections():
	return jsonify(rpi.get_system_status())  

# API per ottenere informazioni su raspberry pi 
@app.route('/alert/alert_sended', methods=['GET'])
def get_alert_sended():
	return jsonify(alert_instance.alert_sended)  

# API per ottenere informazioni su raspberry pi 
@app.route('/alert/alert_received', methods=['GET'])
def get_alert_received():
	return jsonify(alert_instance.alert_received)  


# API per far partire il rover
@app.route('/rover/start', methods=['POST'])
def rover_start():
	global vehicle_control
	vehicle_control.start_path()
	print("ROVER START")
	return jsonify({"message": "Rover partito!"})

# API per far fermare il rover
@app.route('/rover/stop', methods=['POST'])
def rover_stop():
	global vehicle_control
	vehicle_control.stop_path()
	print("ROVER STOP")
	return jsonify({"message": "Rover fermato!"})

# API per arrestare i threads
@app.route('/stop_threads', methods=['POST'])
def stop_all_threads():
	global stop_threads
	stop_threads = True
	# azioni o pulizie se necessario prima di terminare i thread.
	return jsonify({"message": "Tutti i thread verranno fermati."})

# COMANDI MANUALI ROVER
@app.route('/rover/commands/forward', methods=['POST'])
def rover_manual_forward():
	global vehicle_control
	vehicle_control.arduino.speed(70)
	print("Rover Forward")
	return jsonify({"message": "Rover Forward!"})

@app.route('/rover/commands/left', methods=['POST'])
def rover_manual_left():
	global vehicle_control
	vehicle_control.arduino.steer(vehicle_control.arduino.str_left,3)
	print("Rover Left")
	return jsonify({"message": "Rover Left!"})

@app.route('/rover/commands/right', methods=['POST'])
def rover_manual_right():
	global vehicle_control
	vehicle_control.arduino.steer(vehicle_control.arduino.str_right,3)
	print("Rover Right")
	return jsonify({"message": "Rover Right!"})

@app.route('/rover/commands/brake', methods=['POST'])
def rover_manual_brake():
	global vehicle_control
	vehicle_control.arduino.stop()
	print("Rover Brake")
	return jsonify({"message": "Rover Brake!"})

@app.route('/rover/commands/stop', methods=['POST'])
def rover_manual_stop():
	global vehicle_control
	vehicle_control.arduino.stop()
	print("Rover Stop")
	return jsonify({"message": "Rover Stop!"})

@app.route('/rover/commands/reverse', methods=['POST'])
def rover_manual_reverse():
	global vehicle_control
	vehicle_control.arduino.backward()
	print("Rover Reverse")
	return jsonify({"message": "Rover Reverse!"})

if __name__ == "__main__":
	capture_thread = threading.Thread(target=capture_frames)
	#cv2_thread = threading.Thread(target=cv2Lines)
	detection_thread = threading.Thread(target=detection)
	status_thread = threading.Thread(target=update_vehicle_status)
	aps_thread = threading.Thread(target=update_other_aps)
	flask_thread = threading.Thread(target=run_flask_app)

	flask_thread.start()
	capture_thread.start()
	time.sleep(0.1)
	detection_thread.start()
	#cv2_thread.start()
	status_thread.start()
	aps_thread.start()
