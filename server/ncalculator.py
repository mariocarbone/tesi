import paho.mqtt.client as mqtt
import json
import time
import threading

class SubscriberClient:
    def __init__(self, broker_address, port):
        self.client = mqtt.Client("subscriber")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker_address, port)
        self.times = []

    def on_connect(self, client, userdata, flags, rc):
        print(f"<Subscriber> Connesso con codice: {rc}")
        client.subscribe("/alert/#", qos=1)

    def on_message(self, client, userdata, message):
        now = time.time()
        payload = json.loads(message.payload)
        t_creation = payload.get("t_creation")
        time_travel = now - t_creation
        self.times.append(time_travel)

    def calculate_average_time(self):
        if self.times:
            return sum(self.times) / len(self.times)
        return 0

    def run(self):
        self.client.loop_start()
        while True:
            time.sleep(5)  # Intervallo per calcolare la media
            average_time = self.calculate_average_time()
            print(f"Tempo medio di trasmissione: {average_time * 1000} ms")

def main():
    broker_address = "192.168.1.6"
    port = 1883
    subscriber = SubscriberClient(broker_address, port)
    subscriber.run()

if __name__ == "__main__":
    main()
