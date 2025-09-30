import os
import cdsapi
import numpy as np
from datetime import datetime
from flask import Flask, render_template, jsonify
from netCDF4 import Dataset

# Flask uygulaması
app = Flask(__name__)

# Kaydedilecek dosya
DATA_FILE = "static/weather.nc"

# Varsayılan koordinatlar (Adem Tolunay Anadolu Lisesi)
LAT = 36.89083
LON = 30.67111


# === Yardımcı Fonksiyonlar ===

def download_weather():
    """
    Copernicus'tan ERA5 hava durumu verisini indirir.
    """
    c = cdsapi.Client()

    now = datetime.utcnow()
    year = str(now.year)
    month = f"{now.month:02d}"
    day = f"{now.day:02d}"
    hour = f"{(now.hour // 6) * 6:02d}:00"  # en yakın 6 saatlik aralık

    print(f"[INFO] {year}-{month}-{day} {hour} için veri indiriliyor...")

    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": [
                "2m_temperature",
                "2m_dewpoint_temperature",
                "total_precipitation",
                "surface_pressure",
                "10m_u_component_of_wind",
                "10m_v_component_of_wind",
            ],
            "year": year,
            "month": month,
            "day": day,
            "time": hour,
            "format": "netcdf"
        },
        DATA_FILE
    )

    print("[INFO] Veri indirildi.")


def read_weather():
    """
    İndirilen NetCDF dosyasını okuyup ortalama sıcaklık vs. döndürür.
    """
    if not os.path.exists(DATA_FILE):
        return None

    dataset = Dataset(DATA_FILE, "r")

    # Değişkenleri çek
    lats = dataset.variables["latitude"][:]
    lons = dataset.variables["longitude"][:]

    # En yakın grid noktasını bul
    lat_idx = np.abs(lats - LAT).argmin()
    lon_idx = np.abs(lons - LON).argmin()

    temp = dataset.variables["t2m"][0, lat_idx, lon_idx] - 273.15  # Kelvin -> °C
    dew = dataset.variables["d2m"][0, lat_idx, lon_idx] - 273.15
    pressure = dataset.variables["sp"][0, lat_idx, lon_idx] / 100  # Pa -> hPa
    u_wind = dataset.variables["u10"][0, lat_idx, lon_idx]
    v_wind = dataset.variables["v10"][0, lat_idx, lon_idx]
    wind_speed = np.sqrt(u_wind**2 + v_wind**2)
    rain = dataset.variables["tp"][0, lat_idx, lon_idx] * 1000  # m -> mm

    dataset.close()

    return {
        "temperature": round(float(temp), 1),
        "dew_point": round(float(dew), 1),
        "pressure": round(float(pressure), 1),
        "wind_speed": round(float(wind_speed), 1),
        "rain": round(float(rain), 1),
        "unit_temp": "°C",
        "unit_pressure": "hPa",
        "unit_wind": "m/s",
        "unit_rain": "mm",
        "location": "Adem Tolunay Anadolu Lisesi"
    }


# === ROUTES ===

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/refresh")
def refresh_data():
    try:
        download_weather()
        return jsonify({"status": "ok", "message": "Veri başarıyla indirildi!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/api/weather")
def get_weather():
    data = read_weather()
    if data is None:
        return jsonify({"status": "error", "message": "Veri yok. Önce /api/refresh çağırın."})

    return jsonify({"status": "ok", **data})


# === MAIN ===
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
