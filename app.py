from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
import requests

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WX_URL = "https://api.open-meteo.com/v1/forecast"

# Map our units to Open-Meteo parameters and UI labels
UNITS = {
    "metric": {"temp": "celsius", "wind": "ms", "tlabel": "°C", "wlabel": "m/s"},
    "imperial": {"temp": "fahrenheit", "wind": "mph", "tlabel": "°F", "wlabel": "mph"},
}

class NetError(Exception):
    pass


def geocode_city(city: str):
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    try:
        r = requests.get(GEO_URL, params=params, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        raise NetError(f"Network error (geocoding): {e}")
    data = r.json() or {}
    results = data.get("results") or []
    if not results:
        raise NetError("City not found")
    top = results[0]
    return {
        "name": top.get("name", ""),
        "country": top.get("country", ""),
        "lat": top.get("latitude"),
        "lon": top.get("longitude"),
    }


def fetch(city: str, units: str = "metric"):
    city = (city or "").strip()
    if not city:
        raise ValueError("City is required")
    if units not in UNITS:
        raise ValueError("Units must be 'metric' or 'imperial'")

    loc = geocode_city(city)
    p = UNITS[units]
    params = {
        "latitude": loc["lat"],
        "longitude": loc["lon"],
        "current_weather": True,
        "temperature_unit": p["temp"],
        "windspeed_unit": p["wind"],
    }
    try:
        r = requests.get(WX_URL, params=params, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        raise NetError(f"Network error (weather): {e}")
    data = r.json() or {}
    cw = data.get("current_weather") or {}
    if not cw:
        raise NetError("No current weather available for this location")
    return {
        "name": loc["name"],
        "country": loc["country"],
        "temp": cw.get("temperature"),
        "wind": cw.get("windspeed"),
        "units": units,
        "tlabel": p["tlabel"],
        "wlabel": p["wlabel"],
    }


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Weather – Tkinter (Open‑Meteo)")
        self.geometry("420x300")
        self.minsize(420, 300)
        self.configure(padx=12, pady=12)
        self._build()

    def _build(self) -> None:
        row = ttk.Frame(self)
        row.pack(fill="x", pady=(0, 8))
        ttk.Label(row, text="City").pack(side="left")
        self.city = tk.StringVar(value="New York")
        ttk.Entry(row, textvariable=self.city, width=28).pack(side="left", padx=(6, 10))
        ttk.Label(row, text="Units").pack(side="left")
        self.units = tk.StringVar(value="metric")
        ttk.Combobox(row, textvariable=self.units, state="readonly", width=10,
                     values=("metric", "imperial")).pack(side="left", padx=(6, 10))
        self.btn = ttk.Button(row, text="Get Weather", command=self.on_get)
        self.btn.pack(side="left")

        card = ttk.LabelFrame(self, text="Current")
        card.pack(fill="both", expand=True)
        self.out_city = ttk.Label(card, font=("Segoe UI", 14, "bold"))
        self.out_city.pack(anchor="w", padx=8, pady=(8, 2))
        grid = ttk.Frame(card)
        grid.pack(fill="x", padx=8)
        self.out_temp = ttk.Label(grid, font=("Segoe UI", 32, "bold"))
        self.out_temp.grid(row=0, column=0, sticky="w", pady=(4, 8))
        sub = ttk.Frame(grid)
        sub.grid(row=0, column=1, sticky="w", padx=(16, 0))
        self.out_desc = ttk.Label(sub, text="")
        self.out_desc.pack(anchor="w")
        grid2 = ttk.Frame(card)
        grid2.pack(fill="x", padx=8, pady=(6, 10))
        self.out_hum = ttk.Label(grid2, text="")  # Open‑Meteo current doesn't expose humidity; keep for future
        self.out_hum.grid(row=0, column=0, sticky="w", padx=(0, 20))
        self.out_wind = ttk.Label(grid2)
        self.out_wind.grid(row=0, column=1, sticky="w")
        self.status = ttk.Label(self, text="Ready", anchor="w")
        self.status.pack(fill="x", pady=(8, 0))
        try:
            self.call('tk', 'scaling', 1.15)
        except tk.TclError:
            pass

    def set_busy(self, busy: bool) -> None:
        self.btn.configure(state=("disabled" if busy else "normal"))
        self.status.configure(text=("Loading..." if busy else "Ready"))

    def on_get(self) -> None:
        city = self.city.get().strip()
        units = self.units.get().strip()
        if not city:
            messagebox.showwarning("Input", "Enter a city")
            return
        self.set_busy(True)
        self.after(10, self._fetch_sync, city, units)

    def _fetch_sync(self, city: str, units: str) -> None:
        try:
            d = fetch(city, units)
        except Exception as e:
            self.set_busy(False)
            messagebox.showerror("Weather", str(e))
            return
        self.out_city.configure(text=f"{d['name']}{', ' + d['country'] if d['country'] else ''}")
        self.out_temp.configure(text=f"{d['temp']} {d['tlabel']}")
        # Open‑Meteo current endpoint doesn't include description text; omit or compute from code maps if needed
        self.out_desc.configure(text="")
        self.out_hum.configure(text="")
        self.out_wind.configure(text=f"Wind: {d['wind']} {d['wlabel']}")
        self.set_busy(False)


if __name__ == "__main__":
    App().mainloop()