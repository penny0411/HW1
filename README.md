# 🌡️ IoT DHT11 Live Dashboard

This project is a real-time IoT monitoring application that simulates DHT11 sensor data (Temperature & Humidity) and displays it on a beautiful, auto-refreshing dashboard.

## 📂 Project Structure and Components

Here is a summary of all the code in this project and what each file does:

### 1. `dht11_simulator.py` (Data Generator)
This script simulates a physical DHT11 sensor. It generates random temperature (15-35°C) and humidity (30-80%) readings every 2 seconds and continuously stores them in a local SQLite database (`aiotdb.db`). 

### 2. `dashboard.py` (Streamlit Frontend)
The core frontend visualization application built with Streamlit and Plotly. It reads the real-time data from `aiotdb.db`. Features include:
- A premium **Dark Navy Theme** with custom CSS.
- **Dynamic Auto-refresh**: Uses `st.fragment` to automatically reload the data and charts every 2 seconds without the whole page flickering.
- **Metric Cards**: Shows current temperature, humidity, and calculated averages/max values.
- **Live Charts**: Interactive Plotly area/line charts for historical trends.

### 3. `server.py` & `templates/` (Flask REST API)
A lightweight Python Flask server. While Streamlit acts as the primary visual dashboard, this server provides REST API endpoints (`/api/data` and `/api/data_latest`) that allow external devices or applications to submit and retrieve sensor data programmatically. The `templates` folder contains some additional HTML files for the Flask server.

### 4. `aiotdb.db` (Database)
The SQLite database file (created automatically when you run the scripts) where all sensor data is permanently logged.

### 5. `requirements.txt`
A list of Python dependencies required to run the project.

---

## 🚀 How to Run the Project

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Data Simulator**:
   In one terminal, run the sensor simulator to start generating data:
   ```bash
   python dht11_simulator.py
   ```

3. **Start the Live Dashboard**:
   In a separate terminal, run the Streamlit dashboard:
   ```bash
   python -m streamlit run dashboard.py
   ```
   Then open `http://localhost:8501` to view your live data.
