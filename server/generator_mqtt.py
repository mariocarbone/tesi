import paho.mqtt.client as mqtt
import json
import time
import threading

def create_client(client_id, broker_address, port):
    client = mqtt.Client(client_id)

    def on_connect(client, userdata, flags, rc):
        print(f"<Client {client_id}> Connesso con codice: {rc}")
        payload = json.dumps({"t_creation": time.time()})
        client.publish("/alert/" + client_id, payload)
    
    client.on_connect = on_connect
    client.connect(broker_address, port)
    return client

def run_client(client):
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"<Client {client._client_id}> Disconnessione.")

def main():
    broker_address = "192.168.1.6"  # Indirizzo del broker
    port = 1883  # Porta del broker
    clients = []

    for i in range(1000):
        client_id = f"client_{i}"
        client = create_client(client_id, broker_address, port)
        clients.append(client)

        # Avvio il client in un thread separato
        thread = threading.Thread(target=run_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    main()