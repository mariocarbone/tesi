
import cv2
import subprocess
import os
import darknet_video
from threading import Thread
import time

ld_library_path = os.environ.get('LD_LIBRARY_PATH', '')
ld_library_path += ':/usr/local/cuda-12.0/targets/x86_64-linux/lib'
ld_library_path += ':/usr/local/lib'
ld_library_path += ':/usr/local/cuda/lib64'
os.environ['LD_LIBRARY_PATH'] = ld_library_path
INPUT_VIDEO = "/home/fabio/src/darknet/data/crossing_480p.mp4"
OUTPUT_VIDEO = "output_video.mp4"
TXT_OUTPUT="output.txt"
TRESH=.50

def label_objects_in_video():
    Thread(target=darknet_video.yolo()).start()
    while True:
        print(darknet_video.get_json())
        time.sleep(0.2)
        
        
def play_output_video():
   
    cap = cv2.VideoCapture(OUTPUT_VIDEO)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
 
        cv2.imshow("Output Video", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


label_objects_in_video()
#play_output_video()
