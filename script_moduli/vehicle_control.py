from serial import Serial
from RPi import GPIO

class VehicleControl:
    
    def __init__(self, porta_seriale):
        # Inizializza la connessione seriale con Arduino sulla porta specificata
        self.ser = Serial(porta_seriale, baudrate=9600)
        self.command_buffer = []

    def speed(self, value):
        # Invia il comando di controllo della velocità a Arduino
        command = f"SPEED {value}"
        self.command_buffer.append(command)

    def turn(self, direction):
        # Invia il comando di controllo della direzione a Arduino
        command = f"TURN {direction}"
        self.command_buffer.append(command)

    def brake(self):
        # Invia il comando di frenata a Arduino
        command = "BRAKE"
        self.command_buffer.append(command)

    def get_status(self):
        # Legge lo stato del veicolo da Arduino
        status = self.ser.readline().decode().rstrip()
        return status

    def process_commands(self):
        if self.command_buffer:
            command = self.command_buffer.pop(0)
            self.ser.write(command.encode())

        # Altro codice per la gestione dei comandi in uscita da Arduino e lettura dati dalla GPIO
