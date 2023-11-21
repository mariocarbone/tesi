#import RPi.GPIO as GPIO
import time
import subprocess
from pyembedded.raspberry_pi_tools.raspberrypi import PI


class Raspberry(str):
	def __init__(self):
		print("Raspberry Inizializzato")
		self.network_info = {}
		self.wifi_info = {}
		self.system_status = {}
		self.pi = PI()
		#self.distance = 0
		#GPIO.setwarnings(False)
		#GPIO.cleanup()
		#GPIO.setmode(GPIO.BOARD)
		#self.trig_pin = 7
		#self.echo_pin = 11
		#GPIO.setup(self.trig_pin, GPIO.OUT)
		#GPIO.setup(self.echo_pin, GPIO.IN)

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
		return self.system_status
	
	def calculate_distance(self, rssi, n=2):
		if rssi is None:
			return None
		A = -30  # Valore RSSI tipico a 1 metro
		distance = 10 ** ((A - rssi) / (10 * n))
		return distance
	
	def get_rsu_distance(self):
		#Aggiorno lo stato del wifi
		self.system_status["wifi"] = self.pi.get_wifi_status()	
		#Calcolo una stima dlla distanza basandomi sugli rssi
		print(self.system_status)
		self.system_status["ap_distance"] = self.calculate_distance(self.system_status["wifi"]["rssi"])

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

