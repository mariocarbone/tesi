import paho.mqtt.client as mqtt
import json
import time
import random
import threading

def publish_message(client):
    while True:
        payload = json.dumps({"t_creation": time.time()})
        client.publish("/alert/message", payload)
        time.sleep(random.uniform(0.5, 5))  # Intervallo random tra 0.5 e 5 secondi

def create_client(broker_address, port):
    client = mqtt.Client()
    client.connect(broker_address, port)
    return client

def main():
    broker_address = "192.168.1.6"
    port = 1883
    clients = [create_client(broker_address, port) for _ in range(50)]

    threads = [threading.Thread(target=publish_message, args=(client,)) for client in clients]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
