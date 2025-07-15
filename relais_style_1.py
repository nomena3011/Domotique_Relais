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
    <title>Contrôle des Relais</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        h1 {
            color: white;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            letter-spacing: 1px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            width: 100%;
            max-width: 1200px;
            margin-bottom: 40px;
        }

        .relay {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .relay::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }

        .relay:hover::before {
            left: 100%;
        }

        .relay:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.2);
        }

        .relay h3 {
            font-size: 1.4em;
            margin-bottom: 15px;
            color: #333;
            font-weight: 600;
        }

        .relay .etat {
            margin: 15px 0;
            font-weight: bold;
            font-size: 1.2em;
            padding: 10px;
            border-radius: 10px;
            transition: all 0.3s ease;
        }

        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 50px;
            font-weight: bold;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
            min-width: 140px;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255,255,255,0.3);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.3s, height 0.3s;
        }

        .btn:hover::before {
            width: 300px;
            height: 300px;
        }

        .btn:active {
            transform: scale(0.95);
        }

        .on {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4);
        }

        .on:hover {
            background: linear-gradient(135deg, #2ecc71, #27ae60);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(46, 204, 113, 0.6);
        }

        .off {
            background: linear-gradient(135deg, #c0392b, #e74c3c);
            color: white;
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.4);
        }

        .off:hover {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(231, 76, 60, 0.6);
        }

        .global {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 25px;
            padding: 30px;
            text-align: center;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 2px solid rgba(255, 255, 255, 0.2);
            max-width: 600px;
            width: 100%;
        }

        .global h3 {
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #333;
            font-weight: 600;
        }

        .global .btn {
            margin: 10px;
            font-size: 1.1em;
            padding: 15px 35px;
            min-width: 200px;
        }

        .status-on {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .status-off {
            background: linear-gradient(135deg, #f8d7da, #f1b0b7);
            color: #721c24;
            border: 1px solid #f1b0b7;
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 2em;
            }
            
            .global .btn {
                min-width: 150px;
                margin: 5px;
            }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .relay:hover h3 {
            animation: pulse 1s infinite;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <h1>🔌 Contrôle des Relais</h1>
    <div class="grid">
        {% for name, pin in relays.items() %}
        <div class="relay">
            <h3>{{ name }}</h3>
            <div class="etat" id="etat-{{ pin }}">
                <div class="loading"></div>
            </div>
            <button class="btn" id="btn-{{ pin }}" onclick="toggleRelay({{ pin }})">
                <div class="loading"></div>
            </button>
        </div>
        {% endfor %}
    </div>

    <div class="global">
        <h3>🎛️ Contrôle Global</h3>
        <button class="btn on" onclick="globalControl('on')">🔥 TOUS ALLUMER</button>
        <button class="btn off" onclick="globalControl('off')">❄️ TOUS ÉTEINDRE</button>
    </div>

    <script>
        function updateStates() {
            fetch('/states')
                .then(response => response.json())
                .then(data => {
                    for (const [pin, state] of Object.entries(data)) {
                        const etat = document.getElementById('etat-' + pin);
                        const btn = document.getElementById('btn-' + pin);

                        if (state === 'on') {
                            etat.innerHTML = '🟢 ON';
                            etat.className = 'etat status-on';
                            btn.innerText = 'ÉTEINDRE';
                            btn.className = 'btn off';
                        } else {
                            etat.innerHTML = '🔴 OFF';
                            etat.className = 'etat status-off';
                            btn.innerText = 'ALLUMER';
                            btn.className = 'btn on';
                        }
                    }
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
            const buttons = document.querySelectorAll('.global .btn');
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
