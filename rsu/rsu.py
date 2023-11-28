import cv2
import threading
import time
import subprocess
import os
import numpy as np
import logging

from multiprocessing import Process, Value
from threading import Lock
from threading import Thread
from collections import deque
from queue import Queue

#Librerie
from detection import Tensorflow
from mqtt_lib import MQTTConnection
from rpi_lib import Raspberry
from alert_lib import Alert

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
cap = cv2.VideoCapture(0)

#MQTT INFO
broker_address = "192.168.1.6"
broker_port = 1883
topic_alert = "/alert"
topic_auto = "/smartcar"
topic_rsu = "/rsu"
rsu_id = "RSU_PI01"
rsu_deatils = {
    "id": rsu_id,
    "connected_clients": 0,
    "ssid": "RSU_PI01"#,
    #"gps": {"lat": 39.35613, "lon": 16.22815}
}
mqtt = MQTTConnection(broker_address, broker_port, topic_alert, topic_auto, topic_rsu, rsu_id)

veicoli_connessi = {}

# Istanze Moduli
tf_instance = Tensorflow()
rpi = Raspberry()
alert_instance = Alert(rsu_id, mqtt)

# Stato del veicolo
status_json = {}
status_lock = Lock()

# Prediction trovate su frame
prediction_json = {}
prediction_lock = Lock()

# Code dei frame
frame_queue = deque(maxlen=15) #Webcam
tf_queue = deque(maxlen=15) #Tensorflow Output

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
  
# Contatore FPS
start_time = time.time()
frame_counter = 1
contatore_media = 0
somma_tempi_frame = 0
media_frame = 0

# Funzione per acquisire i frame dalla webcam e aggiungerli al buffer
def capture_frames():
	global stop_threads, cap
	while not stop_threads:
		ret, frame = cap.read()
		if ret:
			add_frame(frame)
	cap.release()

# Funzione per effettuare object detection sui frame della coda
def detection():
	global frame_counter,somma_tempi_frame, media_frame, contatore_media,prediction_json, prediction_lock, stop_threads
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
				prediction_json = {}
		else:
			#logging.warning('Coda dei frame vuota') 
			#print(round(time.time()*1000), "- App Main > Coda dei frame vuota")
			continue

# Funzione per generare i frame per la Web UI
def generate_frames():
	global stop_threads
	while not stop_threads:
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
	status_obj = status
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

# API per arrestare i threads
@app.route('/stop_threads', methods=['POST'])
def stop_all_threads():
	global stop_threads
	stop_threads = True
	# azioni o pulizie se necessario prima di terminare i thread.
	return jsonify({"message": "Tutti i thread verranno fermati."})

if __name__ == "__main__":
	capture_thread = threading.Thread(target=capture_frames)
	detection_thread = threading.Thread(target=detection)
	flask_thread = threading.Thread(target=run_flask_app)

	flask_thread.start()
	capture_thread.start()
	time.sleep(0.1)
	detection_thread.start()

