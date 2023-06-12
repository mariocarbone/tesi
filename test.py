import os
import sys
import cv2
import time

PYTHONPATH = '/home/fabio/src/darknet'
 #os.environ['PYTHONPATH'] = PYTHONPATH
sys.path.append(PYTHONPATH)

import darknet

def get_from_buffer():
    img=[]
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    return frame
        
def start_yolo_v3(img):
    weights    ="/home/fabio/src/tesi/weights/yolov3.weights"
    data_file  ="/home/fabio/src/tesi/data/coco.data"
    config_file="/home/fabio/src/tesi/cfg/yolov3.cfg"
    input_path ="/home/fabio/src/tesi/data/crossing_480p.mp4"
    output_path="/home/fabio/src/tesi/output_video.mp4"
    thresh=.25
    dont_show=True
    network, class_names, class_colors = darknet.load_network(
            config_file,
            data_file,
            weights,
            batch_size=1
    )
    darknet_width = darknet.network_width(network)
    darknet_height = darknet.network_height(network)
    print("rete yolo v3 caricata")
    
def start_yolo_v3_tiny(img):
    weights    ="/home/fabio/src/tesi/weights/yolov3-tiny.weights"
    data_file  ="/home/fabio/src/tesi/data/coco.data"
    config_file="/home/fabio/src/tesi/cfg/yolov3-tiny.cfg"
    input_path ="/home/fabio/src/tesi/data/crossing_480p.mp4"
    output_path="/home/fabio/src/tesi/output_video.mp4"
    thresh=.25
    dont_show=True
    network, class_names, class_colors = darknet.load_network(
            config_file,
            data_file,
            weights,
            batch_size=1
    )
    darknet_width = darknet.network_width(network)
    darknet_height = darknet.network_height(network)
    print("rete yolo v3 tiny caricata") 


def start_yolo_v3_tiny_custom(img):
    weights    ="/home/fabio/src/tesi/weights/yolov4.weights"
    data_file  ="/home/fabio/src/tesi/data/coco.data"
    config_file="/home/fabio/src/tesi/cfg/yolov4-tiny.cfg"
    input_path ="/home/fabio/src/tesi/data/crossing_480p.mp4"
    output_path="/home/fabio/src/tesi/output_video.mp4"
    thresh=.25
    dont_show=True
    network, class_names, class_colors = darknet.load_network(
            config_file,
            data_file,
            weights,
            batch_size=1
    )
    darknet_width = darknet.network_width(network)
    darknet_height = darknet.network_height(network)
    print("rete yolo v4 caricata") 



def check_speed():
    return 130

def start_vision():
    while True:
        speed = check_speed()
        frame = get_from_buffer()
        if speed > 30:
            if speed > 100:
                start_yolo_v3(frame)
            else:
                start_yolo_v3_tiny(frame)
        else:
            start_yolo_v3_tiny_custom(frame)
            
start_vision()