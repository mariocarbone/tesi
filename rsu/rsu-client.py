import paho.mqtt.client as mqtt
import json
import random
import time
import math
from geopy.distance import geodesic

# Informazioni RSU
rsu_id_vero = "RSU_" + str(random.randint(100, 999))
rsu_id = "RSU_01"

rsu_deatils = {
    "id": rsu_id,
    "connected_clients": 0,
    "ssid": "AP_128311",
    "gps": {"lat": 39.35613, "lon": 16.22815}
}

veicoli_connessi = {}

# Broker MQTT e Topic
broker_address = "localhost"
broker_port = 1883
topic_auto = "/smartcar/#"
topic_rsu = "/rsu/#"
topic_rsu_topub = "/rsu/"
alert_topic = "/alert/"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code "+str(rc))
    client.subscribe(topic_auto)

def on_message(client, userdata, message):
    global veicoli_connessi
    if message.topic.startswith("/smartcar"):
        payload = json.loads(message.payload)
        vehicle_plate = payload["id"] 
        if payload["rsu_id"] == rsu_id:
            veicoli_connessi[vehicle_plate] = payload


client = mqtt.Client(rsu_id_vero)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, broker_port)
client.loop_start()

# Aggiornamento stato
def update_status():
    while True:
        rsu_deatils["connected_clients"]=len(veicoli_connessi)
        rsu_details_json = json.dumps(rsu_deatils)
        client.publish(topic_rsu_topub + rsu_id + "/details", rsu_details_json)
        print("Aggiornati dettagli RSU " +
              rsu_id+": "+str(rsu_deatils))
        time.sleep(5)
        print("invio alert random")
        location = {"lat": 39.35613, "lon": 16.22815}
        alertSend(createAlert("car", location, "Pippo"))
        time.sleep(5)

# Calcoli RSU - Alert Veicoli

max_speed = 40  # Velocità massima del tratto stradale (km/h)
deceleration = 0.8 # Coefficiente di decelerazione del veicolo (stima tra 0.7 - 0.9)

# Dakar =(14.716677 , -17.467686)

def speed_kmh_ms(speed_kmh):
	return speed_kmh*5/18
	
def speed_ms_kmh(speed_ms):
	return speed_ms*18/5

# Calcola lo spazio di frenata necessario utilizzando la formula del moto uniformemente accelerato
def calculate_stopping_distance(initial_speed, target_speed, deceleration): # velocità in m/s

    if target_speed >= initial_speed:
        raise ValueError("La velocità finale deve essere inferiore alla velocità iniziale.")
    
    stopping_distance = ((initial_speed ** 2) - (target_speed ** 2)) / (2 * deceleration)
    return stopping_distance

safety_distance = 5  # Distanza di sicurezza dal pericolo o dall'ostacolo (espressa in metri)
num_zones = 3  # Numero di zone di rallentamento desiderate

def generate_alert_radius(speed, deceleration_coefficient):
	
    braking_distance = (speed ** 2) / (2 * deceleration_coefficient)
    alert_radius = braking_distance / 2
    return math.ceil(alert_radius)

def calculate_communication_delay(previous_delay, current_delay, alpha):

    # Calcola il ritardo di comunicazione utilizzando una media ponderata dei valori precedenti e correnti
    communication_delay = (alpha * previous_delay) + ((1 - alpha) * current_delay)
    return communication_delay

previous_delay = 0.0
current_delay = 10.0
alpha = 0.5

def update_communication_delay():

    communication_delay = calculate_communication_delay(previous_delay, current_delay, alpha)
    # Aggiorna il ritardo precedente con il ritardo appena calcolato
    previous_delay = communication_delay


# persona, veicolo, moto, bici, cane

alert_db = {}

def createAlert(tipo, location, revealedBy):
    alert_id=random.randint(0,1000)
    alert_details = {
    "id": alert_id ,
    "type": tipo,
    "revealedBy": revealedBy,
    "gps": {"lat": location["lat"], "lon": location["lon"]}
    }
    alert_db[alert_id]=alert_details
    return alert_details


def alertSend(alert):
    alert_json = json.dumps(alert)
    client.publish(alert_topic + "/" + str(alert["id"]), alert_json)
    print("Inviato ALERT " + str(alert))
   
    

update_status()
