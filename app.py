from vision import Darknet
import cv2
from collections     import deque
from queue           import Queue
from threading       import Thread
import time
import numpy as np
import random
from mqtt_lib import MQTTConnection

darknet1 = Darknet("v3")
darknet2 = Darknet("v3_tiny")
darknet3 = Darknet("v4_tiny")

mqtt_con = MQTTConnection("localhost",1883,"/alert","/smartcar","001")

frame_queue =  Queue(maxsize=15)
cap = cv2.VideoCapture(0)
ret, frame_video = cap.read()
cap.release()
   
# Funzione per processare le immagini con OpenCV
def cv2Lines(frame_con_box):
    green_color = (0, 255, 0, 20)  # BGR colore verde
    red_color = (0, 0, 255, 20)  # BGR colore verde
    orange_color = (0, 125, 255, 20)  # BGR colore verde
    yellow_color = (0, 255, 255, 20) # BGR colore giallo                         
    linee_rosse = [((77,356),(563,356)), #Orizzontale 
                    ((0,480),(77,356)), #Basso Sinistra
                    ((640,480),(563,356))] #Basso Destra                
    linee_arancio = [((180,186),(460,186)), #Orizzontale 
                    ((77,356),(180,186)),  #Basso Sinistra
                    ((460,186),(563,356))] #Basso Destra
    linee_verdi = [((230,106),(410,106)),
                    ((180,186),(230,106)),
                    ((410,106),(460,186))]    
   
    #frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
    overlay = np.zeros_like(frame_con_box, dtype=np.uint8)
    
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
    
    frame_con_box=draw_text_on_frame(frame_con_box,"100mm",305,120)
    frame_con_box=draw_text_on_frame(frame_con_box,"200mm",305,290)
    frame_con_box=draw_text_on_frame(frame_con_box,"300mm",305,370)

    frame_with_lines = cv2.addWeighted(frame_con_box, 1, overlay, 0.4, 0)
    return frame_with_lines


def draw_text_on_frame(frame,text,offset_sx,offset_dw):
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

def read_frame():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        #print("Leggo un frame")
        ret, frame = cap.read()
        if not ret:
            break
        frame_queue.put(frame)
    cap.release()

def show_video():
    while(True):
        global frame_video
        test=cv2Lines(frame_video)
        cv2.imshow('APP', test)
        if cv2.waitKey(1) == ord('q'):
            break
  
def start():
    global frame_video
    speed=0
    while(True):
        current_time = int(time.time())
        speed = current_time % 60   
        frame=frame_queue.get()

        #stato=arduino.checkstatus()
        #mqtt.sendstatus(stato)

        offset_sx=30
        offset_dw=60
        testo="Km/h ="+str(speed)
        frame=draw_text_on_frame(frame,testo,30,60)
        if(speed<=20):
            frame=draw_text_on_frame(frame,"YOLO V3",30,40)
            darknet1.detection(frame)
            frame_video=darknet1.get_latest_frame()
            test=darknet1.get_predictions()
            mqtt_con.send_alert(test)

        elif(speed>20 and speed<=40):
            frame=draw_text_on_frame(frame,"YOLO V4 TINY",30,40)
            darknet3.detection(frame)
            frame_video=darknet3.get_latest_frame()
            test=darknet3.get_predictions()
            mqtt_con.send_alert(test)

        elif(speed>40):
            frame=draw_text_on_frame(frame,"YOLO V3 TINY",30,40)
            darknet2.detection(frame)
            frame_video=darknet2.get_latest_frame()
            test=darknet2.get_predictions()
            mqtt_con.send_alert(test)



Thread(target=read_frame).start()
Thread(target=show_video).start()
Thread(target=start).start()

     