# Google Weather API Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the OpenWeather One Call API with the Google Maps Platform Weather API in `code.py`, remapping condition type enums to the existing 12-tile sprite sheet.

**Architecture:** All changes are confined to `code.py` (API URL, response parsing, icon mapping) and `secrets.py` (key rename). The BMP sprite sheet is untouched. Offline testing uses `Fake_Requests` with a saved `google_response.txt`. Because this runs on CircuitPython (no pytest), logic-only functions are verified with `python3` on the desktop; full display integration is verified on-device with offline mode.

**Tech Stack:** CircuitPython 9.x, `adafruit_magtag`, `adafruit_fakerequests`, Google Maps Platform Weather API v1

---

## File Map

| File | Change |
|---|---|
| `code.py` | All logic changes — ICON_MAP, 3 replaced functions, 1 new helper, 2 updated call sites |
| `secrets.py` | Rename `openweather_token` → `google_weather_key` |
| `google_response.txt` | New — saved Google API sample response for offline testing |
| `response.txt` | Keep unchanged (old OpenWeather reference) |

---

### Task 1: Create `google_response.txt` for offline testing

**Files:**
- Create: `google_response.txt`

This file lets you test all parsing changes without WiFi or burning API quota. It must have ≥17 hours (the display reads indices 0,2,4,…,16).

- [ ] **Step 1: Create `google_response.txt`**

Create the file at the project root with this content (24 hours, realistic Virginia summer data, UTC-4 offset):

