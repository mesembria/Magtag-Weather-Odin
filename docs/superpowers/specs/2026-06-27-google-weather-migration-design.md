# Google Weather API Migration Design

**Date:** 2026-06-27
**Status:** Approved

## Overview

Replace the OpenWeather One Call API 3.0 with the Google Maps Platform Weather API (powered by Google DeepMind's MetNet model) for improved hyperlocal accuracy, especially for short-range precipitation timing. No hardware changes. No changes to the BMP sprite sheet.

## Goals

- Swap the data source from OpenWeather to Google Weather
- Remap weather condition codes to the existing 12-tile sprite sheet
- Preserve all existing display logic unchanged

## Non-Goals

- Modifying the BMP sprite sheet
- Adding new display features
- Changing the sleep schedule or display layout

---

## API

**Endpoint:**
```
GET https://weather.googleapis.com/v1/forecast/hours:lookup
  ?location.latitude={lat}
  &location.longitude={lng}
  &hours=24
  &key={google_weather_key}
```

**Auth:** API key in query string (same pattern as current setup). Key stored in `secrets.py` under `google_weather_key`.

**Key response fields per hour (`forecastHours[]`):**

| Field path | Type | Notes |
|---|---|---|
| `displayDateTime.hours` | int | Local hour (0–23), no offset math needed |
| `isDaytime` | bool | Used to pick day vs night tile for clear/partly-cloudy |
| `temperature.degrees` | float | Celsius — must convert to °F |
| `weatherCondition.type` | string | Enum, e.g. `"CLEAR"`, `"RAIN_SHOWERS"` |
| `precipitation.probability.percent` | int | 0–100 — divide by 100 for existing display logic |

---

## Icon Mapping

The existing `weather_icons_20px.bmp` is a 60×80px, 4-colour grayscale sprite sheet — 3 columns × 4 rows of 20×20 tiles. No changes to the file.

### Tile index reference

| Tile | Description |
|---|---|
| 0 | Sunny / clear day |
| 1 | Partly cloudy day |
| 2 | Mostly cloudy |
| 3 | Overcast |
| 4 | Heavy rain / rain showers |
| 5 | Light rain |
| 6 | Thunderstorm |
| 7 | Snow |
| 8 | Fog/mist (unused — no fog enum in Google API) |
| 9 | Clear night |
| 10 | Partly cloudy night |
| 11 | Wind |

### Google condition type → tile

Day/night variants (CLEAR, MOSTLY_CLEAR, PARTLY_CLOUDY) select tile based on `isDaytime`; all other conditions use the same tile regardless of time of day.

```python
ICON_MAP = {
    # Clear
    "CLEAR":             (0, 9),   # (day_tile, night_tile)
    "MOSTLY_CLEAR":      (0, 9),

    # Partly cloudy
    "PARTLY_CLOUDY":     (1, 10),

    # Cloudy
    "MOSTLY_CLOUDY":     2,
    "CLOUDY":            3,

    # Wind
    "WINDY":             11,
    "WIND_AND_RAIN":     4,

    # Light rain (tile 5)
    "LIGHT_RAIN":              5,
    "LIGHT_RAIN_SHOWERS":      5,
    "CHANCE_OF_SHOWERS":       5,
    "SCATTERED_SHOWERS":       5,
    "LIGHT_TO_MODERATE_RAIN":  5,

    # Heavy rain (tile 4)
    "RAIN_SHOWERS":            4,
    "HEAVY_RAIN_SHOWERS":      4,
    "RAIN":                    4,
    "MODERATE_TO_HEAVY_RAIN":  4,
    "HEAVY_RAIN":              4,
    "RAIN_PERIODICALLY_HEAVY": 4,

    # Thunderstorm / hail (hail falls back to thunderstorm)
    "THUNDERSTORM":             6,
    "THUNDERSHOWER":            6,
    "LIGHT_THUNDERSTORM_RAIN":  6,
    "SCATTERED_THUNDERSTORMS":  6,
    "HEAVY_THUNDERSTORM":       6,
    "HAIL":                     6,
    "HAIL_SHOWERS":             6,

    # Snow (all variants → same tile)
    "LIGHT_SNOW_SHOWERS":       7,
    "CHANCE_OF_SNOW_SHOWERS":   7,
    "SCATTERED_SNOW_SHOWERS":   7,
    "SNOW_SHOWERS":             7,
    "HEAVY_SNOW_SHOWERS":       7,
    "LIGHT_TO_MODERATE_SNOW":   7,
    "MODERATE_TO_HEAVY_SNOW":   7,
    "SNOW":                     7,
    "LIGHT_SNOW":               7,
    "HEAVY_SNOW":               7,
    "SNOWSTORM":                7,
    "SNOW_PERIODICALLY_HEAVY":  7,
    "HEAVY_SNOW_STORM":         7,
    "BLOWING_SNOW":             7,
    "RAIN_AND_SNOW":            7,

    # Fallback
    "TYPE_UNSPECIFIED":         0,
}
```

---

## Code Changes (all in `code.py`)

### 1. `ICON_MAP` — full replacement

Replace the 11-entry OpenWeather dict with the mapping above.

### 2. `get_icon(condition_type, is_daytime)` — simplify signature and logic

Old: matched on 2-char prefix + wildcard suffix.
New: plain dict lookup; tuples indicate day/night split.

```python
def get_icon(condition_type, is_daytime):
    entry = ICON_MAP.get(condition_type, 0)
    if isinstance(entry, tuple):
        return entry[0] if is_daytime else entry[1]
    return entry
```

### 3. `get_data_source_url(lat, lng)` — new URL

```python
def get_data_source_url(lat, lng):
    return (
        "https://weather.googleapis.com/v1/forecast/hours:lookup"
        f"?location.latitude={lat}&location.longitude={lng}"
        f"&hours=24&key={secrets['google_weather_key']}"
    )
```

### 4. `parse_iso_to_epoch(s)` — new helper

Google timestamps are ISO 8601 strings (`"2026-06-27T14:00:00Z"`). CircuitPython has no `datetime.fromisoformat()`, but the format is fixed so we parse manually:

```python
def parse_iso_to_epoch(s):
    # s = "YYYY-MM-DDTHH:MM:SSZ"
    return int(time.mktime(time.struct_time((
        int(s[0:4]), int(s[5:7]), int(s[8:10]),
        int(s[11:13]), int(s[14:16]), int(s[17:19]),
        0, -1, -1
    ))))
```

### 5. `get_forecast(lat, long)` — parse new response shape

Old returned: `json["hourly"]`, `json["current"]["dt"]`, `json["timezone_offset"]`
New returns: `json["forecastHours"]`, local epoch for sleep calc (UTC + tz offset).

`displayDateTime.utcOffset` is a string like `"-14400s"`. Parse it to integer seconds and add to the UTC epoch so `go_to_sleep()` receives a local-time epoch, exactly as before.

```python
def get_forecast(lat, long):
    resp = magtag.network.fetch(get_data_source_url(lat=lat, long=long))
    json_data = resp.json()
    hours = json_data["forecastHours"]
    utc_epoch = parse_iso_to_epoch(hours[0]["interval"]["startTime"])
    tz_offset = int(hours[0]["displayDateTime"]["utcOffset"].rstrip("s"))
    return hours, utc_epoch + tz_offset
```

### 6. `format_forcast_data(forecast_data)` — new field paths, C→F, pop scaling

Signature drops `local_tz_offset` (no longer needed — `displayDateTime.hours` is already local).

```python
def format_forcast_data(forecast_data):
    hour_list = []
    for hour_obj in forecast_data:
        hr = {}
        hr["hour"] = hour_obj["displayDateTime"]["hours"]
        hr["temp"] = hour_obj["temperature"]["degrees"] * 9 / 5 + 32
        hr["icon"] = hour_obj["weatherCondition"]["type"]
        hr["is_daytime"] = hour_obj["isDaytime"]
        hr["pop"]  = hour_obj["precipitation"]["probability"]["percent"] / 100
        hour_list.append(hr)
    return hour_list
```

### 7. `build_temp_group()` — pass `is_daytime` into `get_icon()`

```python
icon_index = get_icon(hour_list[hour_index]["icon"], hour_list[hour_index]["is_daytime"])
```

### 8. Main section — update call sites

```python
# Old:
forecast_data, utc_time, local_tz_offset = get_forecast(lat, long)
hour_list = format_forcast_data(forecast_data, local_tz_offset)
go_to_sleep(utc_time + local_tz_offset)

# New:
forecast_data, local_time = get_forecast(lat, long)
hour_list = format_forcast_data(forecast_data)
go_to_sleep(local_time)
```

### 9. `secrets.py` — rename key

```python
secrets = {
    ...
    "google_weather_key": "YOUR_KEY_HERE",  # replaces openweather_token
    ...
}
```

---

## Offline Testing

`response.txt` contains the current OpenWeather response. A new `google_response.txt` should be saved from a real API call (or manually crafted) for offline testing with `Fake_Requests`.

---

## Summary of Changed Files

| File | Change |
|---|---|
| `code.py` | ICON_MAP, get_icon(), get_data_source_url(), get_forecast(), format_forcast_data(), build_temp_group() call site |
| `secrets.py` | Rename `openweather_token` → `google_weather_key` |
| `response.txt` | Replace with Google API sample response (for offline testing) |
| `bmps/weather_icons_20px.bmp` | No change |
