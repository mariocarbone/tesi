import paho.mqtt.client as mqtt
import json
import time
import threading

def create_client(client_id, broker_address, port):
    client = mqtt.Client(client_id)
    event = threading.Event()  # Evento per sincronizzare la pubblicazione dopo la sottoscrizione

    def on_connect(client, userdata, flags, rc):
        print(f"<Client {client_id}> Connesso con codice: {rc}")
        client.subscribe("/alert/#", qos=1)  # Sottoscrizione a tutti gli alert con QoS 1
        event.set()

    def on_message(client, userdata, message):
        now = time.time()
        payload = json.loads(message.payload)
        t_creation = payload.get("t_creation")
        time_travel = (now - t_creation) * 1000  # Tempo in millisecondi
        print(f"<Client {client_id}> Ricevuto messaggio. Tempo di trasmissione: {time_travel} ms")

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_address, port)

    def publish_message():
        event.wait()  # Aspetta che la connessione e la sottoscrizione siano completate
        payload = json.dumps({"t_creation": time.time()})
        client.publish("/alert/" + client_id, payload, qos=1)  # Pubblica con QoS 1

    return client, publish_message

def run_client(client, publish_message):
    try:
        publish_message()
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"<Client {client._client_id}> Disconnessione.")

def main():
    broker_address = "192.168.1.6"
    port = 1883
    clients = []

    for i in range(1000):
        client_id = f"client_{i}"
        client, publish_message = create_client(client_id, broker_address, port)
        clients.append(client)

        # Avvio il client e la pubblicazione del messaggio in un thread separato
        thread = threading.Thread(target=run_client, args=(client, publish_message))
        thread.start()

if __name__ == "__main__":
    main()
