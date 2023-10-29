import argparse
import sys
import time
import utils
import threading
import queue
from collections import deque

import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision


class Tensorflow(str):

	#Coda dei frame
	tf_queue = deque(maxlen=15)
	#Coda dei rilevamenti JSON
	prd_queue = deque(maxlen=15)
	
	def add_image(self,image):
		self.tf_queue.append(image)

	def get_latest_image(self):
		return self.tf_queue[-1] if self.tf_queue else None
	
	def get_predictions(self):
		return self.prd_queue[-1] if self.prd_queue else None

	def add_predictions(self,prediction):
		self.prd_queue.append(prediction)
		
	# Variables to calculate FPS	
	fps=0
	somma_fps = 0
	counter = 0
	num_fps_media = 10
	fps_avg = 0

	# Visualization parameters
	row_size = 20  # pixels
	left_margin = 24  # pixels
	text_color = (0, 255, 255)  # white
	font_size = 1
	font_thickness = 1

	# Configuration of TF
	model= 'efficientdet_lite0.tflite'
	camera_id: 0
	width = 640
	height = 480
	num_threads = 4
	enable_edgetpu = False

	# Initialize the object detection model
	base_options = core.BaseOptions(file_name=model, use_coral=enable_edgetpu, num_threads=num_threads)
	detection_options = processor.DetectionOptions(max_results=5, score_threshold=0.35, category_name_allowlist=['car','person'])
	options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)
	detector = vision.ObjectDetector.create_from_options(options)	

	def __init__(self):
		print("Tensorflow > Istanza Avviata!")

	def detect(self,frame):
		
		start_time = time.time()
				
		image = frame
		
		self.counter += 1
		image = cv2.flip(image, 1)

		# Convert the image from BGR to RGB as required by the TFLite model.
		rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

		# Create a TensorImage object from the RGB image.
		input_tensor = vision.TensorImage.create_from_array(rgb_image)
		#input_tensor = vision.TensorImage.create_from_array(image)

		# Run object detection estimation using the model.
		detection_result = self.detector.detect(input_tensor)

		# Draw keypoints and edges on input image
		image = utils.visualize(image, detection_result)
		
		# Detection to JSON
		lock = threading.Lock()
		dizionario = {}
		cont = 0
		dizionario["timestamp"]=time.time()
		
		for detected_obj in detection_result.detections:
			out = {
			"category": detected_obj.categories[0].category_name,
			"score": detected_obj.categories[0].score,
			"coordinates": {
			"x": detected_obj.bounding_box.origin_x,
			"y": detected_obj.bounding_box.origin_y,
			"w": detected_obj.bounding_box.width,
			"h": detected_obj.bounding_box.height,
				}
			} 
			lock.acquire()
			try:
				dizionario[cont] = out
				cont += 1
			finally:
				lock.release()

		end_time = time.time()
		self.somma_fps += 1/(end_time - start_time)
		#self.fps = 1/(end_time - start_time)

		if self.counter % self.num_fps_media == 0:
			fps_avg = self.somma_fps / self.num_fps_media
			self.fps = fps_avg
			self.somma_fps = 0
			self.counter = 0
			
		# Show the FPS
		fps_text = 'FPS = {:.1f}'.format(self.fps)
		text_location = (self.left_margin, self.row_size)
		cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN, self.font_size, self.text_color, self.font_thickness)

		self.add_image(image)
		
		if(cont>0):
			self.add_predictions(dizionario)
			return True
		else:
			return False
