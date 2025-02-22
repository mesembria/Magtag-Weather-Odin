# MagTag Weather Odin

A CircuitPython project that displays weather information in a clean, user-friendly format on an Adafruit MagTag e-paper display. Inspired by the Odin display from the Carrot Weather app, this project provides an easy-to-read daily weather forecast that updates periodically.

## Features

- Clean, minimalist weather display
- Current temperature and weather conditions
- Battery-efficient e-paper display
- WiFi-enabled automatic updates
- Weather icon support
- CircuitPython-based for easy customization

## Hardware Requirements

- [Adafruit MagTag](https://www.adafruit.com/product/4800) - 2.9" Grayscale E-Ink WiFi Display
- USB-C cable for programming and power
- Optional: Battery (for portable use)

## Installation

1. Set up your MagTag with CircuitPython:
   - Download the latest [CircuitPython for MagTag](https://circuitpython.org/board/adafruit_magtag_2.9_grayscale/)
   - Follow the [CircuitPython installation guide](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython)

2. Install required libraries:
   - Download the [CircuitPython Library Bundle](https://circuitpython.org/libraries)
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
   - Copy all files to your MagTag's root directory
   - Update `secrets.py` with your configuration (see Configuration section)

## Configuration

Create or update `secrets.py` with the following information:
```python
secrets = {
    'ssid': 'your_wifi_ssid',
    'password': 'your_wifi_password',
    'openweather_token': 'your_api_token',
    'latitude': 'your_latitude',
    'longitude': 'your_longitude'
}
```

### API Setup
This project uses the [OpenWeather One Call API 3.0](https://openweathermap.org/api). To get an API token:
1. Create an account at [OpenWeatherMap](https://openweathermap.org/)
2. Generate an API key in your account dashboard
3. The free tier includes 1,000 calls/day, sufficient for personal use

## Future Enhancements

- [ ] Support for multiple eInk displays
- [ ] Add location and time display
- [ ] Battery life optimization and benchmarking
- [ ] Button-activated display modes
- [ ] Metric unit support
- [ ] Official Adafruit Learning System Guide

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
