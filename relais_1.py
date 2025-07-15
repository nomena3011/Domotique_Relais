from flask import Flask, render_template_string
import RPi.GPIO as GPIO

RELAY_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head><title>Contrôle du relais</title></head>
<body>
  <h2>Contrôle du relais</h2>
  <form action="/on" method="post">
    <button type="submit">Allumer</button>
  </form>
  <form action="/off" method="post">
    <button type="submit">Éteindre</button>
  </form>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/on', methods=['POST'])
def on():
    GPIO.output(RELAY_PIN, GPIO.LOW)
    return render_template_string(HTML)

@app.route('/off', methods=['POST'])
def off():
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    return render_template_string(HTML)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()

