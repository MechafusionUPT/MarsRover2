"""
import socket

PORT = 5000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", PORT))
server.listen(1)
print("Aștept conexiune de la laptop...")

conn, addr = server.accept()
print("Conectat la:", addr)

try:
    while True:
        data = conn.recv(1024)
        if not data:
            break
        direction = data.decode()
        print("Direcție primită:", direction)  # afișează doar string-ul
except KeyboardInterrupt:
    print("Oprit de utilizator")
finally:
    conn.close()
    server.close()
"""
from flask import Flask, render_template_string
import socket
import threading

# Flask setup
app = Flask(__name__)

# Variabilă globală pentru direcțiile primite
directions = []

# HTML simplu pentru afișare
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Joystick Server</title>
    <meta http-equiv="refresh" content="0.5">
    <style>
        body { font-family: Arial; text-align: center; margin-top: 50px; }
        h1 { color: #333; }
        ul { list-style: none; font-size: 24px; padding: 0; }
        li { margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Direcții primite de la joystick</h1>
    <ul>
        {% for d in directions %}
            <li>{{ d }}</li>
        {% endfor %}
    </ul>
</body>
</html>
"""


from flask import Flask, render_template_string
import socket
import threading

app = Flask(__name__)

# Direcția curentă
current_direction = ""

# HTML + CSS + JS pentru afișarea săgeților
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Joystick Arrows</title>
    <style>
        body { font-family: Arial; text-align: center; margin-top: 50px; }
        .arrow-container { position: relative; width: 200px; height: 200px; margin: auto; }
        .arrow {
            position: absolute;
            width: 0; height: 0;
            border-style: solid;
            opacity: 0.3;
        }
        /* Sus */
        #up { border-width: 0 20px 40px 20px; border-color: transparent transparent black transparent; top: 0; left: 80px; }
        /* Jos */
        #down { border-width: 40px 20px 0 20px; border-color: black transparent transparent transparent; bottom: 0; left: 80px; }
        /* Stanga */
        #left { border-width: 20px 40px 20px 0; border-color: transparent black transparent transparent; top: 80px; left: 0; }
        /* Dreapta */
        #right { border-width: 20px 0 20px 40px; border-color: transparent transparent transparent black; top: 80px; right: 0; }
        .active { opacity: 1; border-color: red; }
    </style>
</head>
<body>
    <h1>Joystick Live</h1>
    <div class="arrow-container">
        <div class="arrow" id="up"></div>
        <div class="arrow" id="down"></div>
        <div class="arrow" id="left"></div>
        <div class="arrow" id="right"></div>
    </div>
    <script>
        async function fetchDirection() {
            const resp = await fetch('/direction');
            const data = await resp.text();
            ['up','down','left','right'].forEach(id => {
                document.getElementById(id).classList.remove('active');
            });
            if(data) {
                if(data === "INAINTE") document.getElementById('up').classList.add('active');
                if(data === "INAPOI") document.getElementById('down').classList.add('active');
                if(data === "STANGA") document.getElementById('left').classList.add('active');
                if(data === "DREAPTA") document.getElementById('right').classList.add('active');
            }
        }
        setInterval(fetchDirection, 100);
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/direction")
def get_direction():
    return current_direction

def socket_server():
    global current_direction
    PORT = 5000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", PORT))
    server.listen(1)
    print(f"Aștept conexiune pe portul {PORT}...")
    conn, addr = server.accept()
    print("Conectat la:", addr)
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            current_direction = data.decode()
    except KeyboardInterrupt:
        pass
    finally:
        conn.close()
        server.close()

# Pornim socket server într-un thread separat
threading.Thread(target=socket_server, daemon=True).start()

# Pornim serverul Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
