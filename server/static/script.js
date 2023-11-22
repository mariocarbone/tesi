// Variabile globale per la mappa
var map;

// Variabile globale per i marker dei veicoli
var vehicleMarkers = [];
var vehicleCircles = [];

// Variabile globale marker RSU
var rsuMarkers = [];
var rsuCircles = [];

var vehicleData = {};

var rsuData = {};

var carIcon16 = L.icon({
  iconUrl: 'static/images/car.png',
  //shadowUrl: 'leaf-shadow.png',

  iconSize: [24, 24], // size of the icon
  //shadowSize: [50, 64], // size of the shadow
  iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
  //shadowAnchor: [4, 62],  // the same for the shadow
  popupAnchor: [0, -8] // point from which the popup should open relative to the iconAnchor
});

var camIcon16 = L.icon({
  iconUrl: 'static/images/camera.png',
  //shadowUrl: 'leaf-shadow.png',

  iconSize: [24, 24], // size of the icon
  //shadowSize: [50, 64], // size of the shadow
  iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
  //shadowAnchor: [4, 62],  // the same for the shadow
  popupAnchor: [0, -8] // point from which the popup should open relative to the iconAnchor
});

var carIcon = L.icon({
  iconUrl: 'static/images/car.png',
  //shadowUrl: 'leaf-shadow.png',

  iconSize: [32, 32], // size of the icon
  //shadowSize: [50, 64], // size of the shadow
  iconAnchor: [16, 16], // point of the icon which will correspond to marker's location
  //shadowAnchor: [4, 62],  // the same for the shadow
  popupAnchor: [0, -16] // point from which the popup should open relative to the iconAnchor
});

var camIcon = L.icon({
  iconUrl: 'static/images/camera.png',
  //shadowUrl: 'leaf-shadow.png',

  iconSize: [32, 32], // size of the icon
  //shadowSize: [50, 64], // size of the shadow
  iconAnchor: [16, 16], // point of the icon which will correspond to marker's location
  //shadowAnchor: [4, 62],  // the same for the shadow
  popupAnchor: [0, -16] // point from which the popup should open relative to the iconAnchor
});


document.addEventListener("DOMContentLoaded", function () {
  map = L.map('map').setView([39.35609, 16.2282], 18);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

  
  // add the OpenStreetMap tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
  }).addTo(map);

  var m = L.marker([39.35671, 16.22795], {
    rotationAngle: 45,
    icon: carIcon,
    draggable: true
  }).addTo(map).bindPopup('Sono una macchina di prova!');


});

// Funzione per aggiornare la lista dei veicoli

function updateVehicleList(vehicleData) {
  var vehicleList = document.getElementById('vehicle-list');
  vehicleList.innerHTML = ''; // Svuota la lista precedente

  // Popola la lista con gli elementi dei veicoli
  for (var vehicleId in vehicleData) {
    if (vehicleData.hasOwnProperty(vehicleId)) {
      var vehicle = vehicleData[vehicleId];
      var listItem = document.createElement('li');
      listItem.classList.add('list-group-item');
      listItem.textContent = 'Veicolo ' + vehicle.id;
      listItem.setAttribute('data-id', vehicle.id); // Imposta l'attributo data-id con l'ID del veicolo
      vehicleList.appendChild(listItem);
    }
  }
}

// Funzione per aggiornare il marker di un veicolo
function updateVehicleMarker(vehicle) {
  var marker = vehicleMarkers[vehicle.id];

  // Se il marker non esiste, creo un nuovo marker per il veicolo e lo aggiungo alla mappa
  if (!marker) {
    marker = L.marker([vehicle.gps.lat, vehicle.gps.lon], { icon: carIcon16 }).addTo(map).bindPopup('ID: ' + vehicle.id);

    vehicleMarkers[vehicle.id] = marker;
  }
  // Altrimenti, aggiorna la posizione del marker
  else {
    marker.setLatLng([vehicle.gps.lat, vehicle.gps.lon]);
  }

  // Aggiungi o aggiorna il marker circolare
  var circle = vehicleCircles[vehicle.id];
  if (!circle) {
    circle = L.circle([vehicle.gps.lat, vehicle.gps.lon], {
      radius: 60, // Raggio del cerchio in metri
      color: 'red',
      fillColor: '#f03',
      fillOpacity: 0.1
    }).addTo(map);
    vehicleCircles[vehicle.id] = circle;
  }
  else {
    circle.setLatLng([vehicle.gps.lat, vehicle.gps.lon]);
  }
}

