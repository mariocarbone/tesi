from multiprocessing import Value
from collections import deque
from threading import Thread
from threading import Lock
from queue import Queue
from threading import Thread, enumerate
import threading
import argparse
import darknet
import time
import cv2
import os
import random
from ctypes import *
import numpy as np
from flask import Flask, render_template, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# import RPi.GPIO as GPIO

ld_library_path = os.environ.get('LD_LIBRARY_PATH', '')
ld_library_path += ':/usr/local/cuda-12.0/targets/x86_64-linux/lib'
ld_library_path += ':/usr/local/lib'
ld_library_path += ':/usr/local/cuda/lib64'
os.environ['LD_LIBRARY_PATH'] = ld_library_path

weights = "/home/fabio/src/darknet/yolov3-tiny.weights"
data_file = "/home/fabio/src/darknet/cfg/coco.data"
config_file = "/home/fabio/src/darknet/yolov3-tiny.cfg"
input_path = "/home/fabio/src/darknet/data/crossing_480p.mp4"
output_path = "/home/fabio/src/darknet/output_video.mp4"
thresh = .25
dont_show = True
ext_output = "output_video.txt"
cap = cv2.VideoCapture(input_path)
network, class_names, class_colors = darknet.load_network(
    config_file,
    data_file,
    weights,
    batch_size=1
)

darknet_width = darknet.network_width(network)
darknet_height = darknet.network_height(network)
video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
current_json = []

frame_queue = Queue() # coda frame prelevati dal flusso video
darknet_image_queue = Queue(maxsize=1)
detections_queue = Queue(maxsize=1)
fps_queue = Queue(maxsize=1)

cv2_queue = deque(maxlen=15)  # coda dei frame da processare in OpenCV
img_queue = deque(maxlen=15)  # coda dei frame per visualizzazione web

# Distanza Misurata con Sensore ad Ultrasuoni
distance = Value('d', 0.0)
distance_lock = Lock()

# Metodi per l'aggiunta dei frame alle relative code

def add_frame(frame):
    global cv2_queue
    cv2_queue.append(frame)

def get_latest_frame():  # preleva l'utimo frame aggiunto
    global cv2_queue
    return cv2_queue[-1] if cv2_queue else None

def add_image(img):
    global img_queue
    img_queue.append(img)

def get_latest_image():  # preleva l'utimo frame aggiunto
    global img_queue
    return img_queue[-1] if img_queue else None

# Funzione per acquisire i frame dalla webcam e aggiungerli al buffer

def capture_frames():
    # Webcam
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        if ret:
            add_frame(frame)

    video_capture.release()

'''
def set_saved_video(input_video, output_video, size):
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    fps = int(input_video.get(cv2.CAP_PROP_FPS))
    video = cv2.VideoWriter(output_video, fourcc, fps, size)
    return video
'''

def convert2relative(bbox):
    x, y, w, h = bbox
    _height = darknet_height
    _width = darknet_width
    return x/_width, y/_height, w/_width, h/_height


def convert2original(image, bbox):
    x, y, w, h = convert2relative(bbox)

    image_h, image_w, __ = image.shape

    orig_x = int(x * image_w)
    orig_y = int(y * image_h)
    orig_width = int(w * image_w)
    orig_height = int(h * image_h)

    bbox_converted = (orig_x, orig_y, orig_width, orig_height)

    return bbox_converted


def convert4cropping(image, bbox):
    x, y, w, h = convert2relative(bbox)

    image_h, image_w, __ = image.shape

    orig_left = int((x - w / 2.) * image_w)
    orig_right = int((x + w / 2.) * image_w)
    orig_top = int((y - h / 2.) * image_h)
    orig_bottom = int((y + h / 2.) * image_h)

    if (orig_left < 0):
        orig_left = 0
    if (orig_right > image_w - 1):
        orig_right = image_w - 1
    if (orig_top < 0):
        orig_top = 0
    if (orig_bottom > image_h - 1):
        orig_bottom = image_h - 1

    bbox_cropping = (orig_left, orig_top, orig_right, orig_bottom)

    return bbox_cropping


def video_capture(frame_queue, darknet_image_queue):
    global cap
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(
            frame_rgb, (darknet_width, darknet_height), interpolation=cv2.INTER_LINEAR)
        frame_queue.put(frame)
        # add_frame(frame)
        img_for_detect = darknet.make_image(darknet_width, darknet_height, 3)
        darknet.copy_image_from_bytes(img_for_detect, frame_resized.tobytes())
        darknet_image_queue.put(img_for_detect)
    cap.release()


lock = threading.Lock()
risultati = {}

def get_json():
    global risultati
    return risultati

def set_json(json):
    global risultati, lock
    lock.acquire()
    try:
        risultati = json
    finally:
        lock.release()

