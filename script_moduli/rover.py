from vehicle_control import VehicleControl
from alert_manager import AlertManager
from darknet_video import Darknet
from mqtt_manager import MQTTConnection
import time
import threading

# Definisci la classe DataHandler per gestire i valori
class DataHandler:
    def __init__(self):
        self.distance = 0
        self.position = None
        self.coordinates = None
        self.video_stream = None

    def update_values(self, distance, position, coordinates, video_stream):
        self.distance = distance
        self.position = position
        self.coordinates = coordinates
        self.video_stream = video_stream

    def get_values(self):
        return {
            'distance': self.distance,
            'position': self.position,
            'coordinates': self.coordinates,
            'video_stream': self.video_stream
        }

# Crea un'istanza di DataHandler
data_handler = DataHandler()

# Definisci una funzione per l'aggiornamento periodico dei valori
def update_values_periodically():
    while True:
        # Simula l'ottenimento dei valori da vari moduli
        distance = 10  # Ottieni la distanza
        position = 'Nord'  # Ottieni la posizione
        coordinates = (45.123456, 9.987654)  # Ottieni le coordinate GPS
        video_stream = 'http://example.com/stream'  # Ottieni il flusso video

        # Aggiorna i valori nel DataHandler
        data_handler.update_values(distance, position, coordinates, video_stream)

        # Aggiorna i valori periodicamente
        time.sleep(1)  # Esegui l'aggiornamento ogni secondo

# Crea un thread per l'aggiornamento periodico dei valori
update_thread = threading.Thread(target=update_values_periodically)
update_thread.start()

def main():

    # Inizializza i vari oggetti e le connessioni
    vehicle_control = VehicleControl(porta_seriale='/dev/ttyACM0')
    alert_manager = AlertManager()
    darknet = Darknet()
    mqtt_connection = MQTTConnection(broker_address='mqtt://localhost')

    # Esegui il loop principale
    while True:
        # Processa comandi da VehicleControl
        vehicle_control.process_commands()

        # Ricevi e processa gli alert
        alert_manager.receive_alerts()

        # Esegui l'object detection utilizzando Darknet
        darknet.process_video()

        # Gestisci i messaggi MQTT
        mqtt_connection.handle_message(topic, message)

        # Invia lo stato del veicolo tramite MQTT
        mqtt_connection.send_vehicle_status()


def update_values_periodically():
    while True:

        # Richiama la funzione di callback registrata nel modulo WEB_UI
        if web_ui_callback:
            web_ui_callback(valore1, valore2)

        # Aggiorna i valori periodicamente
        time.sleep(1)  # Esegui l'aggiornamento ogni secondo

if __name__ == "__main__":
    main()