// Funzione per aggiornare il marker delle RSU
function updateRSUMarker(rsu) {
  var markerRSU = rsuMarkers[rsu.id];

  // Se il marker non esiste, creo un nuovo marker per l'rsu e lo aggiungo alla mappa
  if (!markerRSU) {
    markerRSU = L.marker([rsu.gps.lat, rsu.gps.lon], { icon: camIcon16 }).addTo(map).bindPopup('ID: ' + rsu.id);

    rsuMarkers[rsu.id] = markerRSU;
  }
  // Altrimenti, aggiorna la posizione del marker
  else {
    markerRSU.setLatLng([rsu.gps.lat, rsu.gps.lon]);
  }

  // Aggiungi o aggiorna il marker circolare
  var circle = rsuCircles[rsu.id];
  if (!circle) {
    circle = L.circle([rsu.gps.lat, rsu.gps.lon], {
      radius: 100, // Raggio del cerchio in metri
      color: 'blue',
      fillColor: '#f03',
      fillOpacity: 0.1
    }).addTo(map);
    rsuCircles[rsu.id] = circle;
  }
  else {
    circle.setLatLng([rsu.gps.lat, rsu.gps.lon]);
  }
}

//Funzione per ottenere dati delle RSU
function getRsuDetails() {
  fetch('http://localhost:5000/rsu-details')
    .then(response => response.json())
    .then(data => {
      rsuData = data;
      var rsuDetails = document.getElementById('rsu-details');
      rsuDetails.innerHTML =
        '<h4>Dettagli RSU:</h4>';

      for (var rsuId in rsuData) {
        if (rsuData.hasOwnProperty(rsuId)) {
          var rsu = rsuData[rsuId];

          //Aggiorno la lista delle RSU  --- ora è una
          rsuDetails.innerHTML +=
            'RSU ID: ' + rsu.id + '<br>' +
            'Numero client connessi: ' + rsu.connected_clients + '<br>' +
            'SSID: ' + rsu.ssid + '<br><br>';

            updateRSUMarker(rsu);
        }
      }
    })
    .catch(error => {
      console.log('Errore nella richiesta HTTP:', error);
    });
}


// Funzione per ottenere la lista dei veicoli tramite una richiesta HTTP
function getVehicleList() {
  fetch('http://localhost:5000/veicoli')
    .then(response => response.json())
    .then(data => {
      vehicleData = data; // Aggiorna la variabile vehicleData con i dati dei veicoli
      updateVehicleList(vehicleData);

      // Aggiorna i marker dei veicoli sulla mappa
      for (var vehicleId in vehicleData) {
        if (vehicleData.hasOwnProperty(vehicleId)) {
          var vehicle = vehicleData[vehicleId];
          updateVehicleMarker(vehicle);
        }
      }
    })

    .catch(error => {
      console.log('Errore nella richiesta HTTP:', error);
    });
}

// Funzione per aggiornare i dettagli del veicolo nel box dedicato
function updateVehicleDetails(vehicle) {
  var vehicleDetails = document.getElementById('vehicle-details');
  vehicleDetails.innerHTML =
    '<h4>Dettagli del veicolo:<br>' + vehicle.id + '</h4><br>' +
    'Accelerazione: ' + vehicle.acceleration + '<br>' +
    'Frenata: ' + vehicle.braking + '<br>' +
    'Velocità: ' + vehicle.speed + '<br>' +
    'Latitudine: ' + vehicle.gps.lat + '<br>' +
    'Longitudine: ' + vehicle.gps.lon + '<br>' +
    'Distanza: ' + vehicle.distance + '<br>' +
    'ID RSU: ' + vehicle.rsu_id;
}

// Funzione per gestire il click sugli elementi della lista dei veicoli
function handleVehicleClick(event) {
  var vehicleId = event.target.getAttribute('data-id'); // Ottieni l'ID del veicolo cliccato
  var vehicle = vehicleData[vehicleId];

  if (vehicle) {
    updateVehicleDetails(vehicle); // Aggiorna i dettagli del veicolo nel box dedicato
    map.setView([vehicle.gps.lat, vehicle.gps.lon], 18); // Centra la mappa sulla posizione del veicolo
  }
}

var centerButton = document.getElementById('center-button');
centerButton.addEventListener('click', function () {
  var desiredLatLng = L.latLng(39.35609, 16.2282); // Latitudine e longitudine del punto desiderato
  map.setView(desiredLatLng, 18); // Imposta la vista sulla posizione desiderata con un determinato livello di zoom
});

// Aggiungi il gestore di eventi per il click sugli elementi della lista dei veicoli
var vehicleList = document.getElementById('vehicle-list');
vehicleList.addEventListener('click', handleVehicleClick);


// Aggiorna la lista dei veicoli e i marker ogni secondo
setInterval(getVehicleList, 1000);

// Aggiorna i dettagli della RSU ogni 5 secondi
setInterval(getRsuDetails, 2000);