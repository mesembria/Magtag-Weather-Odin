# Error Handling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add clear error messages on display and LEDs for all failure points, with button-triggered wake from every deep sleep.

**Architecture:** All changes are in `code.py`. Two functions are added/refactored (`show_error`, `go_to_sleep`). The main block gains targeted try/except at each failure point. `get_forecast()` is split into a separate `parse_forecast(resp)` helper so the fetch and parse can be wrapped independently.

**Tech Stack:** CircuitPython 9.x, adafruit_magtag, built-in `alarm` module, `displayio`, `label.Label`, `terminalio.FONT`

---

### Task 1: Add alarm imports and refactor go_to_sleep()

**Files:**
- Modify: `code.py` (imports section, `go_to_sleep` function)

- [ ] **Step 1: Add imports**

Add these two lines to the import block at the top of `code.py`, after the existing imports:

```python
import alarm
import board
```

- [ ] **Step 2: Replace go_to_sleep()**

Replace the existing `go_to_sleep()` function (lines 337–357) with:

```python
def go_to_sleep(current_time):
    """Enter deep sleep until next sync time; any button press also wakes the device."""
    hour, minutes, seconds = time.localtime(current_time)[3:6]

    if hour > 20:
        seconds_to_sleep = ((((24 - hour) * 60) - minutes) + (6 * 60)) * 60
    elif hour < 6:
        seconds_to_sleep = (((6 - hour) * 60) - minutes) * 60
    else:
        seconds_to_sleep = (((hour % 2) * 60) + (60 - minutes)) * 60

    print(
        "Sleeping for {} hours, {} minutes".format(
            seconds_to_sleep // 3600, (seconds_to_sleep // 60) % 60
        )
    )
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + seconds_to_sleep)
    button_alarms = [
        alarm.pin.PinAlarm(pin=board.BUTTON_A, value=False, pull=True),
        alarm.pin.PinAlarm(pin=board.BUTTON_B, value=False, pull=True),
        alarm.pin.PinAlarm(pin=board.BUTTON_C, value=False, pull=True),
        alarm.pin.PinAlarm(pin=board.BUTTON_D, value=False, pull=True),
    ]
    alarm.exit_and_deep_sleep_until_alarms(time_alarm, *button_alarms)
```

- [ ] **Step 3: Deploy and verify button wake**

Copy `code.py` to the `CIRCUITPY` drive. Let the device complete a normal fetch cycle and enter deep sleep. Press any of the 4 front buttons. The device should wake and restart — visible via serial console printing `Fetching forecast...`.

- [ ] **Step 4: Commit**

```bash
git add code.py
git commit -m "refactor: replace exit_and_deep_sleep with alarm module to enable button wake"
```

---

### Task 2: Implement show_error()

**Files:**
- Modify: `code.py` (add `show_error` function after `go_to_sleep`)

- [ ] **Step 1: Add show_error() function**

Add the following function immediately after `go_to_sleep()`:

