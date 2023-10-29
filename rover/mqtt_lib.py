import paho.mqtt.client as mqtt
import json

class MQTTConnection:

    def handle_message(self, topic, message):
        # Processa il messaggio ricevuto da MQTT e prende decisioni in base al contenuto
        print("Sto processando il messaggio")

    def send_vehicle_status(self,vehicle_info):
        vehicle_info_json = json.dumps(vehicle_info)
        self.client.publish(self.topic_auto + "/info", vehicle_info_json)
        # Invia continuamente lo stato del veicolo su un topic MQTT specificato

    def send_alert(self, alert):
        alert_json = json.dumps(alert)
        self.client.publish(self.topic_alert + "/" + str(alert["timestamp"]) , alert_json)
        # Invia continuamente lo stato del veicolo su un topic MQTT specificato

    def on_connect(self, client, userdata, flags, rc):
        print("<stato> Connesso al broker MQTT: <code: " + str(rc) + ">")
        client.subscribe(self.topic_alert)

    def on_message(self, client, userdata, message):
        if message.topic.startswith("/alert"):
            print("<alert> Ricevuto Alert")
            payload = json.loads(message.payload)
            self.gestisciAlert(payload)
            # alert_id = payload["id"]
            # alert[alert_id] = payload

    def gestisciAlert(self, payload):
        # Implementa la logica per gestire l'alert ricevuto
        print("Gestione dell'alert:", payload)

    def __init__(self, broker_address, port, topic_alert, topic_auto, vehicle_id):
        self.broker = broker_address
        self.port = port
        self.topic_alert = topic_alert
        self.topic_auto = topic_auto
        self.vehicle_id = vehicle_id
        self.client = mqtt.Client(vehicle_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker_address, port)
        self.client.loop_start()

