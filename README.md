README COMING SOON!

# Tesi: Sviluppo di un sistema di smart alerting basato su percezione cooperativa

Rover:  
Lo script principale app-main.py vi avviato sul rover, questo va ad utilizzare diverse librerie python tra cui Tensorflow per effettuare il riconoscimento di ostacoli e condividerli con altri dispositivi mediante protocollo mqtt.

La libreria detection.py utilizza Tensorflow che effettua la object detection. Con le prediction in formato JSON prodotte dalla rete si utilizza alert_lib.py per elaborare le prediction e capire se sono rilevamenti che possono portare a collisioni del veicolo (e in tal caso vengono gestiti dalla libreria control-lib.py) in ogni caso entra in gioco la libreria mqtt_lib.py, necessaria per ricevere ed inviare comunicazioni con il Broker MQTT riguardanti alert o stato del veicolo.
