import paho.mqtt.client as mqtt
import json
import time

class MQTTConnection:

	def __init__(self, broker_address, port, topic_alert, topic_auto, vehicle_id):
		self.broker = broker_address
		self.port = port
		self.topic_alert = topic_alert
		self.topic_auto = topic_auto
		self.vehicle_id = vehicle_id
		self.client = mqtt.Client(vehicle_id)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.connect(broker_address, port)
		self.client.loop_start()

	def on_connect(self, client, userdata, flags, rc):
		print("<MQTT> Connesso al broker MQTT: <code: " + str(rc) + ">")
		client.subscribe(self.topic_alert + '/+')

	def on_message(self, client, userdata, message):
		if message.topic.startswith("/alert"):
			payload = json.loads(message.payload)
			if payload["creator_id"] == self.vehicle_id:
				pass 
			else:
				creator = payload["creator_id"]
				t_arrival = time.time()*1000 
				t_trasm = payload["t_creation"]*1000
				t_total_ms = round(t_arrival - t_trasm)
				print("<Ricevuto Alert> da", creator, " - Tempo impiegato:", t_total_ms , " ms")
				payload["t_travel"]= t_total_ms
				if self.on_alert_callback:
					self.on_alert_callback(payload)
				#self.manage_alert(payload)
			# alert_id = payload["id"]
			# alert[alert_id] = payload

	def send_vehicle_status(self,vehicle_info):
		vehicle_info_json = json.dumps(vehicle_info)
		self.client.publish(self.topic_auto + "/info", vehicle_info_json)

	def send_alert(self, alert):
		alert_json = json.dumps(alert)
		rsu_id = alert.get("connected_RSU", "RSU")
		if rsu_id == "N/A":
			full_topic = f"{self.topic_alert}"
		else:
			full_topic = f"{self.topic_alert}/{rsu_id}"

		self.client.publish(full_topic, alert_json)

	def manage_alert(self, payload):
		print("")
		#print("Gestione dell'alert:", payload)
		




