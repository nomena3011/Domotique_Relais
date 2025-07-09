from flask import Flask, render_template_string, jsonify, request
import RPi.GPIO as GPIO

# Configuration des broches GPIO
RELAY_PINS = {
    "Relais 1": 17,
    "Relais 2": 27,
    "Relais 3": 22,
    "Relais 4": 23
}

# Initialisation GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in RELAY_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)  # OFF par défaut

app = Flask(__name__)

# Template HTML avec retour visuel
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Contrôle des Relais</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            width: 400px;
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
        }
        .relay-control {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status {
            font-weight: bold;
            margin-top: 5px;
        }
        .on-button {
            background-color: #28a745;
            color: white;
            padding: 8px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .off-button {
            background-color: #dc3545;
            color: white;
            padding: 8px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .state {
            font-size: 0.9em;
            margin-top: 6px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Panneau de Contrôle</h2>
        {% for name, pin in relays.items() %}
        <div class="relay-control" id="relay-{{ pin }}">
            <div>
                <div>{{ name }}</div>
                <div class="state" id="state-{{ pin }}">...</div>
            </div>
            <div>
                <button class="on-button" onclick="toggleRelay({{ pin }}, 'on')">Allumer</button>
                <button class="off-button" onclick="toggleRelay({{ pin }}, 'off')">Éteindre</button>
            </div>
        </div>
        {% endfor %}
    </div>

    <script>
    // Met à jour l'état affiché (🟢 / 🔴)
    function updateStates() {
        fetch("/states")
        .then(response => response.json())
        .then(data => {
            for (const [pin, state] of Object.entries(data)) {
                const stateElement = document.getElementById("state-" + pin);
                if (state === "on") {
                    stateElement.innerHTML = "🟢 ON";
                    stateElement.style.color = "green";
                } else {
                    stateElement.innerHTML = "🔴 OFF";
                    stateElement.style.color = "red";
                }
            }
        });
    }

    // Allume/Éteint un relais
    function toggleRelay(pin, action) {
        fetch(`/relay/${pin}/${action}`, { method: 'POST' })
        .then(() => updateStates());
    }

    // Mise à jour régulière de l'état
    updateStates();
    setInterval(updateStates, 5000); // Actualise toutes les 5 secondes
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, relays=RELAY_PINS)

@app.route('/relay/<int:pin>/<action>', methods=['POST'])
def control_relay(pin, action):
    if pin in RELAY_PINS.values():
        if action == 'on':
            GPIO.output(pin, GPIO.LOW)
        elif action == 'off':
            GPIO.output(pin, GPIO.HIGH)
    return '', 204

@app.route('/states')
def get_states():
    states = {}
    for name, pin in RELAY_PINS.items():
        state = GPIO.input(pin)
        states[pin] = "off" if state == GPIO.HIGH else "on"
    return jsonify(states)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()

