import paho.mqtt.client as mqtt
import json
import time
import threading

class MQTTClient:
    def __init__(self, client_id, broker_address, port, publish_interval=5):
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.connect(broker_address, port)
        self.topic = "/alert/" + client_id
        self.publish_interval = publish_interval

    def on_connect(self, client, userdata, flags, rc):
        print(f"<Client {client._client_id.decode()}> Connesso con codice: {rc}")
        client.subscribe("/alert/#", qos=1)
        self.publish_repeatedly()

    def publish_repeatedly(self):
        while True:
            payload = json.dumps({"t_creation": time.time()})
            self.client.publish(self.topic, payload, qos=0)
            time.sleep(self.publish_interval)

    def run(self):
        self.client.loop_start()

def create_and_run_client(client_id, broker_address, port, publish_interval):
    mqtt_client = MQTTClient(client_id, broker_address, port, publish_interval)
    mqtt_client.run()

def main():
    broker_address = "192.168.1.6"
    port = 1883
    publish_interval = 2  # Intervallo in secondi tra le pubblicazioni
    clients = []

    for i in range(50):
        client_id = f"client_{i}"
        thread = threading.Thread(target=create_and_run_client, args=(client_id, broker_address, port, publish_interval))
        thread.start()
        clients.append(thread)

    # Aspetta che tutti i client terminino (opzionale)
    for client in clients:
        client.join()

if __name__ == "__main__":
    main()
