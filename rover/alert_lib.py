import time
import threading
from mqtt_lib import MQTTConnection
from control_lib import Vehicle_Control

class Alert:
    
    def __init__(self, vehicle_id, vehicle_control, rpi_instance, mqtt_connection):
        self.vehicle_id = vehicle_id
        self.mqtt_connection = mqtt_connection
        self.vehicle_control = vehicle_control
        self.rpi_instance = rpi_instance
        self.alert_sended = {}
        self.last_predictions = []

    def process_predictions(self, predictions):
        prediction_timestamp = predictions.get('timestamp', time.time())
        if self.should_generate_alert(predictions):
            for key, prediction in predictions.items():
                if key != "timestamp":
                    if not self.is_recent_alert(prediction):
                        alert_thread = threading.Thread(target=self.create_and_send_alert, args=(prediction, prediction_timestamp))
                        alert_thread.start()
                        # Aggiungi la prediction corrente alle ultime 10
                        self.last_predictions.append((prediction, prediction_timestamp))
                        # Mantieni solo le ultime 10 prediction
                        if len(self.last_predictions) > 10:
                            self.last_predictions.pop(0)
    
    def is_recent_alert(self, current_prediction):
        for prev_prediction, _ in self.last_predictions:
            if self.are_predictions_similar(current_prediction, prev_prediction):
                return True
        return False
    
    def are_predictions_similar(self, current_prediction, prev_prediction):
        # Confronta le coordinate e lo score delle prediction
        current_coords = current_prediction.get('coordinates', {})
        prev_coords = prev_prediction.get('coordinates', {})
        score_diff = abs(current_prediction.get('score', 0) - prev_prediction.get('score', 0))
        coords_diff = all(abs(current_coords.get(key, 0) - prev_coords.get(key, 0)) < 50 for key in ['x', 'y', 'w', 'h'])
        return coords_diff and score_diff < 0.1

    def should_generate_alert(self, predictions):
        for key, prediction in predictions.items():
            if key != "timestamp" and prediction["category"] == "person" and prediction["score"] > 0.7:
                return True
        return False

    def create_and_send_alert(self, prediction, prediction_timestamp):
        alert_details = {
            "timestamp": prediction_timestamp,
            "vehicle_id": self.vehicle_id,
            "front_distance": self.vehicle_control.status.get('distance', 0),
            "connected_RSU": self.rpi_instance.system_status.get("ap_connected", 'N/A'),
            "distance_from_rsu": self.rpi_instance.system_status.get("ap_distance", 'N/A'),
            "distance_from_other_aps": self.rpi_instance.system_status.get("other_aps", {}),
            "type": prediction.get('category', 'unknown'),
            "confidence": prediction.get('score', 0),
            "object_in_front": self.vehicle_control.status.get("object_in_front", False),
            "vehicle_stopped": self.vehicle_control.status.get('stopped', False),
            "coordinates": prediction.get('coordinates')
        }
        print(prediction_timestamp, "Alert creato")
        self.alert_sended[str(prediction_timestamp)] = alert_details
        # Mantieni solo gli ultimi 10 alert
        if len(self.alert_sended) > 10:
            oldest_key = sorted(self.alert_sended.keys())[0]
            del self.alert_sended[oldest_key]

        self.mqtt_connection.send_alert(alert_details)

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



