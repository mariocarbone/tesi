import paho.mqtt.client as mqtt
import json
import time

class MQTTConnection:

    def __init__(self, broker_address, port, rsu_id, standalone=False):
        self.broker = broker_address
        self.port = port
        self.rsu_id = rsu_id
        self.client = mqtt.Client(rsu_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.standalone = standalone
        self.client.connect(broker_address, port)
        if not standalone:
            self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("<MQTT> Connesso al broker MQTT: <code: " + str(rc) + ">")
        if self.standalone:
            client.subscribe("/alert/#")
        else:
            client.subscribe("/alert/" + self.rsu_id + '/#')

    def on_message(self, client, userdata, message):
        now = time.time()*1000
        payload = json.loads(message.payload)
        start = payload.get("t_creation")*1000
        time_travel = now - start
        print(f"<Ricevuto messaggio> Topic: {message.topic}, {time_travel} ms")

    def start(self):
        if self.standalone:
            try:
                self.client.loop_forever()
            except KeyboardInterrupt:
                print("MQTT Connection terminata.")
        else:
            print("MQTT Connection già avviata in modalità non-standalone.")

# Esempio di utilizzo in modalità standalone
if __name__ == "__main__":
    mqtt_connection = MQTTConnection("192.168.1.6", 1883, "rsu_id", standalone=True)
    mqtt_connection.start()
