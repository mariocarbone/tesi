import serial
import json
import time

class Arduino:

	def __init__(self, serial_port, baud_rate, timeout, write_timeout):
		self.ser = serial.Serial(serial_port, baud_rate)
		self.ser.timeout=timeout
		self.ser.write_timeout=write_timeout
		self.serial_port = serial_port
		self.baud_rate = baud_rate
		self.timeout = timeout
		self.write_timeout = write_timeout
		self.str_left="LEFT"
		self.str_right="RIGHT"
		self.str_center="CENTER"


	def steer(self, side, value):
		if(side == self.str_left):
			command = self.str_left+str(value)
		elif(side == self.str_right):
			command = self.str_right+str(value)
		else:
			print("Side not recognized")
		self.send_command(command)

	def turn_left(self):
		command = self.str_left+"5"
		self.send_command(command)

	def turn_right(self):
		command = self.str_right+"5"
		self.send_command(command)

	def speed(self, speed):
		command = "SPEED"+str(speed)
		self.send_command(command)

	def backward(self, speed):
		command = "BACK"+str(speed)
		self.send_command(command)

	def stop(self):
		command = "STOP"
		self.send_command(command)

	def brake(self):
		command = "BRAKE"
		self.send_command(command)

	def get_status(self):
		command = "STATUS"
		self.send_command(command)
		response = self.ser.readline().decode('ascii')

		try:
			if response.strip():  # Verifica se la stringa non è vuota o contiene solo spazi
				data = json.loads(response)
			else:
				data = {}  # Restituisci un dizionario vuoto per una stringa vuota
			return data
		except json.JSONDecodeError as e:
			print(f"Errore nella decodifica JSON: {e}")
			data = {}  # Puoi restituire un dizionario vuoto o effettuare altre azioni correttive
			return data

	def send_command(self, command):
		newline = "\n"
		complete_command = command+newline
		try:
			self.ser.write(complete_command.encode())
			#print("COMANDO INVIATO",complete_command)
		except serial.SerialTimeoutException:
			print("Timeout nell'invio del comando", command)
			self.reconnect()
	
	def process_alert(self, alert):
		command = "ALERT"
		

	def reconnect(self):	
		print("Avvio una nuova connessione")
		self.ser = serial.Serial(self.serial_port, self.baud_rate)
		self.ser.timeout=self.timeout
		self.ser.write_timeout=self.write_timeout
	

	
