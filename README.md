# MagTag Weather Odin

A CircuitPython project that displays an hourly weather forecast in a clean, minimalist format on an Adafruit MagTag e-paper display. Inspired by the Odin display from the Carrot Weather app, it renders 9 hourly columns showing temperature (with weather icons at relative heights), precipitation probability bars, and hour labels. After rendering, the device enters deep sleep until the next update.

## Features

- 9-column hourly forecast display (every 2 hours)
- Weather icons positioned vertically by temperature relative to day's range
- Precipitation probability bars with percentage labels (shown when >30%)
- Hour labels (e.g., `6A`, `2P`)
- Battery-efficient e-paper display with deep sleep between updates
- Smart sleep schedule: pauses 8pm–6am, updates every 2 hours otherwise
- WiFi-enabled automatic updates via Google Maps Platform Weather API

## Hardware Requirements

- [Adafruit MagTag](https://www.adafruit.com/product/4800) - 2.9" Grayscale E-Ink WiFi Display
- USB-C cable for programming and power
- Optional: Battery (for portable use)

## Installation

1. Set up your MagTag with CircuitPython:
   - Tested with **CircuitPython 9.0.4** — download from [circuitpython.org](https://circuitpython.org/board/adafruit_magtag_2.9_grayscale/)
   - Follow the [CircuitPython installation guide](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython)

2. Install required libraries:
   - Download the **CircuitPython 9.x [Library Bundle](https://circuitpython.org/libraries)**
   - Copy the following libraries to your MagTag's `lib` folder:
     - adafruit_magtag
     - adafruit_bitmap_font
     - adafruit_display_shapes
     - adafruit_imageload
     - adafruit_io
     - adafruit_minimqtt
     - neopixel.mpy
     - simpleio.mpy

3. Project files:
   - Clone this repository or download the files
   - Copy `code.py`, `bmps/`, and your populated `secrets.py` to your MagTag's root directory

## Configuration

Create or update `secrets.py` with the following:
```python
secrets = {
    'ssid': 'your_wifi_ssid',
    'password': 'your_wifi_password',
    'google_weather_key': 'your_api_key',
    'lat': '37.21350',
    'long': '-80.03739',
}
```

### API Setup
This project uses the [Google Maps Platform Weather API](https://developers.google.com/maps/documentation/weather) (powered by Google DeepMind MetNet). To get an API key:
1. Create or sign in to a [Google Cloud](https://console.cloud.google.com/) account
2. Enable the **Weather API** in the API Library
3. Create an API key under **Credentials**
4. Restrict the key to the Weather API for security

### Offline Debugging
A saved API response (`google_response.txt`) is included for testing without WiFi. In `code.py`, swap the live fetch in `get_forecast()`:
```python
# resp = magtag.network.fetch(get_data_source_url(lat, long))
resp = Fake_Requests("google_response.txt")
```

## Inspiration
This project is based on the [MagTag Daily Weather Forecast Display](https://learn.adafruit.com/magtag-weather/) and inspired by the Carrot Weather app's Odin display:


<figure>
  <img src="https://github.com/mesembria/magtag_weather_odin/assets/6217774/e7298e5b-3a08-4e74-806b-e9e1ef17edb7" width="600" />
</figure>

## Example Screenshots

<figure>
  <img src="https://github.com/mesembria/magtag_weather_odin/assets/6217774/971df265-4eae-4ab9-b939-bd295a32a8b5" />  
</figure>

![IMG_5530](https://github.com/mesembria/magtag_weather_odin/assets/6217774/f213587d-b09b-4a84-b20b-854b044b2018)
![IMG_5532](https://github.com/mesembria/magtag_weather_odin/assets/6217774/e105ea66-8bc3-4509-9d20-08bb5a2032c1)


## License

See [LICENSE](LICENSE) file for details.