```python
def show_error(title, detail, led_color):
    """Show an error screen on the e-ink display, signal via neopixels, then deep sleep 30 min."""
    print("Error:", title, "-", detail)

    magtag.peripherals.neopixels.fill(led_color)

    while len(magtag.splash) > 0:
        magtag.splash.pop()

    error_group = displayio.Group()

    bg = Rect(0, 0, magtag.graphics.display.width, magtag.graphics.display.height, fill=0xFFFFFF)
    error_group.append(bg)

    title_label = label.Label(terminalio.FONT, text=title, color=0x000000, scale=2)
    title_label.anchor_point = (0.5, 0)
    title_label.anchored_position = (magtag.graphics.display.width // 2, 20)
    error_group.append(title_label)

    detail_label = label.Label(terminalio.FONT, text=detail, color=0x000000)
    detail_label.anchor_point = (0.5, 0)
    detail_label.anchored_position = (magtag.graphics.display.width // 2, 68)
    error_group.append(detail_label)

    sync_label = label.Label(terminalio.FONT, text="Press any button to sync", color=0x000000)
    sync_label.anchor_point = (0.5, 0)
    sync_label.anchored_position = (magtag.graphics.display.width // 2, 92)
    error_group.append(sync_label)

    magtag.splash.append(error_group)

    time.sleep(magtag.display.time_to_refresh + 1)
    magtag.display.refresh()
    time.sleep(magtag.display.time_to_refresh + 1)

    magtag.peripherals.neopixels.fill((0, 0, 0))

    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 1800)
    button_alarms = [
        alarm.pin.PinAlarm(pin=board.BUTTON_A, value=False, pull=True),
        alarm.pin.PinAlarm(pin=board.BUTTON_B, value=False, pull=True),
        alarm.pin.PinAlarm(pin=board.BUTTON_C, value=False, pull=True),
        alarm.pin.PinAlarm(pin=board.BUTTON_D, value=False, pull=True),
    ]
    alarm.exit_and_deep_sleep_until_alarms(time_alarm, *button_alarms)
```

- [ ] **Step 2: Temporarily call show_error() to verify display output**

At the very start of the main block (just before `print("Fetching forecast...")`), temporarily add:

```python
show_error("TEST ERROR", "This is a test message", (255, 0, 0))
```

Deploy to CIRCUITPY. The device should:
1. Light all 4 neopixels red
2. Render "TEST ERROR" (scale=2), "This is a test message", and "Press any button to sync" on the e-ink screen
3. Turn off neopixels and enter 30-minute deep sleep

- [ ] **Step 3: Remove the temporary test call**

Delete the `show_error("TEST ERROR", ...)` line.

- [ ] **Step 4: Commit**

```bash
git add code.py
git commit -m "feat: add show_error() for e-ink display and neopixel error feedback"
```

---

### Task 3: Add battery check

**Files:**
- Modify: `code.py` (main block, before icon load)

- [ ] **Step 1: Add battery check at the top of the main block**

In the main block, add the following as the first thing that runs (before the icon load and before `print("Fetching forecast...")`):

```python
voltage = magtag.peripherals.battery
if voltage < 3.5:
    show_error(
        "LOW BATTERY",
        "Charge soon ({:.1f}V)".format(voltage),
        (255, 255, 0)
    )
```

- [ ] **Step 2: Test by temporarily raising the threshold**

Change `3.5` to `5.0` to force a trigger regardless of actual charge. Deploy to CIRCUITPY. The device should:
1. Light all 4 neopixels yellow
2. Display "LOW BATTERY", "Charge soon (X.XV)" with the real voltage reading, and "Press any button to sync"
3. Enter deep sleep

Restore the threshold to `3.5`.

- [ ] **Step 3: Commit**

```bash
git add code.py
git commit -m "feat: add proactive battery voltage check before network fetch"
```

---

### Task 4: Refactor fetch/parse and add targeted network, API, and data error handling

**Files:**
- Modify: `code.py` (remove module-level icon load, rename `get_forecast`, restructure main block)

- [ ] **Step 1: Remove the module-level icon load**

Delete this line from near the top of `code.py` (currently appears just after `magtag = MagTag()`):

```python
icons_small_bmp, icons_small_pal = adafruit_imageload.load(ICONS_SMALL_FILE)
```

- [ ] **Step 2: Rename get_forecast() to parse_forecast()**

Replace the existing `get_forecast(lat, long)` function with `parse_forecast(resp)`, which takes the HTTP response instead of coordinates. The body is the same minus the fetch call:

```python
def parse_forecast(resp):
    """Parse Google Weather API response into forecast hours and local epoch time."""
    json_data = resp.json()
    hours = json_data["forecastHours"]
    utc_epoch = parse_iso_to_epoch(hours[0]["interval"]["startTime"])
    tz_offset = int(hours[0]["displayDateTime"]["utcOffset"].rstrip("s"))
    return hours, utc_epoch + tz_offset
```

