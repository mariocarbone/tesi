#import RPi.GPIO as GPIO
import time
import subprocess
import re
import netifaces
from pyembedded.raspberry_pi_tools.raspberrypi import PI


class Raspberry(str):
	def __init__(self):
		print("Raspberry Inizializzato")
		self.network_info = {}
		self.wifi_info = {}
		self.system_status = {}
		self.pi = PI()
		self.other_aps = {}

	def get_system_status(self):
		ram_used = int(self.pi.get_ram_info()[1])
		ram_total = int(self.pi.get_ram_info()[0])
		ram_usage = round((ram_used/ram_total)*100,1)
		
		self.system_status["ram"] = ram_usage
		self.system_status["cpu"] = self.pi.get_cpu_usage()
		self.system_status["temp"] = round(self.pi.get_cpu_temp(),1)
		self.system_status["wifi"] = self.pi.get_wifi_status()
		self.system_status["ip"] = self.pi.get_connected_ip_addr(network="wlan0")
		self.system_status["disk_space"] = self.pi.get_disk_space()
		self.system_status["ap_connected"] = self.system_status["wifi"][0]
		self.system_status["ap_distance"] = self.get_rsu_distance()
		self.get_rsu_distance()
		return self.system_status

	def update_other_aps(self):
		interface = "wlan0"
		rsu_networks = self.scan_wifi_rsu(interface)
		connected_rsu = self.system_status.get("ap_connected")

		if 'other_aps' not in self.system_status:
			self.system_status['other_aps'] = {}

		for ssid, rssi in rsu_networks:
			if ssid != connected_rsu:  # Escludi l'RSU connessa
				distance = self.calculate_distance(int(rssi))
				self.system_status['other_aps'][ssid] = distance

		print(self.system_status['other_aps'])

	def calculate_distance(self, rssi, n=2):
		if rssi is None:
			return None
		A = -30  # Valore RSSI misurato ad un metro
		distance = 10 ** ((A - rssi) / (10 * n))
		return round(distance,2)
	
	def get_rsu_distance(self):
		rssi_str = self.system_status["wifi"][1]
		rssi = int(rssi_str.split(' ')[0]) # RSSI in intero
		return self.calculate_distance(rssi)
	
	def get_rsu_distance_with_update(self):
		# Aggiorno lo stato del wifi
		self.system_status["wifi"] = self.pi.get_wifi_status()
		rssi_str = self.system_status["wifi"][1]
		rssi = int(rssi_str.split(' ')[0])  # RSSI a intero
		return self.calculate_distance(rssi)
	
	def get_other_rsu_distance(self):
		return self.system_status['other_aps']

	def scan_wifi_rsu(self, interface):
		try:
			# Esegui il comando senza shlex.split
			scan_output = subprocess.check_output(['sudo', 'iwlist', interface, 'scan'], text=True)

			# Estrai tutti gli SSID e i livelli del segnale
			networks = re.findall(r"ESSID:\"(.+?)\".*?\n.*?Signal level=(.+?) dBm", scan_output, re.DOTALL)
			
			# Filtra solo le reti che iniziano con "RSU"
			rsu_networks = [(ssid, signal) for ssid, signal in networks if ssid.startswith("RSU")]

			return rsu_networks
		except subprocess.CalledProcessError as e:
			print(f"Errore durante la scansione delle reti Wi-Fi: {e}\nOutput: {e.output}")
			return {}

	def get_wifi_network_info(self):
		wifi_interface = "wlan0"

		if wifi_interface in netifaces.interfaces():
			addrs = netifaces.ifaddresses(wifi_interface)
			if netifaces.AF_INET in addrs:
				ip = addrs[netifaces.AF_INET][0]["addr"]
				self.wifi_info["IP"] = ip
			self.wifi_info["ESSID"] = self.get_current_ssid()

		return self.wifi_info

	def get_current_ssid():
		try:
			result = subprocess.check_output(["iwgetid", "-r"], universal_newlines=True)
			return result.strip()
		except subprocess.CalledProcessError:
			return "N/A"

