# Error Handling & Debugging Design

**Date:** 2026-06-27
**Project:** magtag_weather_odin

## Goal

Add clear, readable error feedback for all likely failure points on the MagTag device. Errors are shown on the e-ink display and signaled via neopixel LEDs. After displaying an error the device enters deep sleep to conserve battery. Any button press wakes the device and triggers an immediate sync.

---

## Error Taxonomy

Six failure points, handled in this order:

| # | When | Error | Detection |
|---|------|-------|-----------|
| 1 | Before fetch | Low battery (`< 3.5V`) | Proactive voltage check via `magtag.peripherals.battery` |
| 2 | At startup | Missing icon file | `OSError` from `adafruit_imageload.load()` |
| 3 | During fetch | WiFi / network down | `ConnectionError`, `OSError` from `magtag.network.fetch()` |
| 4 | After fetch | API error (bad key, quota, 4xx/5xx) | `resp.status_code != 200` |
| 5 | During parse | Unexpected API data | `KeyError`, `ValueError` in `get_forecast()` / `format_forcast_data()` |
| 6 | Anywhere | Unknown error | Top-level `except Exception` fallback |

Battery is checked first so that if a low-voltage brownout is the root cause of a network failure, the user sees "LOW BATTERY" rather than a misleading WiFi error.

---

## Error Display Format

Each error clears the display and shows three lines of text:

```
┌─────────────────────────────────────┐
│                                     │
│  LOW BATTERY                        │
│  Charge soon (3.2V)                 │
│  Press any button to sync           │
│                                     │
└─────────────────────────────────────┘
```

- **Line 1** — error name in ALL CAPS (short, scannable)
- **Line 2** — one-line explanation with relevant detail (voltage, HTTP status code, etc.)
- **Line 3** — always `"Press any button to sync"`

Uses existing `terminalio.FONT` with `label.Label`. No new font assets required.

### Error messages

| Error | Line 1 | Line 2 |
|-------|--------|--------|
| Low battery | `LOW BATTERY` | `Charge soon (X.XV)` |
| WiFi / network | `NO NETWORK` | `Could not connect to WiFi` |
| API error | `API ERROR` | `Server returned XXX` |
| Unexpected data | `DATA ERROR` | `Unexpected API response` |
| Missing icon file | `MISSING FILE` | `weather_icons_20px.bmp not found` |
| Unknown | `ERROR` | Exception class name |

---

## LED Color Scheme

All 4 neopixels light the same solid color while the error screen is displayed. LEDs turn off before deep sleep.

| Error | Color |
|-------|-------|
| Low battery | Yellow |
| WiFi / network | Red |
| API error | Orange |
| Unexpected data | Purple |
| Missing icon file | White |
| Unknown | White |

---

## Button Wake & Sleep Behavior

Deep sleep is configured with both a time alarm and all 4 button pin alarms. Any button press wakes the device, restarting `code.py` from scratch — identical to a scheduled wake. No special "woken by button" detection is needed.

Sleep duration on error uses the same logic as normal operation (`go_to_sleep()` unchanged in its timing calculation). The button provides manual retry; the next scheduled wake provides automatic recovery.

The current `magtag.exit_and_deep_sleep(seconds)` call is replaced with `alarm.exit_and_deep_sleep_until_alarms(time_alarm, *button_alarms)` from CircuitPython's built-in `alarm` module.

This button-wake behavior applies during every deep sleep, not just error screens. Any button press always triggers an immediate sync.

---

## Code Structure

### New function: `show_error(title, detail, led_color)`

- Sets all 4 neopixels to `led_color`
- Clears `magtag.splash` and renders three `label.Label` lines
- Waits for display refresh, then turns off LEDs
- Calls `go_to_sleep(local_time)` if `local_time` is available. If not (e.g. battery check or network failure occurs before the API response sets the time), falls back to a fixed 30-minute deep sleep — the time-based sleep logic requires a synced clock which may not be available at that point.

### Updated function: `go_to_sleep(current_time)`

- Same sleep duration logic as today
- Replaces `magtag.exit_and_deep_sleep(seconds)` with `alarm.exit_and_deep_sleep_until_alarms()` passing a `TimeAlarm` and four `PinAlarm` instances for `board.BUTTON_A`, `board.BUTTON_B`, `board.BUTTON_C`, `board.BUTTON_D` (active-low, pull-up enabled)

### Updated main block

Targeted try/except at each failure point, in order:

```
battery check          → show_error("LOW BATTERY", ..., yellow)
icon file load         → show_error("MISSING FILE", ..., white)
get_forecast()         → network errors → show_error("NO NETWORK", ..., red)
                       → resp.status_code check → show_error("API ERROR", ..., orange)
                       → KeyError/ValueError → show_error("DATA ERROR", ..., purple)
format/render/sleep    → except Exception → show_error("ERROR", ..., white)
```

No new files. No new libraries beyond the built-in `alarm` module (already available on CircuitPython 9.x for MagTag).