def inference(darknet_image_queue, detections_queue, fps_queue):
    global cap, thresh
    while cap.isOpened():
        time.sleep(0.04)
        darknet_image = darknet_image_queue.get()
        prev_time = time.time()
        detections = darknet.detect_image(
            network, class_names, darknet_image, thresh=thresh)
        detections_queue.put(detections)
        fps = int(1/(time.time() - prev_time))
        fps_queue.put(fps)
        # print("FPS: {}".format(fps))
        # darknet.print_detections(detections, ext_output)
        set_json(darknet.print_json(detections))
        # risultati=darknet.print_json(detections)

        darknet.free_image(darknet_image)
    cap.release()

def drawing(frame_queue, detections_queue, fps_queue):
    global cap
    random.seed(3)  # deterministic bbox colors
    # video = set_saved_video(cap, output_path, (video_width, video_height))
    while cap.isOpened():
        time.sleep(0.04)
        frame = frame_queue.get()
        # frame=get_latest_frame()
        detections = detections_queue.get()
        fps = fps_queue.get()
        detections_adjusted = []
        if frame is not None:
            for label, confidence, bbox in detections:
                bbox_adjusted = convert2original(frame, bbox)
                detections_adjusted.append(
                    (str(label), confidence, bbox_adjusted))
            image = darknet.draw_boxes(
                detections_adjusted, frame, class_colors)
            if not dont_show:
                cv2.imshow('Inference', image)
            # if output_path is not None:
            #    video.write(image)
            add_frame(image)
            # if cv2.waitKey(fps) == 27:
            #    break
    cap.release()
    # video.release()
    cv2.destroyAllWindows()


"""   
# Funzione per misurare la distanza
def measure_distance():
    
    global distance, distance_value
    GPIO.setmode(GPIO.BOARD)
    
    trig_pin = 7
    echo_pin = 11
    GPIO.setup(trig_pin, GPIO.OUT)
    GPIO.setup(echo_pin, GPIO.IN)
    
    while True:
        
        GPIO.output(trig_pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(trig_pin, GPIO.LOW)
        
        while GPIO.input(echo_pin) == 0:
            pulse_start = time.time()
        while GPIO.input(echo_pin) == 1:
            pulse_end = time.time()
            
        pulse_duration = pulse_end - pulse_start
        
        distance_value = pulse_duration * 17150
        
        with distance_lock:
            distance.value = round(distance_value, 2)
            
        time.sleep(1)
"""

# Funzione per processare le immagini con OpenCV

def cv2Lines():

    green_color = (0, 255, 0, 20)  # BGR colore verde
    red_color = (0, 0, 255, 20)  # BGR colore verde
    orange_color = (0, 125, 255, 20)  # BGR colore verde
    yellow_color = (0, 255, 255, 20)  # BGR colore giallo

    linee_rosse = [((77, 356), (563, 356)),  # Orizzontale
                   ((0, 480), (77, 356)),  # Basso Sinistra
                   ((640, 480), (563, 356))]  # Basso Destra

    linee_arancio = [((180, 186), (460, 186)),  # Orizzontale
                     ((77, 356), (180, 186)),  # Basso Sinistra
                     ((460, 186), (563, 356))]  # Basso Destra
    linee_verdi = [((230, 106), (410, 106)),
                   ((180, 186), (230, 106)),
                   ((410, 106), (460, 186))]

    while True:
        if len(cv2_queue) > 0:
            time.sleep(0.04)
            frame = get_latest_frame()
            frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)

            # Crea un'immagine trasparente dello stesso size del frame
            overlay = np.zeros_like(frame, dtype=np.uint8)

            # Disegna le linee sull'overlay
            for line in linee_rosse:
                pt1, pt2 = line
                cv2.line(overlay, pt1, pt2, red_color, thickness=2)

            for line in linee_arancio:
                pt1, pt2 = line
                cv2.line(overlay, pt1, pt2, orange_color, thickness=2)

            for line in linee_verdi:
                pt1, pt2 = line
                cv2.line(overlay, pt1, pt2, green_color, thickness=2)

            # Mescola l'overlay con il frame originale utilizzando la trasparenza
            image_with_lines = cv2.addWeighted(frame, 1, overlay, 0.4, 0)

            add_image(image_with_lines)
        else:
            continue

# Funzione per generare i frame per la Web UI
def generate_frames():
    while True:
        time.sleep(0.04)
        if len(img_queue) > 0:
            frame = get_latest_image()  # Prendo l'ultima immagine
            # Effettuo l'encoding dell'immagine
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        else:
            continue

# Homepage
@app.route('/')
def index():
    return render_template('index.html')


# API per ottenere il flusso video
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# API per ottenere la distanza
@app.route('/get_distance', methods=['GET'])
def get_distance():
    global distance, distance_lock

    with distance_lock:
        distance_value = distance.value

    return str(distance_value)


if __name__ == "__main__":
    Thread(target=video_capture, args=(
        frame_queue, darknet_image_queue)).start()
    Thread(target=inference, args=(darknet_image_queue,
           detections_queue, fps_queue)).start()
    Thread(target=drawing, args=(frame_queue,
           detections_queue, fps_queue)).start()
    cv2_thread = threading.Thread(target=cv2Lines).start()
    app.run(port=5000, debug=True)
