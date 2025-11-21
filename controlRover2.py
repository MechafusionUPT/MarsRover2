from flask import Flask, render_template_string
from flask_socketio import SocketIO
from motorsTestPCA import move_forward, move_backward, stir_left, stir_right, stop_all

# ==================================================
#   FLASK + SOCKET.IO SETUP
# ==================================================

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

current_direction = ""
current_speed = 0

# ==================================================
#   INTERFAȚĂ HTML CU SĂGEȚI
# ==================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Joystick Rover Control</title>
    <style>
        body { font-family: Arial; text-align: center; margin-top: 50px; }
        .arrow-container { position: relative; width: 200px; height: 200px; margin: auto; }
        .arrow { position: absolute; width: 0; height: 0; border-style: solid; opacity: 0.3; }
        #up    { border-width: 0 20px 40px 20px;  border-color: transparent transparent black transparent; top: 0; left: 80px; }
        #down  { border-width: 40px 20px 0 20px; border-color: black transparent transparent transparent; bottom: 0; left: 80px; }
        #left  { border-width: 20px 40px 20px 0; border-color: transparent black transparent transparent; top: 80px; left: 0; }
        #right { border-width: 20px 0 20px 40px; border-color: transparent transparent transparent black; top: 80px; right: 0; }
        .active { opacity: 1; border-color: red; }
        h2 { margin-top: 25px; color: #444; }
    </style>
</head>
<body>
    <h1>Joystick Rover Control</h1>
    <h2 id="speedVal">Speed: 0</h2>

    <div class="arrow-container">
        <div class="arrow" id="up"></div>
        <div class="arrow" id="down"></div>
        <div class="arrow" id="left"></div>
        <div class="arrow" id="right"></div>
    </div>

    <script src="https://cdn.socket.io/4.6.1/socket.io.min.js"></script>
    <script>
        const socket = io();

        socket.on("move_update", data => {
            const {direction, speed} = data;
            document.getElementById("speedVal").textContent = "Speed: " + speed;

            ["up","down","left","right"].forEach(id =>
                document.getElementById(id).classList.remove("active")
            );

            if (direction === "INAINTE") document.getElementById("up").classList.add("active");
            if (direction === "INAPOI")  document.getElementById("down").classList.add("active");
            if (direction === "STANGA")  document.getElementById("left").classList.add("active");
            if (direction === "DREAPTA") document.getElementById("right").classList.add("active");
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

# ==================================================
#   SOCKET.IO - PRIMIM COMANDA DE LA CONTROLLER
# ==================================================

@socketio.on("control.move")
def handle_move(data):
    global current_direction, current_speed

    vx = data["vx"]
    vy = data["vy"]

    # viteza = intensitatea joystickului
    speed = int(abs(vx if abs(vx)>abs(vy) else vy) * 100)
    current_speed = speed

    # direcție
    if vy > 0.2:
        current_direction = "INAINTE"
        move_forward(speed)
    elif vy < -0.2:
        current_direction = "INAPOI"
        move_backward(speed)
    elif vx > 0.2:
        current_direction = "DREAPTA"
        stir_right(speed)
    elif vx < -0.2:
        current_direction = "STANGA"
        stir_left(speed)
    else:
        current_direction = "STOP"
        stop_all()

    socketio.emit("move_update", {
        "direction": current_direction,
        "speed": current_speed
    })

# ==================================================
#   RUN
# ==================================================

if __name__ == "__main__":
    try:
        socketio.run(app, host="0.0.0.0", port=8000)
    finally:
        stop_all()
