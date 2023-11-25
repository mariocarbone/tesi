import time
from mqtt_lib import MQTTConnection
from control_lib import Vehicle_Control
class Alert:
    
    def __init__(self, vehicle_id, vehicle_control, rpi_instance, mqtt_connection):#, zone):
        self.vehicle_id = vehicle_id
        #self.zone = zone
        self.mqtt_connection = mqtt_connection
        self.vehicle_control = vehicle_control
        self.rpi_istance = rpi_instance

    def process_predictions(self, predictions):
        if self.should_generate_alert(predictions):
            detailed_alert = self.create_detailed_alert(predictions)
            self.mqtt_connection.send_alert(detailed_alert)

    def should_generate_alert(self, predictions):
        for prediction in predictions:
            if prediction["category"] == "person" and prediction["score"] > 0.5:
                return True
        return False

    def create_alert(self, prediction):
        alert_details = {
            "timestamp": int(time.time()),
            "vehicle_id": self.vehicle_id,
            "front_distance" : self.vehicle_control.status['distance'],
            "connected_RSU": self.rpi_istance.system_status["wifi"][0],
            "distance_from_rsu": self.rpi_istance.system_status["ap_distance"],
            "distance_from_other_aps" : self.rpi_istance.other_aps,
            "type" : prediction['category'],
            "confindence" : prediction['score'],
            "object_in_front" : self.vehicle_control.status["object_in_front"],      
            "vehicle_stopped": self.vehicle_control.status['stopped'],
            #"vehicle_stopped": self.vehicle_control.status.get("stopped", True)
        }
        return alert_details

    def send_alert(self, alert):
        self.mqtt_connection.send_alert(alert)

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
    
    def check_predictions(self,predictions):
        for prediction in predictions:
            center=self.check_center(prediction)
            zona=self.check_zona(center)
            if (zona != None):
                print(zona[0])



