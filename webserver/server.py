import paho.mqtt.client as mqtt
import json
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import time

#Broker MQTT dati
broker_address = "localhost"
topic_auto = "/smartcar/#"
topic_rsu = "/rsu/#"

veicoli = {}
rsu_details = {}

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code "+str(rc))
    client.subscribe(topic_auto)
    client.subscribe(topic_rsu)

def on_message(client, userdata, message):
    global veicoli, rsu_details

    if message.topic.startswith("/rsu"):
        print("Messaggio ricevuto su RSU:" + "TIMESTAMP" + str(time.time()))#message.payload.decode())
        payload = json.loads(message.payload)
        rsu_id = payload["id"]
        rsu_details[rsu_id] = payload
    elif message.topic.startswith("/smartcar"):
        print("Messaggio ricevuto su topic auto:" + "TIMESTAMP" +str(time.time())) #message.payload.decode())
        payload = json.loads(message.payload)
        vehicle_plate = payload["id"]
        veicoli[vehicle_plate] = payload
    else:
        # Gestisco altri topic non previsti
        print("Messaggio ricevuto su un topic non gestito:", message.topic)

# Client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address)
client.loop_start()

# APP FLASK
app = Flask(__name__)
CORS(app)

@app.route("/")
def view_map():
    return render_template("index.html", veicoli=veicoli)

@app.route("/veicoli")
def vehicle_list():
    return jsonify(veicoli)

@app.route("/rsu-details")
def rsu_info():
    return jsonify(rsu_details)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
    
