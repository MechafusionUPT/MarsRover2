from flask import Flask, render_template, Response
import cv2
from pyzbar import pyzbar
import os
import time
import threading
from urllib.parse import urlparse, parse_qs
import adafruit_dht
import board

TEAM_NAME = "ALSERA"
os.environ["BLINKA_FORCE"] = "1"

app = Flask(__name__)

qr_content = "Niciun cod detectat încă"
generated_url = "—"
last_qr = None

dht = adafruit_dht.DHT11(board.D4)

# -----------------------------
# CAMERA SETUP UNICĂ
# -----------------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

frame_global = None


def camera_thread():
    global frame_global
    while True:
        ret, frame = cap.read()
        if ret:
            frame_global = frame
        time.sleep(0.01)


def scan_qr():
    global qr_content, generated_url, last_qr

    while True:
        if frame_global is None:
            time.sleep(0.2)
            continue

        decoded = pyzbar.decode(frame_global)
        for obj in decoded:
            qr_data = obj.data.decode("utf-8")

            if qr_data != last_qr:
                last_qr = qr_data
                qr_content = qr_data
                print("QR detectat:", qr_data)

                parsed = urlparse(qr_data)
                query = parse_qs(parsed.query)

                checkpoint = query.get("p", ["t1"])[0]
                secret = query.get("secret", ["unknown"])[0]

                try:
                    temp = dht.temperature
                    hum = dht.humidity
                except:
                    temp = None
                    hum = None

                if temp is not None:
                    generated_url = (
                        f"https://iovanalex.ro/sec/checkin.php?"
                        f"team={TEAM_NAME}&p={checkpoint}&secret={secret}&t={temp}&h={hum}"
                    )
                else:
                    generated_url = "Eroare citire DHT11"

        time.sleep(0.4)


def gen_frames():
    while True:
        if frame_global is None:
            continue

        ret, buffer = cv2.imencode('.jpg', frame_global)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/")
def index():
    return render_template("qr_livefeed.html", content=qr_content, url=generated_url)


@app.route("/data")
def data():
    return {"content": qr_content, "url": generated_url}


if __name__ == "__main__":
    threading.Thread(target=camera_thread, daemon=True).start()
    threading.Thread(target=scan_qr, daemon=True).start()

    print("SERVER PORNIT pe 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
