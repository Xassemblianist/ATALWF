async function loadWeather() {
  let res = await fetch("/api/weather");
  let data = await res.json();

  if (data.status === "ok") {
    document.getElementById("location").innerText = data.location;
    document.getElementById("temperature").innerText = `${data.temperature} ${data.unit_temp}`;
    document.getElementById("dew").innerText = `${data.dew_point} ${data.unit_temp}`;
    document.getElementById("wind").innerText = `${data.wind_speed} ${data.unit_wind}`;
    document.getElementById("rain").innerText = `${data.rain} ${data.unit_rain}`;
    document.getElementById("pressure").innerText = `${data.pressure} ${data.unit_pressure}`;
  } else {
    document.getElementById("location").innerText = "⚠️ " + data.message;
    document.getElementById("temperature").innerText = "-- °C";
  }
}

async function refreshWeather() {
  let res = await fetch("/api/refresh");
  let data = await res.json();
  alert(data.message);
  loadWeather();
}

document.addEventListener("DOMContentLoaded", () => {
  loadWeather();
  document.getElementById("refresh").addEventListener("click", refreshWeather);
});
