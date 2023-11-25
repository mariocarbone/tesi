import time
import threading
from mqtt_lib import MQTTConnection
class Alert:

	def __init__(self, rsu_id, mqtt_connection):
		self.rsu_id = rsu_id
		self.mqtt_connection = mqtt_connection
		self.alert_sended = {}
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
			"creator_id": self.rsu_id,
			"type": predictions.get('category', 'unknown'),
			"confidence": predictions.get('score', 0),
			"coordinates": predictions.get('coordinates')
		}
		print(prediction_timestamp, "<Alert creato>")
		self.alert_sended[str(prediction_timestamp)] = alert_details
		# Mantieni solo gli ultimi 10 alert
		if len(self.alert_sended) > 10:
			oldest_key = sorted(self.alert_sended.keys())[0]
			del self.alert_sended[oldest_key]
		#print(alert_details)
		self.mqtt_connection.send_alert(alert_details)


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

