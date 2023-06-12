import os
import sys
import cv2
import time
import random

PYTHONPATH = '/home/fabio/src/darknet'
#os.environ['PYTHONPATH'] = PYTHONPATH
sys.path.append(PYTHONPATH)

import darknet
import cv2

from collections     import deque
from queue           import Queue

class Darknet(str):
 
    data_file_v3   = "/home/fabio/src/darknet/cfg/coco.data"
    weights_v3     = "/home/fabio/src/darknet/yolov3.weights"
    config_file_v3 = "/home/fabio/src/darknet/yolov3.cfg"
    #input_path_v3  = "/home/fabio/src/darknet/data/crossing_480p.mp4"
    #output_path_v3 = "/home/fabio/src/darknet/output_video.mp4"
     
    data_file_v3_tiny   = "/home/fabio/src/darknet/cfg/coco.data"
    weights_v3_tiny     = "/home/fabio/src/darknet/yolov3-tiny.weights"
    config_file_v3_tiny = "/home/fabio/src/darknet/yolov3-tiny.cfg"

    data_file_v4_tiny   = "/home/fabio/src/darknet/cfg/coco.data"
    weights_v4_tiny     = "/home/fabio/src/darknet/yolov4-tiny.weights"
    config_file_v4_tiny = "/home/fabio/src/darknet/yolov4-tiny.cfg"
  
    thresh=.25
    dont_show=True

    frame_queue = Queue()
    fps_queue   = Queue(maxsize=1)
    darknet_image_queue = Queue(maxsize=1)
    detections_queue    = Queue(maxsize=1)
    
    coda_frame = deque(maxlen=15)
    cv2_queue  = deque(maxlen=15)
    img_queue  = deque(maxlen=15)
    prediction_queue= deque(maxlen=15)
    
    tipoRete=""

    def __init__(self,tipoRete):
        self.tipoRete=tipoRete
        print("Ho creato una rete "+tipoRete)
        if(tipoRete=="v3"):
            self.network, self.class_names, self.class_colors = darknet.load_network(
            self.config_file_v3,
            self.data_file_v3,
            self.weights_v3,
            batch_size=1
            )
            self.darknet_width  = darknet.network_width (self.network)
            self.darknet_height = darknet.network_height(self.network)
        elif(tipoRete=="v3_tiny"):
            self.network, self.class_names, self.class_colors = darknet.load_network(
            self.config_file_v3_tiny,
            self.data_file_v3_tiny,
            self.weights_v3_tiny,
            batch_size=1
            )
            self.darknet_width  = darknet.network_width (self.network)
            self.darknet_height = darknet.network_height(self.network)
        elif(tipoRete=="v4_tiny"):
            self.network, self.class_names, self.class_colors = darknet.load_network(
            self.config_file_v4_tiny,
            self.data_file_v4_tiny,
            self.weights_v4_tiny,
            batch_size=1
            )
            self.darknet_width  = darknet.network_width (self.network)
            self.darknet_height = darknet.network_height(self.network)

    def detection(self, frame): 
        #print("Detection")
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (self.darknet_width, self.darknet_height),interpolation=cv2.INTER_LINEAR)
        img_for_detect = darknet.make_image(self.darknet_width, self.darknet_height, 3)
        
        darknet.copy_image_from_bytes(img_for_detect, frame_resized.tobytes())
        self.inference(img_for_detect,frame)
        
    def inference(self,darknet_image,original_frame):
        #print("Inference "+self.tipoRete)
        start_time = time.time()
        detections = darknet.detect_image(self.network, self.class_names, darknet_image, self.thresh)
        darknet.free_image(darknet_image)
        self.drawing(detections, original_frame, start_time)

    def draw_text_on_frame(self,frame,text,offset_sx,offset_dw):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_color = (255, 255, 255)  # Colore del testo in formato BGR
        thickness = 2
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        x = offset_sx  # Offset orizzontale dal margine sinistro
        y = frame.shape[0] - offset_dw  # Offset verticale dal margine superiore
        cv2.rectangle(frame, (x, y - text_size[1]), (x + text_size[0], y), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, text, (x, y), font, font_scale, font_color, thickness)
        return frame
    
    def drawing(self, rilevamenti, original_frame, start_time): 
        #print("Drawing")
        #random.seed(3)  
        frame = original_frame
        detections = rilevamenti
        detections_adjusted = []
        #print(darknet.print_json(detections))
        self.add_predictions(darknet.print_json(detections))
        if frame is not None:
            for label, confidence, bbox in detections:
                bbox_adjusted = self.convert2original(frame, bbox)
                detections_adjusted.append((str(label), confidence, bbox_adjusted))
            image = darknet.draw_boxes(detections_adjusted, frame, self.class_colors)

            elapsed_time = time.time() - start_time
            elapsed_time_ms = elapsed_time * 1000
            testo="FPS ="+str(round(1000/elapsed_time_ms,3))
            image=self.draw_text_on_frame(image,testo,30,20)
            self.add_frame(image)
            

    
       
    # Metodi di utilità
    
    # Metodi per l'aggiunta dei frame alle relative code
    def add_frame(self,frame):
        self.cv2_queue.append(frame)
        
    def get_latest_frame(self):
        return self.cv2_queue[-1] if self.cv2_queue else None
    
    def get_predictions(self):
        return self.prediction_queue[-1] if self.prediction_queue else None
    
    def add_predictions(self,prediction):
        self.prediction_queue.append(prediction)
    
    def add_image(img):
        global img_queue
        img_queue.append(img)
        
    def get_latest_image():
        global img_queue
        return img_queue[-1] if img_queue else None

    def convert2relative(self,bbox):
        x, y, w, h  = bbox
        _height     = self.darknet_height
        _width      = self.darknet_width
        return x/_width, y/_height, w/_width, h/_height

    def convert2original(self,image, bbox):
        x, y, w, h = self.convert2relative(bbox)
        image_h, image_w, __ = image.shape
        orig_x       = int(x * image_w)
        orig_y       = int(y * image_h)
        orig_width   = int(w * image_w)
        orig_height  = int(h * image_h)
        bbox_converted = (orig_x, orig_y, orig_width, orig_height)
        return bbox_converted
   
    
    