from flask import Flask, render_template_string, redirect, url_for
import RPi.GPIO as GPIO
import time

# Configuration des broches GPIO pour 4 relais
# Assurez-vous que ces numéros de broches correspondent à votre câblage
RELAY_PINS = {
    "Relais 1": 17,
    "Relais 2": 27,
    "Relais 3": 22,
    "Relais 4": 23
}

# Initialisation du GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in RELAY_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    # Mettre tous les relais sur OFF au démarrage (HIGH = OFF pour la plupart des modules)
    GPIO.output(pin, GPIO.HIGH)

app = Flask(__name__)

# Le template HTML avec du style CSS intégré
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contrôle des Relais</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 400px;
            text-align: center;
        }
        h2 {
            color: #333;
            margin-bottom: 25px;
        }
        .relay-control {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }
        .relay-name {
            font-size: 1.1em;
            font-weight: bold;
            color: #555;
        }
        .buttons form {
            display: inline-block;
            margin-left: 5px;
        }
        button {
            color: white;
            border: none;
            padding: 12px 18px;
            border-radius: 6px;
            font-size: 1em;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.1s;
        }
        button:hover {
            opacity: 0.9;
        }
        button:active {
            transform: scale(0.95);
        }
        .on-button {
            background-color: #28a745; /* Vert */
        }
        .off-button {
            background-color: #dc3545; /* Rouge */
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Panneau de Contrôle des Relais</h2>
        
        {% for name, pin in relays.items() %}
        <div class="relay-control">
            <span class="relay-name">{{ name }}</span>
            <div class="buttons">
                <form action="{{ url_for('control_relay', pin=pin, action='on') }}" method="post">
                    <button class="on-button" type="submit">Allumer</button>
                </form>
                <form action="{{ url_for('control_relay', pin=pin, action='off') }}" method="post">
                    <button class="off-button" type="submit">Éteindre</button>
                </form>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    # Passe le dictionnaire des relais au template
    return render_template_string(HTML_TEMPLATE, relays=RELAY_PINS)

@app.route('/relay/<int:pin>/<action>', methods=['POST'])
def control_relay(pin, action):
    # Vérifie si la broche demandée est bien l'une de nos broches de relais
    if pin in RELAY_PINS.values():
        if action == 'on':
            # GPIO.LOW allume le relais
            GPIO.output(pin, GPIO.LOW)
        elif action == 'off':
            # GPIO.HIGH éteint le relais
            GPIO.output(pin, GPIO.HIGH)
    
    # Redirige vers la page d'accueil
    return redirect(url_for('index'))

if __name__ == '__main__':
    try:
        # Lance l'application Flask, accessible sur le réseau local
        app.run(host='0.0.0.0', port=5000)
    finally:
        # Nettoie les GPIO à la fermeture de l'application
        print("\n Nettoyage des GPIO...")
        GPIO.cleanup()