```json
{
  "forecastHours": [
    {"interval":{"startTime":"2026-06-27T14:00:00Z","endTime":"2026-06-27T15:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":10,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"PARTLY_CLOUDY","description":"Partly Cloudy","iconBaseUri":"https://maps.gstatic.com/weather/v1/partly_cloudy"},"temperature":{"degrees":24.5,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":25.0,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":20,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":65,"uvIndex":6,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-27T15:00:00Z","endTime":"2026-06-27T16:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":11,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"MOSTLY_CLOUDY","description":"Mostly Cloudy","iconBaseUri":"https://maps.gstatic.com/weather/v1/mostly_cloudy"},"temperature":{"degrees":26.1,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":27.0,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":30,"type":"RAIN"},"qpf":{"quantity":0.1,"unit":"MILLIMETERS"}},"relativeHumidity":68,"uvIndex":7,"thunderstormProbability":5},
    {"interval":{"startTime":"2026-06-27T16:00:00Z","endTime":"2026-06-27T17:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":12,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"SCATTERED_SHOWERS","description":"Scattered Showers","iconBaseUri":"https://maps.gstatic.com/weather/v1/scattered_showers"},"temperature":{"degrees":27.2,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":28.5,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":55,"type":"RAIN"},"qpf":{"quantity":2.5,"unit":"MILLIMETERS"}},"relativeHumidity":72,"uvIndex":5,"thunderstormProbability":10},
    {"interval":{"startTime":"2026-06-27T17:00:00Z","endTime":"2026-06-27T18:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":13,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"RAIN_SHOWERS","description":"Rain Showers","iconBaseUri":"https://maps.gstatic.com/weather/v1/rain_showers"},"temperature":{"degrees":25.8,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":26.0,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":75,"type":"RAIN"},"qpf":{"quantity":5.0,"unit":"MILLIMETERS"}},"relativeHumidity":80,"uvIndex":3,"thunderstormProbability":20},
    {"interval":{"startTime":"2026-06-27T18:00:00Z","endTime":"2026-06-27T19:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":14,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"THUNDERSTORM","description":"Thunderstorm","iconBaseUri":"https://maps.gstatic.com/weather/v1/thunderstorm"},"temperature":{"degrees":23.3,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":23.0,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":90,"type":"RAIN"},"qpf":{"quantity":10.0,"unit":"MILLIMETERS"}},"relativeHumidity":88,"uvIndex":1,"thunderstormProbability":65},
    {"interval":{"startTime":"2026-06-27T19:00:00Z","endTime":"2026-06-27T20:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":15,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"HEAVY_RAIN","description":"Heavy Rain","iconBaseUri":"https://maps.gstatic.com/weather/v1/heavy_rain"},"temperature":{"degrees":22.0,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":21.5,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":85,"type":"RAIN"},"qpf":{"quantity":8.0,"unit":"MILLIMETERS"}},"relativeHumidity":90,"uvIndex":1,"thunderstormProbability":30},
    {"interval":{"startTime":"2026-06-27T20:00:00Z","endTime":"2026-06-27T21:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":16,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"LIGHT_RAIN","description":"Light Rain","iconBaseUri":"https://maps.gstatic.com/weather/v1/light_rain"},"temperature":{"degrees":21.5,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":21.0,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":60,"type":"RAIN"},"qpf":{"quantity":3.0,"unit":"MILLIMETERS"}},"relativeHumidity":85,"uvIndex":2,"thunderstormProbability":5},
    {"interval":{"startTime":"2026-06-27T21:00:00Z","endTime":"2026-06-27T22:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":17,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"CLOUDY","description":"Cloudy","iconBaseUri":"https://maps.gstatic.com/weather/v1/cloudy"},"temperature":{"degrees":21.0,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":20.5,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":25,"type":"RAIN"},"qpf":{"quantity":0.5,"unit":"MILLIMETERS"}},"relativeHumidity":78,"uvIndex":3,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-27T22:00:00Z","endTime":"2026-06-27T23:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":18,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"MOSTLY_CLOUDY","description":"Mostly Cloudy","iconBaseUri":"https://maps.gstatic.com/weather/v1/mostly_cloudy"},"temperature":{"degrees":20.8,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":20.5,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":15,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":75,"uvIndex":2,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-27T23:00:00Z","endTime":"2026-06-28T00:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":19,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"PARTLY_CLOUDY","description":"Partly Cloudy","iconBaseUri":"https://maps.gstatic.com/weather/v1/partly_cloudy"},"temperature":{"degrees":19.5,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":19.0,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":10,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":70,"uvIndex":1,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T00:00:00Z","endTime":"2026-06-28T01:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":20,"minutes":0,"utcOffset":"-14400s"},"isDaytime":false,"weatherCondition":{"type":"CLEAR","description":"Clear","iconBaseUri":"https://maps.gstatic.com/weather/v1/clear"},"temperature":{"degrees":18.0,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":17.5,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":5,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":68,"uvIndex":0,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T01:00:00Z","endTime":"2026-06-28T02:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":21,"minutes":0,"utcOffset":"-14400s"},"isDaytime":false,"weatherCondition":{"type":"MOSTLY_CLEAR","description":"Mostly Clear","iconBaseUri":"https://maps.gstatic.com/weather/v1/mostly_clear"},"temperature":{"degrees":17.2,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":16.8,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":5,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":65,"uvIndex":0,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T02:00:00Z","endTime":"2026-06-28T03:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":22,"minutes":0,"utcOffset":"-14400s"},"isDaytime":false,"weatherCondition":{"type":"CLEAR","description":"Clear","iconBaseUri":"https://maps.gstatic.com/weather/v1/clear"},"temperature":{"degrees":16.5,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":16.0,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":0,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":63,"uvIndex":0,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T03:00:00Z","endTime":"2026-06-28T04:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":27,"hours":23,"minutes":0,"utcOffset":"-14400s"},"isDaytime":false,"weatherCondition":{"type":"CLEAR","description":"Clear","iconBaseUri":"https://maps.gstatic.com/weather/v1/clear"},"temperature":{"degrees":15.8,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":15.5,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":0,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":61,"uvIndex":0,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T04:00:00Z","endTime":"2026-06-28T05:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":28,"hours":0,"minutes":0,"utcOffset":"-14400s"},"isDaytime":false,"weatherCondition":{"type":"MOSTLY_CLEAR","description":"Mostly Clear","iconBaseUri":"https://maps.gstatic.com/weather/v1/mostly_clear"},"temperature":{"degrees":15.0,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":14.5,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":0,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":60,"uvIndex":0,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T05:00:00Z","endTime":"2026-06-28T06:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":28,"hours":1,"minutes":0,"utcOffset":"-14400s"},"isDaytime":false,"weatherCondition":{"type":"CLEAR","description":"Clear","iconBaseUri":"https://maps.gstatic.com/weather/v1/clear"},"temperature":{"degrees":14.5,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":14.0,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":0,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":59,"uvIndex":0,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T06:00:00Z","endTime":"2026-06-28T07:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":28,"hours":2,"minutes":0,"utcOffset":"-14400s"},"isDaytime":false,"weatherCondition":{"type":"WINDY","description":"Windy","iconBaseUri":"https://maps.gstatic.com/weather/v1/windy"},"temperature":{"degrees":14.2,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":13.0,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":0,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":58,"uvIndex":0,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T07:00:00Z","endTime":"2026-06-28T08:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":28,"hours":3,"minutes":0,"utcOffset":"-14400s"},"isDaytime":false,"weatherCondition":{"type":"PARTLY_CLOUDY","description":"Partly Cloudy","iconBaseUri":"https://maps.gstatic.com/weather/v1/partly_cloudy"},"temperature":{"degrees":14.0,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":13.5,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":5,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":60,"uvIndex":0,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T08:00:00Z","endTime":"2026-06-28T09:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":28,"hours":4,"minutes":0,"utcOffset":"-14400s"},"isDaytime":false,"weatherCondition":{"type":"CLEAR","description":"Clear","iconBaseUri":"https://maps.gstatic.com/weather/v1/clear"},"temperature":{"degrees":13.8,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":13.2,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":0,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":58,"uvIndex":0,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T09:00:00Z","endTime":"2026-06-28T10:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":28,"hours":5,"minutes":0,"utcOffset":"-14400s"},"isDaytime":false,"weatherCondition":{"type":"CLEAR","description":"Clear","iconBaseUri":"https://maps.gstatic.com/weather/v1/clear"},"temperature":{"degrees":13.5,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":13.0,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":0,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":57,"uvIndex":0,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T10:00:00Z","endTime":"2026-06-28T11:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":28,"hours":6,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"CLEAR","description":"Sunny","iconBaseUri":"https://maps.gstatic.com/weather/v1/clear"},"temperature":{"degrees":15.0,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":14.5,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":0,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":55,"uvIndex":1,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T11:00:00Z","endTime":"2026-06-28T12:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":28,"hours":7,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"MOSTLY_CLEAR","description":"Mostly Clear","iconBaseUri":"https://maps.gstatic.com/weather/v1/mostly_clear"},"temperature":{"degrees":17.5,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":17.0,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":0,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":52,"uvIndex":3,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T12:00:00Z","endTime":"2026-06-28T13:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":28,"hours":8,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"PARTLY_CLOUDY","description":"Partly Cloudy","iconBaseUri":"https://maps.gstatic.com/weather/v1/partly_cloudy"},"temperature":{"degrees":20.0,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":20.5,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":10,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":50,"uvIndex":5,"thunderstormProbability":0},
    {"interval":{"startTime":"2026-06-28T13:00:00Z","endTime":"2026-06-28T14:00:00Z"},"displayDateTime":{"year":2026,"month":6,"day":28,"hours":9,"minutes":0,"utcOffset":"-14400s"},"isDaytime":true,"weatherCondition":{"type":"CLEAR","description":"Sunny","iconBaseUri":"https://maps.gstatic.com/weather/v1/clear"},"temperature":{"degrees":22.2,"unit":"CELSIUS"},"feelsLikeTemperature":{"degrees":23.0,"unit":"CELSIUS"},"precipitation":{"probability":{"percent":5,"type":"RAIN"},"qpf":{"quantity":0.0,"unit":"MILLIMETERS"}},"relativeHumidity":48,"uvIndex":7,"thunderstormProbability":0}
  ]
}
```

