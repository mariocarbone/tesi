import pygame
import time
from arduino_lib import Arduino

# Inizializza la libreria Pygame
pygame.init()

# Configura la finestra di visualizzazione
display_width = 300
display_height = 150
game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Guida dell'Auto")

# Crea un'istanza del controller dell'auto
arduino = Arduino("/dev/ttyACM0", 9600, 1, 1)


# Variabili per la gestione della velocità
acceleration_step = 15 # Incremento/decremento della velocità ad ogni click
degree_step = 10 
max_speed = 249  # Velocità massima dell'auto
max_degree = 100
min_degree = 0

# Ciclo principale del gioco
def game_loop():
    game_exit = False
    speed = 0
    steer_angle = 50
    reverse = False

    while not game_exit:
        # Gestione degli eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit = True

            # Gestione dei tasti premuti
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Tasto "Su" per accelerare
                    if speed < max_speed:
                        speed += acceleration_step
                    print("ACCELERATION",speed)
                    #steer_angle=50
                    if not reverse:
                        arduino.speed(speed)
                    else:
                        arduino.backward(speed)
                elif event.key == pygame.K_r:  # Tasto "R" per accelerare
                    if reverse:
                        reverse = False
                        print("REVERSE FALSE")
                        speed=0
                        arduino.stop()
                    else:
                        reverse = True
                        print("REVERSE TRUE")
                        speed=0
                        arduino.stop()
                elif event.key == pygame.K_DOWN:  # Tasto "Giù" per frenare
                    if speed > 0:
                        speed -= acceleration_step
                    print("DECELERATION", speed)
                    #steer_angle=50
                    if not reverse:
                        arduino.speed(speed)
                    else:
                        arduino.backward(speed)
                elif event.key == pygame.K_LEFT:  # Tasto "Sinistra" per girare a sinistra
                    if steer_angle > min_degree:
                        steer_angle -= degree_step
                    print("LEFT",steer_angle)
                    arduino.steer(steer_angle)
                elif event.key == pygame.K_RIGHT:  # Tasto "Destra" per girare a destra
                    if steer_angle < max_degree:
                        steer_angle += degree_step
                    print("RIGHT",steer_angle)
                    arduino.steer(steer_angle)
                elif event.key == pygame.K_SPACE:  # Tasto "Spazio" per fermare l'auto
                    speed = 0
                    arduino.stop()
                    print("STOP")

        # Aggiorna lo schermo di visualizzazione
        game_display.fill((255, 255, 255))
        pygame.display.update()

    pygame.quit()
    quit()

# Avvia il gioco
game_loop()
#Threading.thread(target=checkStatus).start()

def checkStatus():
    while True:
        arduino.get_status()
        time.sleep(1)
