from flask import Flask, render_template_string, jsonify, request
import RPi.GPIO as GPIO

# Configuration des broches GPIO pour 8 relais
RELAY_PINS = {
    "Relais 1": 17,
    "Relais 2": 27,
    "Relais 3": 22,
    "Relais 4": 23,
    "Relais 5": 5,
    "Relais 6": 6,
    "Relais 7": 13,
    "Relais 8": 19
}

# Initialisation du GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in RELAY_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contrôle Domotique</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }

        .header h1 {
            font-size: 2.5em;
            font-weight: 300;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }

        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
            font-weight: 300;
        }

        .status-bar {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 30px;
            text-align: center;
            color: white;
            font-size: 0.9em;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
        }

        .relay-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            position: relative;
        }

        .relay-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
        }

        .relay-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .relay-title {
            font-size: 1.3em;
            font-weight: 600;
            color: #333;
        }

        .relay-number {
            width: 35px;
            height: 35px;
            background: #667eea;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.1em;
        }

        .relay-status {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            font-weight: 600;
            font-size: 1.1em;
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 5px;
        }

        .status-inactive {
            color: #e74c3c;
        }

        .status-active {
            color: #27ae60;
        }

        .status-indicator.inactive {
            background: #e74c3c;
        }

        .status-indicator.active {
            background: #27ae60;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .relay-button {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 25px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .relay-button.on {
            background: #27ae60;
            color: white;
        }

        .relay-button.on:hover {
            background: #2ecc71;
            transform: translateY(-1px);
        }

        .relay-button.off {
            background: #e74c3c;
            color: white;
        }

        .relay-button.off:hover {
            background: #c0392b;
            transform: translateY(-1px);
        }

        .relay-button:active {
            transform: scale(0.98);
        }

        .global-controls {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 25px;
            margin-top: 30px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }

        .global-controls h3 {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #333;
            font-weight: 600;
        }

        .global-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .global-button {
            flex: 1;
            min-width: 160px;
            padding: 15px 25px;
            border: none;
            border-radius: 25px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .global-button.on {
            background: #27ae60;
            color: white;
        }

        .global-button.on:hover {
            background: #2ecc71;
            transform: translateY(-2px);
        }

        .global-button.off {
            background: #e74c3c;
            color: white;
        }

        .global-button.off:hover {
            background: #c0392b;
            transform: translateY(-2px);
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }
            
            .global-buttons {
                flex-direction: column;
            }
            
            .global-button {
                min-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Contrôle Domotique</h1>
            <div class="subtitle">Système de contrôle intelligent - 8 Relais</div>
        </div>

        <div class="status-bar">
            📊 Statut Système: <span id="active-count">0</span>/8 relais actifs | 🌐 IP: 192.168.137.143 | 📶 WiFi: -35 dBm
        </div>

        {% for name, pin in relays.items() %}
        <div class="relay-card">
            <div class="relay-header">
                <div class="relay-title">{{ name }}</div>
                <div class="relay-number">{{ loop.index }}</div>
            </div>
            <div class="relay-status" id="status-{{ pin }}">
                <div class="status-indicator inactive"></div>
                <div class="status-indicator inactive"></div>
                <span class="status-inactive">INACTIF</span>
            </div>
            <button class="relay-button on" id="btn-{{ pin }}" onclick="toggleRelay({{ pin }})">
                <div class="loading"></div>
            </button>
        </div>
        {% endfor %}

        <div class="global-controls">
            <h3>🎛️ Contrôle Global</h3>
            <div class="global-buttons">
                <button class="global-button on" onclick="globalControl('on')">🔥 TOUS ALLUMER</button>
                <button class="global-button off" onclick="globalControl('off')">❄️ TOUS ÉTEINDRE</button>
            </div>
        </div>
    </div>

    <script>
        function updateStates() {
            fetch('/states')
                .then(response => response.json())
                .then(data => {
                    let activeCount = 0;
                    
                    for (const [pin, state] of Object.entries(data)) {
                        const statusDiv = document.getElementById('status-' + pin);
                        const btn = document.getElementById('btn-' + pin);
                        const indicators = statusDiv.querySelectorAll('.status-indicator');
                        const statusText = statusDiv.querySelector('span');

                        if (state === 'on') {
                            activeCount++;
                            indicators.forEach(indicator => {
                                indicator.className = 'status-indicator active';
                            });
                            statusText.textContent = 'ACTIF';
                            statusText.className = 'status-active';
                            btn.innerText = 'ÉTEINDRE';
                            btn.className = 'relay-button off';
                        } else {
                            indicators.forEach(indicator => {
                                indicator.className = 'status-indicator inactive';
                            });
                            statusText.textContent = 'INACTIF';
                            statusText.className = 'status-inactive';
                            btn.innerText = 'ALLUMER';
                            btn.className = 'relay-button on';
                        }
                    }
                    
                    document.getElementById('active-count').textContent = activeCount;
                });
        }

        function toggleRelay(pin) {
            const btn = document.getElementById('btn-' + pin);
            btn.style.opacity = '0.6';
            btn.style.cursor = 'wait';
            
            fetch(`/relay/${pin}/toggle`, { method: 'POST' })
                .then(() => {
                    updateStates();
                    btn.style.opacity = '1';
                    btn.style.cursor = 'pointer';
                });
        }

        function globalControl(action) {
            const buttons = document.querySelectorAll('.global-button');
            buttons.forEach(btn => {
                btn.style.opacity = '0.6';
                btn.style.cursor = 'wait';
            });
            
            fetch(`/relay/all/${action}`, { method: 'POST' })
                .then(() => {
                    updateStates();
                    buttons.forEach(btn => {
                        btn.style.opacity = '1';
                        btn.style.cursor = 'pointer';
                    });
                });
        }

        updateStates();
        setInterval(updateStates, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, relays=RELAY_PINS)

@app.route('/states')
def get_states():
    states = {pin: 'off' if GPIO.input(pin) == GPIO.HIGH else 'on' for pin in RELAY_PINS.values()}
    return jsonify(states)

@app.route('/relay/<int:pin>/toggle', methods=['POST'])
def toggle_relay(pin):
    if pin in RELAY_PINS.values():
        GPIO.output(pin, GPIO.LOW if GPIO.input(pin) == GPIO.HIGH else GPIO.HIGH)
    return ('', 204)

@app.route('/relay/all/<action>', methods=['POST'])
def global_control(action):
    for pin in RELAY_PINS.values():
        GPIO.output(pin, GPIO.LOW if action == 'on' else GPIO.HIGH)
    return ('', 204)

if __name__ == '__main__':
    try:
        print("Serveur en cours d'exécution sur http://[IP_RASPBERRY]:5000")
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()
