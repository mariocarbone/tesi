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

	def steer(self, angle):
		command = "TRN"+str(angle)
		self.send_command(command)

	def turn_left(self):
		command = "TRN45"
		self.send_command(command)

	def turn_right(self):
		command = "TRN-45"
		self.send_command(command)

	def speed(self, speed):
		command = "SPD"+str(speed)
		self.send_command(command)

	def backward(self, speed):
		command = "BAK"+str(speed)
		self.send_command(command)

	def stop(self):
		command = "STP"
		self.send_command(command)

	def brake(self):
		command = "BRK"+speed
		self.send_command(command)

	def get_status(self):
		command = "STA"
		self.send_command(command)
		response = self.ser.readline().decode('ascii')
		print("ARDUINO", response)

		try:
			data = json.loads(response)
			return data
		except json.JSONDecodeError as e:
			print(f"Errore nella decodifica JSON: {e}")
			return {}  # o restituisci un valore predefinito o esegui un'altra azione correttiva

	def send_command(self, command):
		newline = "\n"
		complete_command = command+newline
		try:
			self.ser.write(complete_command.encode())
		#print("COMANDO INVIATO",complete_command)
		except serial.SerialTimeoutException:
			print("Timeout nell'invio del comando", command)
			self.reconnect()
	
	def reconnect(self):
		print("Avvio una nuova connessione")
		self.ser = serial.Serial(self.serial_port, self.baud_rate)
		self.ser.timeout=self.timeout
		self.ser.write_timeout=self.write_timeout
	
	def main(self):
		print("<arduino> Connessione avviata")
		time.sleep(1.5)
		while True:
			#print("<arduino> Seriale Aperta:", test.arduino.isOpen())
			comando = "STATUS"
			newline = "\n"
			comando_completo = comando+newline
			self.ser.write(comando_completo.encode())
			#print("<arduino> Comando inviato:",comando)
			response = self.ser.readline().decode('ascii')
			print("<arduino> Risposta ricevuta:",response)
			time.sleep(1)
			acc= "SPD50\n"
			#print("<arduino> Comando inviato: SPD50")
			self.ser.write(acc.encode())
			time.sleep(1)


	
