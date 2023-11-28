import paho.mqtt.client as mqtt
import json
import time
import threading

class MQTTClient:
    def __init__(self, client_id, broker_address, port):
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        #self.client.on_message = self.on_message
        self.client.connect(broker_address, port)
        self.topic = "/alert/" + client_id

    def on_connect(self, client, userdata, flags, rc):
        print(f"<Client {client._client_id.decode()}> Connesso con codice: {rc}")
        client.subscribe("/alert/#", qos=1)
        self.publish_alert()

    def on_message(self, client, userdata, message):
        now = time.time()
        payload = json.loads(message.payload)
        t_creation = payload.get("t_creation")
        time_travel = (now - t_creation) * 1000
        print(f"<Client {client._client_id.decode()}> Ricevuto messaggio. Tempo di trasmissione: {time_travel} ms")

    def publish_alert(self):
        payload = json.dumps({"t_creation": time.time()})
        self.client.publish(self.topic, payload, qos=1)

    def run(self):
        self.client.loop_forever()

def create_and_run_client(client_id, broker_address, port):
    mqtt_client = MQTTClient(client_id, broker_address, port)
    mqtt_client.run()

def main():
    broker_address = "192.168.1.6"
    port = 1883
    threads = []

    for i in range(50):
        client_id = f"client_{i}"
        thread = threading.Thread(target=create_and_run_client, args=(client_id, broker_address, port))
        thread.start()
        threads.append(thread)

    # Aspetta che tutti i thread terminino (opzionale)
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
