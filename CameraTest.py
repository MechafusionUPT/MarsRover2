from flask import Flask, render_template_string, Response
import cv2
from pyzbar import pyzbar
import os
import board
import sys
import adafruit_dht
import json
import time
import threading

TEAM_NAME = "ALSERA"  # !!Aici schimba numele echipei
os.environ["BLINKA_FORCE"] = "1"
dht = adafruit_dht.DHT11(board.D4)

app = Flask(__name__)

qr_content = "Niciun cod detectat încă"
generated_url = "—"

# ----------------------------------------------------------
# Funcții pentru senzor și QR
# ----------------------------------------------------------
def read_sensor():
    for _ in range(5):
        try:
            t = dht.temperature
            h = dht.humidity
            if t is not None and h is not None:
                return t, h
        except Exception:
            time.sleep(1)
    return None, None


# Folosim o singură instanță de VideoCapture pentru QR și live feed
cap = cv2.VideoCapture(0)
last_qr = None

def scan_qr():
    global qr_content, generated_url, last_qr

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.2)
            continue

        decoded = pyzbar.decode(frame)
        for obj in decoded:
            qr_data = obj.data.decode("utf-8")
            if qr_data != last_qr:
                last_qr = qr_data
                qr_content = qr_data
                print("QR detectat:", qr_data)

                try:
                    data = json.loads(qr_data)
                    checkpoint = data.get("checkpoint", "t1")
                    secret = data.get("secret", "unknown")
                except Exception:
                    checkpoint, secret = "t1", "unknown"

                temp, hum = read_sensor()
                if temp is not None:
                    generated_url = (
                        f"https://iovanalex.ro/sec/checkin.php?"
                        f"team={TEAM_NAME}&p={checkpoint}&secret={secret}&t={temp}&h={hum}"
                    )
                    print("URL generat:", generated_url)
                else:
                    generated_url = "Eroare la citirea senzorului DHT11!"

        time.sleep(0.5)


# ----------------------------------------------------------
# Generator pentru live video feed
# ----------------------------------------------------------
def gen_frames():
    global cap
    while True:
        success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# ----------------------------------------------------------
# Pagina principală cu QR și live feed
# ----------------------------------------------------------
@app.route("/")
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ro">
    <head>
        <meta charset="UTF-8">
        <title>QR & Sensor Data + Live Camera</title>
        <style>
            body { font-family: Arial; margin: 20px; }
            h1 { color: #333; }
            .data { font-size: 1.1em; margin-bottom: 20px; }
            .url { margin-top: 10px; }
            img { border: 1px solid #ccc; }
        </style>
    </head>
    <body>
        <h1>QR & Sensor Data (Live)</h1>
        <div class="data">
            <p><b>Ultimul cod QR detectat:</b> <span id="qr">{{ content }}</span></p>
            <p class="url"><b>URL generat:</b> <a id="url" href="{{ url }}" target="_blank">{{ url }}</a></p>
        </div>

        <h2>Live Camera Feed</h2>
        <img src="{{ url_for('video_feed') }}" width="640" height="480">

        <script>
            async function updateData() {
                try {
                    const r = await fetch('/data');
                    const data = await r.json();
                    document.getElementById("qr").textContent = data.content;
                    const urlElem = document.getElementById("url");
                    urlElem.href = data.url;
                    urlElem.textContent = data.url;
                } catch(e) { console.error(e); }
            }
            setInterval(updateData, 2000);
        </script>
    </body>
    </html>
    """, content=qr_content, url=generated_url)


@app.route("/data")
def data():
    return {"content": qr_content, "url": generated_url}


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------
if __name__ == "__main__":
    t = threading.Thread(target=scan_qr, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
