#import RPi.GPIO as GPIO
import time
import subprocess
import netifaces
from pyembedded.raspberry_pi_tools.raspberrypi import PI


class Raspberry(str):
	def __init__(self):
		print("Raspberry Inizializzato")
		self.network_info = {}
		self.system_status = {}
		self.system_status['ssid'] = "RSU_PI01" #Da configurare manualmente
		self.pi = PI()

	def get_system_status(self):
		ram_used = int(self.pi.get_ram_info()[1])
		ram_total = int(self.pi.get_ram_info()[0])
		ram_usage = round((ram_used/ram_total)*100,1)
		self.system_status["ram"] = ram_usage
		self.system_status["cpu"] = self.pi.get_cpu_usage()
		self.system_status["temp"] = round(self.pi.get_cpu_temp(),1)
		self.system_status["ip"] = self.get_network_info()
		return self.system_status

	def get_network_info(self):
		bridge_interface = "bridge0"
		if bridge_interface in netifaces.interfaces():
			addrs = netifaces.ifaddresses(bridge_interface)
			if netifaces.AF_INET in addrs and addrs[netifaces.AF_INET]:
				return addrs[netifaces.AF_INET][0]["addr"]
		return None