- [ ] **Step 2: Verify the JSON is valid**

```bash
python3 -c "import json; d=json.load(open('google_response.txt')); print(len(d['forecastHours']), 'hours')"
```

Expected output: `24 hours`

- [ ] **Step 3: Commit**

```bash
git add google_response.txt
git commit -m "Add Google Weather API sample response for offline testing"
```

---

### Task 2: Update `secrets.py`

**Files:**
- Modify: `secrets.py`

- [ ] **Step 1: Rename the API key field**

In `secrets.py`, replace:
```python
'openweather_token': '...',
```
with:
```python
'google_weather_key': 'YOUR_GOOGLE_WEATHER_KEY_HERE',
```

- [ ] **Step 2: Verify the key is present**

```bash
python3 -c "from secrets import secrets; print('key present:', 'google_weather_key' in secrets)"
```

Expected: `key present: True`

- [ ] **Step 3: Commit**

```bash
git add secrets.py
git commit -m "Rename API key field to google_weather_key"
```

---

### Task 3: Replace `ICON_MAP` and `get_icon()`

**Files:**
- Modify: `code.py` (lines 21, 31–50)

- [ ] **Step 1: Replace `ICON_MAP` at the top of `code.py`**

Replace:
```python
ICON_MAP = {"01d": 0, "01n": 9, "02d": 1, "02n": 10, "03X": 2, "04X": 3, "09X": 4, "10X": 5, "11X": 6, "13X": 7, "50X": 8}
```

