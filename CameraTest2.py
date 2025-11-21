from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import cv2
from pyzbar import pyzbar
import os
import board
import adafruit_dht
import json
import time
import threading

# ==============================================
# IMPORT ROVER MOTORS
# ==============================================
from motors.motorsTestPCA import (
    move_forward, move_backward, stir_left, stir_right, stop_all
)

# ==============================================
# IMPORT GRIPPER + PITCH (servo @0x40)
# ==============================================
from motors.gripper import (
    init_servos,
    close_grip,
    open_grip,
    pitch_up,
    pitch_down,
    servo_up,
    servo_down
)

TEAM_NAME = "ALSERA"
os.environ["BLINKA_FORCE"] = "1"

# ==============================================
# SENZOR DHT11 - GPIO4
# ==============================================
dht = adafruit_dht.DHT11(board.D4)

# ==============================================
# FLASK + SOCKET.IO
# ==============================================
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

qr_content = "Niciun cod detectat încă"
generated_url = "—"

print(">>> CameraTest2 PORNIT (Flask + SocketIO)")

# ==============================================
# FUNCȚII SENZOR + QR
# ==============================================
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


cap = cv2.VideoCapture(0) #camera rover 
cap2 = cv2.VideoCapture(2) #camera gripper
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


# ==============================================
# GENERATOR VIDEO FEED (MJPEG)
# ==============================================
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

def gen_frames2():
    global cap2
    while True:
        success, frame = cap2.read()
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

@app.route("/video_feed2")
def video_feed2():
    return Response(gen_frames2(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# ==============================================
# PAGINA PRINCIPALĂ
# ==============================================
@app.route("/")
def index():
    return render_template("qr_livefeed.html", content=qr_content, url=generated_url)


@app.route("/data")
def data():
    return {"content": qr_content, "url": generated_url}


# ==============================================
# JOYSTICK → MOTOARE + GRIPPER + PITCH
# ==============================================
def handle_joystick_command_simple(cmd: dict):
    """
    cmd: { vx, vy, sx, grip, pitch }
    
    Mapping real PS4:
    - grip = 1   → X (close grip)
    - grip = -1  → Square (open grip)
    - pitch = 1  → Triangle (pitch up)
    - pitch = -1 → Circle (pitch down)
    """

    try:
        vy = float(cmd.get("vy", 0.0))
        sx = float(cmd.get("sx", 0.0))

        grip = int(cmd.get("grip", 0))
        pitch = int(cmd.get("pitch", 0))

        print(f"[JOYSTICK] vy={vy:.2f} sx={sx:.2f} grip={grip} pitch={pitch}")

        TH = 0.3

        # ---------------- MOTOARE ----------------
        if vy > TH:
            move_forward(70)
        elif vy < -TH:
            move_backward(70)
        elif sx > TH:
            stir_right(70)
        elif sx < -TH:
            stir_left(70)
        else:
            stop_all()

        # ---------------- GRIP -----------------------
        DEGREE = 40
        if grip == 1:
            print("CMD: GRIP CLOSE")
            servo_up(DEGREE)

        if grip == -1:
            print("CMD: GRIP OPEN")
            servo_down(DEGREE)

        # ---------------- PITCH ----------------------
        if pitch == 1:
            print("CMD: PITCH UP")
            pitch_up()

        if pitch == -1:
            print("CMD: PITCH DOWN")
            pitch_down()

    except Exception as e:
        print("Eroare handle_joystick_command_simple:", e)
        try:
            stop_all()
        except:
            pass


@socketio.on("connect")
def on_connect():
    print(">>> SocketIO: client conectat")


@socketio.on("disconnect")
def on_disconnect():
    print(">>> SocketIO: client deconectat")
    try:
        stop_all()
    except Exception:
        pass


@socketio.on("control.move")
def on_control_move(data):
    print("EVENT control.move:", data)
    handle_joystick_command_simple(data)


# ==============================================
# MAIN (fără reloader)
# ==============================================
if __name__ == "__main__":
    t = threading.Thread(target=scan_qr, daemon=True)
    t.start()

    init_servos()

    print(">>> Pornesc serverul pe 0.0.0.0:5000 cu SocketIO...")
    socketio.run(app, host="0.0.0.0", port=5000)
