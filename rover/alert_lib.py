import time
import threading
from mqtt_lib import MQTTConnection
from control_lib import Vehicle_Control

class Alert:
    
    def __init__(self, vehicle_id, vehicle_control, rpi_instance, mqtt_connection):
        self.vehicle_id = vehicle_id
        self.mqtt_connection = mqtt_connection
        self.mqtt_connection.on_alert_callback = self.handle_received_alert
        self.vehicle_control = vehicle_control
        self.vehicle_control.object_in_front_callback = self.on_object_in_front_detected
        self.rpi_instance = rpi_instance
        self.alert_sended = {}
        self.alert_received = {}
        self.last_predictions = []

    def process_predictions(self, predictions):
        prediction_timestamp = predictions.get('timestamp', time.time())
        for key, prediction in predictions.items():
            if key != "timestamp" and isinstance(prediction, dict):
                if self.should_generate_alert(prediction):
                    if not self.is_recent_alert(prediction, prediction_timestamp):
                        alert_thread = threading.Thread(target=self.create_and_send_alert, args=(prediction, prediction_timestamp))
                        alert_thread.start()

    def is_recent_alert(self, current_predictions, current_timestamp):
        for prev_predictions, prev_timestamp in self.last_predictions:
            if self.are_predictions_similar(current_predictions, prev_predictions):
                return True
        self.last_predictions.append((current_predictions, current_timestamp))

        # Mantieni solo le ultime 10 prediction
        if len(self.last_predictions) > 10:
            self.last_predictions.pop(0)
        return False

    def are_predictions_similar(self, current_prediction, prev_prediction):

        current_coords = current_prediction.get('coordinates', {})
        prev_coords = prev_prediction.get('coordinates', {})
        score_diff = abs(current_prediction.get('score', 0) - prev_prediction.get('score', 0))
        coords_diff = all(abs(current_coords.get(key, 0) - prev_coords.get(key, 0)) < 50 for key in ['x', 'y', 'w', 'h'])
        
        # Restituisci True se le previsioni sono simili, altrimenti False
        return coords_diff and score_diff < 0.1

    def should_generate_alert(self, prediction):
        if prediction.get("category") == "person" and prediction.get("score") > 0.7:
                return True
        return False

    def create_and_send_alert(self, predictions, prediction_timestamp):
        alert_details = {
            "timestamp": prediction_timestamp,
            "t_creation" : time.time(),
            "creator_id": self.vehicle_id,
            "front_distance": self.vehicle_control.status.get('distance', 0),
            "connected_RSU": self.rpi_instance.system_status.get("ap_connected", 'N/A'),
            "distance_from_rsu": self.rpi_instance.system_status.get("ap_distance", 'N/A'),
            "distance_from_other_aps": self.rpi_instance.system_status.get("other_aps", {}),
            "type": predictions.get('category', 'unknown'),
            "confidence": predictions.get('score', 0),
            "object_in_front": self.vehicle_control.status.get("object_in_front", False),
            "vehicle_stopped": self.vehicle_control.status.get('stopped', False),
            "coordinates": predictions.get('coordinates')
        }
        print(f"<Alert creato> {alert_details['type']}")
        self.alert_sended[str(prediction_timestamp)] = alert_details
        # Mantieni solo gli ultimi 10 alert
        if len(self.alert_sended) > 10:
            oldest_key = sorted(self.alert_sended.keys())[0]
            del self.alert_sended[oldest_key]
        #print(alert_details)
        self.mqtt_connection.send_alert(alert_details)

    def on_object_in_front_detected(self):
        print("Rilevato oggetto di fronte al veicolo a meno di 15cm, genero un alert")
        self.create_undefined_alert()

    #Alert if vehicle stopped
    def create_vehicle_stopped_alert(self):

        alert_details = {
            "timestamp": time.time(),
            "t_creation" : time.time(),
            "creator_id": self.vehicle_id,
            "front_distance": self.vehicle_control.status.get('distance', 0),
            "connected_RSU": self.rpi_instance.system_status.get("ap_connected", 'N/A'),
            "distance_from_rsu": self.rpi_instance.system_status.get("ap_distance", 'N/A'),
            "distance_from_other_aps": self.rpi_instance.system_status.get("other_aps", {}),
            "type": "vehicle_stopped",
            "object_in_front": self.vehicle_control.status.get("object_in_front", False),
            "vehicle_stopped": self.vehicle_control.status.get('stopped', False),
        }
        self.send_alert(alert_details)
    
    #Alert if object undefined
    def create_undefined_alert(self):
        alert_details = {
            "timestamp": time.time(),
            "t_creation" : time.time(),
            "creator_id": self.vehicle_id,
            "front_distance": self.vehicle_control.status.get('distance', 0),
            "connected_RSU": self.rpi_instance.system_status.get("ap_connected", 'N/A'),
            "distance_from_rsu": self.rpi_instance.system_status.get("ap_distance", 'N/A'),
            "distance_from_other_aps": self.rpi_instance.system_status.get("other_aps", {}),
            "type": "undefined",
            "object_in_front": self.vehicle_control.status.get("object_in_front", False),
            "vehicle_stopped": self.vehicle_control.status.get('stopped', False),
        }
        self.send_alert(alert_details)

    def send_alert(self, alert_details):
        # Invia l'alert tramite MQTT e registra l'alert inviato
        print(f"<Alert creato> {alert_details['type']}")
        self.alert_sended[str(alert_details['timestamp'])] = alert_details
        
        self.mqtt_connection.send_alert(alert_details)
        # Pulizia per mantenere solo gli ultimi 10 alert
        if len(self.alert_sended) > 10:
            oldest_key = sorted(self.alert_sended.keys())[0]
            del self.alert_sended[oldest_key]


    def handle_received_alert(self,alert):
        tstamp = alert.get('timestamp', time.time())
        
        self.alert_received[str(tstamp)] = alert
        # Mantieni solo gli ultimi 10 alert
        if len(self.alert_received) > 10:
            oldest_key = sorted(self.alert_received.keys())[0]
            del self.alert_received[oldest_key]
            
        alert_handle = threading.Thread(target=self.vehicle_control.alert_to_controls, args=(alert,))
        alert_handle.start()


    #CODICE INUTILIZZATO

    def check_zona(self, punto):
        for zona in self.zone :

            # Estrai le coordinate dei quattro vertici
            x1, y1 = zona[0]
            x2, y2 = zona[1]
            x3, y3 = zona[2]
            x4, y4 = zona[3]
            
            # Calcola i coefficienti delle quattro rette che formano il trapezio
            a1 = (y2 - y1) / (x2 - x1)
            b1 = y1 - a1 * x1    
            a2 = (y3 - y2) / (x3 - x2)
            b2 = y2 - a2 * x2
            a3 = (y4 - y3) / (x4 - x3)
            b3 = y3 - a3 * x3
            a4 = (y1 - y4) / (x1 - x4)
            b4 = y4 - a4 * x4

            # Verifica se il punto appartiene al trapezio
            if (punto[1] <= a1 * punto[0] + b1 and
                punto[1] <= a2 * punto[0] + b2 and
                punto[1] >= a3 * punto[0] + b3 and
                punto[1] >= a4 * punto[0] + b4):
                return zona
        return None    
        
    def check_center(self, prediction):
        x=prediction["x"]
        w=prediction["w"]
        punto_x=(x+w)/2
        y=prediction["y"]
        h=prediction["h"]
        punto_y=(y+h)/2
        punto=(punto_x, punto_y)
        return punto
    
    def check_predictions_old(self,predictions):
        for prediction in predictions:
            center=self.check_center(prediction)
            zona=self.check_zona(center)
            if (zona != None):
                print(zona[0])



