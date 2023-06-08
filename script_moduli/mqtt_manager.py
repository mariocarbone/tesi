import paho.mqtt.client as mqtt

class MQTTConnection:
    def __init__(self, broker_address):
        client = mqtt.Client(vehicle_id)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker_address, broker_port)
        client.loop_start()
    
    def handle_message(self, topic, message):
        # Processa il messaggio ricevuto da MQTT e prende decisioni in base al contenuto
        print("Sto processando il messaggio")

    def send_vehicle_status(self):
        client.publish(topic + "/info", vehicle_info_json)
        # Invia continuamente lo stato del veicolo su un topic MQTT specificato
