const express = require('express');
const rpio = require('rpio');
const path = require('path');
const app = express();
const port = 5000;

// 🧠 Pins physiques utilisées pour les 8 relais
const pins = [11, 13, 15, 16, 18, 22, 29, 31]; // Physiques : GPIO17, 27, 22, 23, 24, 25, 5, 6

// Initialisation des relais (LOW = éteint)
let relayStates = Array(pins.length).fill(false);
pins.forEach((pin) => {
  rpio.open(pin, rpio.OUTPUT, rpio.LOW);
});

// Servir le frontend
app.use(express.static(path.join(__dirname, 'public')));

// ✅ Obtenir l'état de tous les relais
app.get('/api/status', (req, res) => {
  res.json({ relayStates });
});

// 🔁 Inverser un relais donné
app.get('/api/toggle/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);

  if (isNaN(id) || id < 0 || id >= pins.length) {
    return res.status(400).json({ error: 'ID de relais invalide (0 à 7)' });
  }

  relayStates[id] = !relayStates[id];
  rpio.write(pins[id], relayStates[id] ? rpio.HIGH : rpio.LOW);
  res.json({ id, state: relayStates[id] });
});

// ✅ Allumer tous les relais
app.get('/api/all/on', (req, res) => {
  relayStates = relayStates.map(() => true);
  pins.forEach(pin => rpio.write(pin, rpio.HIGH));
  res.json({ message: 'Tous les relais sont allumés.', relayStates });
});

// ✅ Éteindre tous les relais
app.get('/api/all/off', (req, res) => {
  relayStates = relayStates.map(() => false);
  pins.forEach(pin => rpio.write(pin, rpio.LOW));
  res.json({ message: 'Tous les relais sont éteints.', relayStates });
});

// 🧹 Nettoyage
process.on('SIGINT', () => {
  pins.forEach(pin => rpio.write(pin, rpio.LOW));
  pins.forEach(pin => rpio.close(pin));
  console.log("Tous les GPIO ont été libérés.");
  process.exit();
});

// 🚀 Lancer le serveur
app.listen(port, () => {
  console.log(`Serveur lancé sur http://localhost:${port}`);
});

