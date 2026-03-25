import sqlite3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
DB_NAME = "aiotdb.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/data', methods=['POST'])
def add_data():
    data = request.json
    temperature = data.get('temperature')
    humidity = data.get('humidity')

    if temperature is None or humidity is None:
        return jsonify({"error": "Missing data"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensors (temperature, humidity)
        VALUES (?, ?)
    ''', (temperature, humidity))
    conn.commit()
    conn.close()

    return jsonify({"message": "Data inserted successfully"}), 201

@app.route('/api/data_latest', methods=['GET'])
def get_latest_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Fetch the last 60 data points for the dashboard
    cursor.execute('''
        SELECT timestamp, temperature, humidity 
        FROM sensors 
        ORDER BY id DESC LIMIT 60
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    # Reverse to make it chronological (oldest to newest)
    rows.reverse()
    
    data = [
        {"timestamp": row[0], "temperature": row[1], "humidity": row[2]}
        for row in rows
    ]
    return jsonify(data)

if __name__ == '__main__':
    init_db()
    # Run the Flask app on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