- [ ] **Step 3: Replace the main block fetch/parse section**

Replace the existing lines:

```python
print("Fetching forecast...")
lat = secrets["lat"]
long = secrets["long"]
forecast_data, local_time = get_forecast(lat, long)
```

with:

```python
try:
    icons_small_bmp, icons_small_pal = adafruit_imageload.load(ICONS_SMALL_FILE)
except OSError:
    show_error("MISSING FILE", "weather_icons_20px.bmp not found", (255, 255, 255))

lat = secrets["lat"]
long = secrets["long"]

print("Fetching forecast...")
try:
    resp = magtag.network.fetch(get_data_source_url(lat, long))
except (ConnectionError, OSError):
    show_error("NO NETWORK", "Could not connect to WiFi", (255, 0, 0))

if resp.status_code != 200:
    show_error(
        "API ERROR",
        "Server returned {}".format(resp.status_code),
        (255, 165, 0)
    )

try:
    forecast_data, local_time = parse_forecast(resp)
except (KeyError, ValueError):
    show_error("DATA ERROR", "Unexpected API response", (128, 0, 128))
```

- [ ] **Step 4: Verify normal operation**

Deploy to CIRCUITPY. Confirm the device fetches weather and renders the display normally (no regressions from splitting the fetch and parse).

- [ ] **Step 5: Test the network error path**

Temporarily change `get_data_source_url()` to return a bogus string:

```python
def get_data_source_url(lat, lng):
    return "https://does-not-exist.invalid/"
```

Deploy. The device should display "NO NETWORK" with red LEDs. Restore the real URL.

- [ ] **Step 6: Test the data error path**

Temporarily add `raise ValueError("test")` as the first line of `parse_forecast()`:

```python
def parse_forecast(resp):
    raise ValueError("test")
    ...
```

Deploy. The device should display "DATA ERROR" with purple LEDs. Remove the temporary raise.

- [ ] **Step 7: Commit**

```bash
git add code.py
git commit -m "feat: split get_forecast into fetch+parse with targeted error handling per failure point"
```

---

### Task 5: Add catch-all handler for the render and sleep phase

**Files:**
- Modify: `code.py` (main block, format/render/sleep section)

- [ ] **Step 1: Wrap the format/render/sleep block**

Replace the existing code from `hour_list = format_forcast_data(forecast_data)` through `go_to_sleep(local_time)` with:

```python
try:
    hour_list = format_forcast_data(forecast_data)

    num_hours = 9
    hour_step = 2

    height = magtag.graphics.display.height
    pop_height = 18
    hour_height = 16
    temp_height = int(height - pop_height - hour_height) + 2

    temp_group = build_temp_group(hour_list, 0, 0, temp_height, num_hours, hour_step)
    precip_group = build_precip_display(hour_list, 0, temp_height, pop_height, num_hours, hour_step)
    hour_group = build_hour_group(hour_list, 0, temp_height + pop_height + 4, hour_height, num_hours, hour_step)

    magtag.splash.append(temp_group)
    magtag.splash.append(precip_group)
    magtag.splash.append(hour_group)

    print("Refreshing...")
    time.sleep(magtag.display.time_to_refresh + 1)
    magtag.display.refresh()
    time.sleep(magtag.display.time_to_refresh + 1)

    print("Sleeping...")
    go_to_sleep(local_time)
except Exception as e:
    show_error("ERROR", type(e).__name__, (255, 255, 255))
```

- [ ] **Step 2: Verify normal end-to-end operation**

Deploy to CIRCUITPY. Confirm weather renders correctly, the device sleeps on schedule, and a button press triggers an immediate re-sync.

- [ ] **Step 3: Commit**

```bash
git add code.py
git commit -m "feat: add catch-all exception handler for format/render/sleep phase"
```