With:
```python
ICON_MAP = {
    "CLEAR":                    (0, 9),
    "MOSTLY_CLEAR":             (0, 9),
    "PARTLY_CLOUDY":            (1, 10),
    "MOSTLY_CLOUDY":            2,
    "CLOUDY":                   3,
    "WINDY":                    11,
    "WIND_AND_RAIN":            4,
    "LIGHT_RAIN":               5,
    "LIGHT_RAIN_SHOWERS":       5,
    "CHANCE_OF_SHOWERS":        5,
    "SCATTERED_SHOWERS":        5,
    "LIGHT_TO_MODERATE_RAIN":   5,
    "RAIN_SHOWERS":             4,
    "HEAVY_RAIN_SHOWERS":       4,
    "RAIN":                     4,
    "MODERATE_TO_HEAVY_RAIN":   4,
    "HEAVY_RAIN":               4,
    "RAIN_PERIODICALLY_HEAVY":  4,
    "THUNDERSTORM":             6,
    "THUNDERSHOWER":            6,
    "LIGHT_THUNDERSTORM_RAIN":  6,
    "SCATTERED_THUNDERSTORMS":  6,
    "HEAVY_THUNDERSTORM":       6,
    "HAIL":                     6,
    "HAIL_SHOWERS":             6,
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
    "TYPE_UNSPECIFIED":         0,
}
```

- [ ] **Step 2: Replace `get_icon()` function**

Replace the entire `get_icon()` function (currently lines 31–50) with:

```python
def get_icon(condition_type, is_daytime):
    entry = ICON_MAP.get(condition_type, 0)
    if isinstance(entry, tuple):
        return entry[0] if is_daytime else entry[1]
    return entry
```

- [ ] **Step 3: Verify the logic on the desktop**

```bash
python3 -c "
ICON_MAP = {
    'CLEAR': (0,9), 'MOSTLY_CLEAR': (0,9),
    'PARTLY_CLOUDY': (1,10),
    'MOSTLY_CLOUDY': 2, 'CLOUDY': 3, 'WINDY': 11,
    'RAIN_SHOWERS': 4, 'LIGHT_RAIN': 5,
    'THUNDERSTORM': 6, 'SNOW': 7, 'TYPE_UNSPECIFIED': 0,
}
def get_icon(t, d):
    e = ICON_MAP.get(t, 0)
    return (e[0] if d else e[1]) if isinstance(e, tuple) else e

assert get_icon('CLEAR', True)  == 0,  'CLEAR day should be tile 0'
assert get_icon('CLEAR', False) == 9,  'CLEAR night should be tile 9'
assert get_icon('PARTLY_CLOUDY', True)  == 1,  'PARTLY_CLOUDY day -> 1'
assert get_icon('PARTLY_CLOUDY', False) == 10, 'PARTLY_CLOUDY night -> 10'
assert get_icon('WINDY', True)  == 11, 'WINDY -> 11'
assert get_icon('RAIN_SHOWERS', True) == 4, 'heavy rain -> 4'
assert get_icon('LIGHT_RAIN', True)   == 5, 'light rain -> 5'
assert get_icon('THUNDERSTORM', True) == 6, 'thunder -> 6'
assert get_icon('SNOW', True)         == 7, 'snow -> 7'
assert get_icon('UNKNOWN_FUTURE_TYPE', True) == 0, 'unknown -> fallback 0'
print('All assertions passed')
"
```

Expected: `All assertions passed`

- [ ] **Step 4: Commit**

```bash
git add code.py
git commit -m "Replace ICON_MAP and get_icon() for Google Weather condition types"
```

---

### Task 4: Add `parse_iso_to_epoch()` helper and replace `get_data_source_url()`

**Files:**
- Modify: `code.py` (after imports, before `get_forecast`)

- [ ] **Step 1: Add `parse_iso_to_epoch()` after the `ICON_MAP` block**

```python
def parse_iso_to_epoch(s):
    # s = "YYYY-MM-DDTHH:MM:SSZ"
    return int(time.mktime(time.struct_time((
        int(s[0:4]), int(s[5:7]), int(s[8:10]),
        int(s[11:13]), int(s[14:16]), int(s[17:19]),
        0, -1, -1
    ))))
```

- [ ] **Step 2: Replace `get_data_source_url()`**

Replace the entire `get_data_source_url()` function with:

