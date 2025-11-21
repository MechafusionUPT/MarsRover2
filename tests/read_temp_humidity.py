import os
import board
import adafruit_dht
from flask import Flask, jsonify, render_template_string


os.environ["BLINKA_FORCE"] = "1"
dht = adafruit_dht.DHT11(board.D4)
app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
    <title>Live DHT11</title>
</head>
<body>
    <h1>Live Temperature & Humidity</h1>
    <p>Temperature: <span id="temp">--</span></p>
    <p>Humidity: <span id="hum">--</span> %</p>

    <script>
        async function update() {
            try {
                const res = await fetch("/temp-umiditate");
                const data = await res.json();
                document.getElementById("temp").innerText = data.temperature;
                document.getElementById("hum").innerText = data.humidity;
            } catch(e) {
                document.getElementById("temp").innerText = "Error";
                document.getElementById("hum").innerText = "Error";
            }
        }
        setInterval(update, 2000); // update la fiecare 2 secunde
        update(); 
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/temp-umiditate")
def temp_umiditate():
    try:
        return jsonify({
            "temperature": dht.temperature,
            "humidity": dht.humidity
        })
    except RuntimeError:
        return jsonify({"temperature": "Error", "humidity": "Error"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)



