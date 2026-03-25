import sqlite3
import time
import random

DB_NAME = "aiotdb.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create sensors table if it doesn't exist
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

def generate_and_insert():
    # Connect to the database inside the loop or keep connection open
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    while True:
        # Simulate DHT11 data: Temperature (0-50 °C), Humidity (20-90 %)
        temperature = round(random.uniform(15.0, 35.0), 2) # normal room temp range
        humidity = round(random.uniform(30.0, 80.0), 2)    # normal room humidity range
        
        # Insert data into the database
        cursor.execute('''
            INSERT INTO sensors (temperature, humidity)
            VALUES (?, ?)
        ''', (temperature, humidity))
        conn.commit()
        
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Inserted -> Temperature: {temperature}°C, Humidity: {humidity}%")
        
        # Wait for 2 seconds
        time.sleep(2)

if __name__ == '__main__':
    init_db()
    try:
        print("Starting DHT11 Simulator...")
        print("Data is being inserted into aiotdb.db every 2 seconds. Press Ctrl+C to stop.")
        generate_and_insert()
    except KeyboardInterrupt:
        print("\nSimulator stopped by user.")