```python
def get_data_source_url(lat, lng):
    return (
        "https://weather.googleapis.com/v1/forecast/hours:lookup"
        "?location.latitude={}&location.longitude={}"
        "&hours=24&key={}".format(lat, lng, secrets["google_weather_key"])
    )
```

Note: f-strings are not available in all CircuitPython versions — use `.format()`.

- [ ] **Step 3: Verify `parse_iso_to_epoch` on the desktop**

```bash
python3 -c "
import time
def parse_iso_to_epoch(s):
    return int(time.mktime(time.struct_time((
        int(s[0:4]), int(s[5:7]), int(s[8:10]),
        int(s[11:13]), int(s[14:16]), int(s[17:19]),
        0, -1, -1
    ))))
result = parse_iso_to_epoch('2026-06-27T14:00:00Z')
print('Epoch:', result)
# Sanity check: should be a large positive integer (Unix timestamp ~1.75 billion range)
assert result > 1_700_000_000, 'Epoch should be a valid 2026 timestamp'
print('OK')
"
```

Expected: prints a large Unix timestamp and `OK`

- [ ] **Step 4: Commit**

```bash
git add code.py
git commit -m "Add parse_iso_to_epoch() helper and replace get_data_source_url() for Google API"
```

---

### Task 5: Replace `get_forecast()` and `format_forcast_data()`

**Files:**
- Modify: `code.py`

- [ ] **Step 1: Replace `get_forecast()`**

Replace the entire `get_forecast()` function with:

```python
def get_forecast(lat, long):
    """Fetch hourly forecast from Google Weather API."""
    resp = magtag.network.fetch(get_data_source_url(lat=lat, long=long))
    #resp = Fake_Requests("google_response.txt")
    json_data = resp.json()
    hours = json_data["forecastHours"]
    utc_epoch = parse_iso_to_epoch(hours[0]["interval"]["startTime"])
    tz_offset = int(hours[0]["displayDateTime"]["utcOffset"].rstrip("s"))
    return hours, utc_epoch + tz_offset
```

- [ ] **Step 2: Replace `format_forcast_data()`**

Replace the entire `format_forcast_data()` function with:

```python
def format_forcast_data(forecast_data):
    """Format Google Weather API hourly data into display-ready dicts."""
    hour_list = []
    for hour_obj in forecast_data:
        hr = {}
        hr["hour"] = hour_obj["displayDateTime"]["hours"]
        hr["temp"] = hour_obj["temperature"]["degrees"] * 9 / 5 + 32
        hr["icon"] = hour_obj["weatherCondition"]["type"]
        hr["is_daytime"] = hour_obj["isDaytime"]
        hr["pop"] = hour_obj["precipitation"]["probability"]["percent"] / 100
        hour_list.append(hr)
    return hour_list
```

- [ ] **Step 3: Verify `format_forcast_data` output on the desktop**

```bash
python3 -c "
import json

def format_forcast_data(forecast_data):
    hour_list = []
    for hour_obj in forecast_data:
        hr = {}
        hr['hour'] = hour_obj['displayDateTime']['hours']
        hr['temp'] = hour_obj['temperature']['degrees'] * 9 / 5 + 32
        hr['icon'] = hour_obj['weatherCondition']['type']
        hr['is_daytime'] = hour_obj['isDaytime']
        hr['pop'] = hour_obj['precipitation']['probability']['percent'] / 100
        hour_list.append(hr)
    return hour_list

data = json.load(open('google_response.txt'))
hours = format_forcast_data(data['forecastHours'])

# Check first hour
h = hours[0]
assert h['hour'] == 10,          'hour should be local 10am'
assert 75 < h['temp'] < 77,      'C 24.5 -> F ~76.1'
assert h['icon'] == 'PARTLY_CLOUDY'
assert h['is_daytime'] == True
assert h['pop'] == 0.20,         'percent 20 -> 0.20'

# Check a night hour (index 10, hour 20:00 local)
n = hours[10]
assert n['is_daytime'] == False, 'hour 20 should be nighttime'

print('hour:', h['hour'], '  temp F:', round(h['temp'], 1), '  pop:', h['pop'])
print('All assertions passed')
"
```

Expected:
```
hour: 10   temp F: 76.1   pop: 0.2
All assertions passed
```

- [ ] **Step 4: Commit**

```bash
git add code.py
git commit -m "Replace get_forecast() and format_forcast_data() for Google Weather API"
```

