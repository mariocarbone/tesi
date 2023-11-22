import paho.mqtt.client as mqtt
import json
import random
import time
from geopy.distance import geodesic


# Informazioni del veicolo


vehicle_id = "AB" + str(random.randint(100, 999)) + "CD"
vehicle_info = {
    "id": vehicle_id,
    "acceleration": 0,
    "braking": 0,
    "speed": 0,
    "gps": {"lat": 39.35576, "lon": 16.22927},
    "distance": 0,
    "rsu_id": "RSU_01"
}
alert = {}

# Broker MQTT e Topic
broker_address = "192.168.1.6"
broker_port = 1883
topic = "/smartcar/" + vehicle_id
alert_topic = "/alert/#"


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code "+str(rc))
    client.subscribe(alert_topic)

def on_message(client, userdata, message):
    global veicoli_connessi
    if message.topic.startswith("/alert"):
        print("RICEVUTO ALERT")
        payload = json.loads(message.payload)
        gestisciAlert(payload)

        #alert_id = payload["id"]
        #alert[alert_id] = payload


client = mqtt.Client(vehicle_id)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, broker_port)
client.loop_start()

# Aggiornamento stato


def update_status():
    while True:
        random_status()
        vehicle_info_json = json.dumps(vehicle_info)
        client.publish(topic + "/info", vehicle_info_json)
        print("Aggiornato stato del veicolo " +
              vehicle_id+": "+str(vehicle_info))
        time.sleep(5)


def random_status():
        vehicle_info["acceleration"] = random.uniform(0, 1)
        vehicle_info["braking"] = random.uniform(0, 1)
        vehicle_info["speed"] = random.uniform(0, 60)
#        39.35547, 16.22687
        vehicle_info["gps"]["lat"] = random.uniform(39.354, 39.358)
        vehicle_info["gps"]["lon"] = random.uniform(16.228, 16.23)
        vehicle_info["distance"] = random.uniform(0, 100)
        # vehicle_info["rsu_id"] = "KM_01"


def gestisciAlert(alert):

    print("GESTISCO ALERT")
    tipo = alert["type"]
    if tipo == "person":
        print("Persona")
    elif tipo == "motorbike":
        print("Moto")
    elif tipo == "car":
        print("Auto")
    elif tipo == "dog":
        print("Cane")
    else:
        print("NON SO CHE CAZZO E`")

    location = (alert["gps"]["lat"], alert["gps"]["lon"])
    my_location = (vehicle_info["gps"]["lat"], vehicle_info["gps"]["lon"])
    distance = geodesic(location, my_location).meters
    print("Alert location: "+ str(location))
    print("My location: "+ str(my_location))
    print("Distanza: " + str(distance)+ "m")



update_status()
