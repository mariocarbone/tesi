import RPi.GPIO as GPIO
import time
import netifaces  # pip -r
import subprocess
from pyembedded.raspberry_pi_tools.raspberrypi import PI


class Raspberry(str):
    def __init__(self):
        print("Raspberry Inizializzato")
        self.network_info = {}
        self.wifi_info = {}
        self.system_status = {}
        self.pi = PI()
        GPIO.setwarnings(False)
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        self.trig_pin = 7
        self.echo_pin = 11
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

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

    # Funzione per misurare la distanza
    def measure_distance(self):
        GPIO.output(self.trig_pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, GPIO.LOW)

        while GPIO.input(self.echo_pin) == 0:
            pulse_start = time.time()
        while GPIO.input(self.echo_pin) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start

        distance_value = pulse_duration * 17150

        # print("Distance = ", distance_value)
        return round(distance_value, 2)

        GPIO.cleanup()

    def get_network_info(self):
        # Ottieni tutti gli interfacce di rete
        interfaces = netifaces.interfaces()

        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                # Ottieni l'indirizzo IP IPv4
                ip = addrs[netifaces.AF_INET][0]["addr"]
                # Ottieni il nome dell'interfaccia
                self.network_info[interface] = ip

        return self.network_info

    def get_wifi_network_info(self):
        wifi_interface = "wlan0"

        if wifi_interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(wifi_interface)
            if netifaces.AF_INET in addrs:
                ip = addrs[netifaces.AF_INET][0]["addr"]
                self.wifi_info["IP"] = ip
            self.wifi_info["ESSID"] = self.get_current_ssid()
            # if netifaces.AF_INET in addrs:
            # 	essid = addrs[netifaces.AF_INET][0].get('essid', "N/A")
            # 	self.wifi_info['ESSID'] = essid
        return self.wifi_info

    def get_current_ssid():
        try:
            result = subprocess.check_output(["iwgetid", "-r"], universal_newlines=True)
            return result.strip()
        except subprocess.CalledProcessError:
            return "N/A"
