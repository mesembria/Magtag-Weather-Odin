# magtag_weather_odin
Code to display temp/weather conditions in a user friendly way on [MagTag](https://www.adafruit.com/product/4800) display. 

Based on and heavily indebted to the [MagTag Daily Weather Forecast Display](https://learn.adafruit.com/magtag-weather/). Updated to create a more useful and easy to read display for daily weather, based on the Odin display from the Carrot weather app.

To Use: 
- Update secrets.py with ssid, password, openweather_token and lat and log
- Copy code onto device. 

Uses the [Open Weather One Call API 3.0](https://openweathermap.org/api). Currently, the first 1000 calls per day are free, so for personal use, there should be no cost. But you still need to sign up for an account to get the token. 

To do:
- Updated instructions for installation
- Support multiple eInk displays
- Add location and time
- Benchmark battery life
- Add support for different time spans or displays powered by button clicks
- Support metric
- Publish as an official Adafruit Learning System Guide

### Inspiration from Carrot Weather
<figure>
  <img src="https://github.com/mesembria/magtag_weather_odin/assets/6217774/e7298e5b-3a08-4e74-806b-e9e1ef17edb7" width="600" />
</figure>

### Example screenshots

<figure>
  <img src="https://github.com/mesembria/magtag_weather_odin/assets/6217774/971df265-4eae-4ab9-b939-bd295a32a8b5" />  
</figure>


![IMG_5530](https://github.com/mesembria/magtag_weather_odin/assets/6217774/f213587d-b09b-4a84-b20b-854b044b2018)
![IMG_5532](https://github.com/mesembria/magtag_weather_odin/assets/6217774/e105ea66-8bc3-4509-9d20-08bb5a2032c1)

