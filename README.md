# Moduli Python e Script Tesi

Lo script principale app.py va avviato sul rover. La libreria darknet.py usata nello script avvia 3 reti neurali che usano Yolo v3, v3_tiny e v4_tiny per effettuare object detection, con le prediction in formato JSON prodotte dalla rete si utilizza alert_lib.py per elaborare le prediction e capire se sono rilevamenti che possono portare a collisioni del veicolo, qui entra in gioco la libreria mqtt_lib.py, necessaria per ricevere ed inviare comunicazioni con il Broker MQTT riguardanti alert o stato del veicolo.
