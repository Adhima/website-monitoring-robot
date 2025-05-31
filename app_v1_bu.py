from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from flask_socketio import SocketIO, emit
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Ini aktifkan CORS otomatis di semua route
app.secret_key = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'thedhimma7'
app.config['MYSQL_DB'] = 'flask_login'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
    account = cursor.fetchone()

    if account:
        session['loggedin'] = True
        session['id'] = account['id']
        session['username'] = account['username']
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error="Username atau password salah!", username=username)

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html', username=session["username"])
    return redirect(url_for('home'))

@app.route('/data')
def data():
    if 'loggedin' not in session:
        return redirect(url_for('home'))
    
    kategori_data = {
        'anomali': [],
        'penambat': [],
        'bantalan': [],
        'kemiringan': []
    }
    return render_template("data.html", kategori_data=kategori_data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
'''
@app.route('/human')
def human_feed():
    def generate():
        while True:
            frame = get_latest_frame()
            if frame is None:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
'''
# ==== STATUS VARIABEL ====
lamp_status = False
motor_status = False
motor_direction = "none"  # forward, reverse, none
motor_target_speed = 0
motor_current_speed = 0
manual_brake_status = False
esp_connected = False

# ==== ENDPOINT LAMPU ====
@app.route('/lamp', methods=['POST'])
def lamp_control():
    global lamp_status
    lamp_status = request.json.get("lamp", False)
    return jsonify({"status": "ok"})

@app.route('/lamp_status')
def lamp_status_api():
    return jsonify({"lamp": lamp_status})

# ==== ENDPOINT TEMPERATURE ====
temperature_data = {"temperature": 0.0}

@app.route("/update_temperature", methods=["POST"])
def update_temperature():
    global temperature_data
    data = request.get_json()
    temperature_data["temperature"] = data.get("temperature", 0.0)
    return jsonify({"status": "ok"})

@app.route("/temperature_data")
def get_temperature():
    return jsonify(temperature_data)


# ==== ENDPOINT MOTOR ====
@app.route('/motor', methods=['POST'])
def motor_control():
    global motor_status
    motor_status = request.json.get("motor", False)
    if not motor_status:
        # Reset jika dimatikan
        set_motor_direction("none")
        set_motor_speed(0)
    return jsonify({"status": "ok"})

@app.route('/motor_status')
def motor_status_api():
    global motor_status, esp_connected
    esp_connected = True  # Setiap kali ESP32 akses, dianggap connected
    return jsonify({"motor": motor_status})

@app.route('/motor_speed', methods=['POST'])
def motor_speed_post():
    global motor_target_speed
    motor_target_speed = request.json.get("speed", 0)
    return jsonify({"status": "ok"})

@app.route('/motor_speed_status')
def motor_speed_status_api():
    return jsonify({"speed": motor_target_speed})

# ==== ENDPOINT ARAH MOTOR ====
@app.route('/motor_direction', methods=['POST'])
def motor_direction_post():
    global motor_direction
    motor_direction = request.json.get("direction", "none")
    return jsonify({"status": "ok"})

@app.route('/motor_direction_status')
def motor_direction_status():
    return jsonify({"direction": motor_direction})

def set_motor_direction(direction):
    global motor_direction
    motor_direction = direction

def set_motor_speed(speed):
    global motor_target_speed
    motor_target_speed = speed

# ==== UPDATE KECEPATAN DARI ARDUINO ====
@app.route("/speed", methods=["POST"])
def receive_speed():
    global motor_current_speed
    speed = request.json.get("speed", 0)
    motor_current_speed = speed
    socketio.emit("speed_update", {"speed": speed})
    return jsonify({"status": "ok"})

@app.route('/current_speed')
def current_speed():
    return jsonify({"speed": motor_current_speed})

# ==== UPDATE STATUS REM MANUAL ====
@app.route('/manual_brake', methods=['POST'])
def manual_brake_control():
    global manual_brake_status
    manual_brake_status = request.json.get("manual_brake", False)
    return jsonify({"status": "ok"})

@app.route('/manual_brake_status')
def manual_brake_status_api():
    return jsonify({"manual_brake": manual_brake_status})

# ==== UPDATE STATUS ESP ====
@app.route('/esp_status')
def esp_status():
    global esp_connected
    return jsonify({"connected": esp_connected})

# ==== SOCKETIO PING ====
@app.route('/ping')
def ping():
    return jsonify({"pong": True})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