---

### Task 6: Update `build_temp_group()` call site and main section

**Files:**
- Modify: `code.py`

- [ ] **Step 1: Update `get_icon()` call inside `build_temp_group()`**

Find this line inside `build_temp_group()`:
```python
icon_index = get_icon(hour_list[hour_index]["icon"])
```

Replace with:
```python
icon_index = get_icon(hour_list[hour_index]["icon"], hour_list[hour_index]["is_daytime"])
```

- [ ] **Step 2: Update the main section call sites**

Find in the main section (`# M A I N`):
```python
forecast_data, utc_time, local_tz_offset = get_forecast(lat, long)

hour_list = format_forcast_data(forecast_data, local_tz_offset)
```

Replace with:
```python
forecast_data, local_time = get_forecast(lat, long)

hour_list = format_forcast_data(forecast_data)
```

Find at the end of the main section:
```python
go_to_sleep(utc_time + local_tz_offset)
```

Replace with:
```python
go_to_sleep(local_time)
```

- [ ] **Step 3: Commit**

```bash
git add code.py
git commit -m "Update build_temp_group() and main section call sites"
```

---

### Task 7: Offline test on device

**Files:**
- Modify: `code.py` (temporarily enable offline mode)

- [ ] **Step 1: Enable offline mode in `get_forecast()`**

In `get_forecast()`, comment out the live fetch and enable `Fake_Requests`:

```python
def get_forecast(lat, long):
    """Fetch hourly forecast from Google Weather API."""
    #resp = magtag.network.fetch(get_data_source_url(lat=lat, long=long))
    resp = Fake_Requests("google_response.txt")
    json_data = resp.json()
    hours = json_data["forecastHours"]
    utc_epoch = parse_iso_to_epoch(hours[0]["interval"]["startTime"])
    tz_offset = int(hours[0]["displayDateTime"]["utcOffset"].rstrip("s"))
    return hours, utc_epoch + tz_offset
```

- [ ] **Step 2: Copy files to the MagTag**

Copy to `CIRCUITPY/` drive:
- `code.py`
- `google_response.txt`
- `secrets.py`

- [ ] **Step 3: Observe the serial console**

Open a serial monitor (e.g., `screen /dev/tty.usbmodem* 115200` or use Mu editor). Expected output:

```
Fetching forecast...
Refreshing...
Sleeping for X hours, Y minutes
```

No tracebacks. The display should show 9 columns starting at 10am with icons, temperature bars, and precipitation bars.

- [ ] **Step 4: Verify the display visually**

Check:
- [ ] 9 hourly columns visible
- [ ] Hour labels read correctly (10A, 12P, 2P, 4P, 6P, 8P, 10P, 12A, 2A)
- [ ] Temperature bars scale up toward the thunderstorm hours (afternoon) and down overnight
- [ ] Icons change across the day (partly cloudy → thunderstorm → rain → clear night)
- [ ] Precip bars appear for afternoon hours; label shows `%` for hours >30%
- [ ] Night hours (8pm onward) show the correct night-variant icons for CLEAR/MOSTLY_CLEAR

---

### Task 8: Switch to live API and final test

**Files:**
- Modify: `code.py` (restore live fetch)
- Modify: `secrets.py` (add real API key)

- [ ] **Step 1: Restore live fetch in `get_forecast()`**

```python
def get_forecast(lat, long):
    """Fetch hourly forecast from Google Weather API."""
    resp = magtag.network.fetch(get_data_source_url(lat=lat, long=long))
    #resp = Fake_Requests("google_response.txt")
    json_data = resp.json()
    hours = json_data["forecastHours"]
    utc_epoch = parse_iso_to_epoch(hours[0]["interval"]["startTime"])
    tz_offset = int(hours[0]["displayDateTime"]["utcOffset"].rstrip("s"))
    return hours, utc_epoch + tz_offset
```

- [ ] **Step 2: Add your real API key to `secrets.py`**

Set `google_weather_key` to your actual Google Maps Platform key (the one restricted to the Weather API in the Cloud Console).

- [ ] **Step 3: Copy files to the MagTag and observe serial output**

Expected:
```
Fetching forecast...
Refreshing...
Sleeping for X hours, Y minutes
```

If you see an HTTP error (403/401), the API key or billing is not set up correctly — check the Google Cloud Console.

- [ ] **Step 4: Final commit**

```bash
git add code.py secrets.py
git commit -m "Switch to live Google Weather API"
```
