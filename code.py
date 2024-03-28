# SPDX-FileCopyrightText: 2020 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import terminalio
import displayio
import adafruit_imageload
from adafruit_display_text import label
from adafruit_magtag.magtag import MagTag
from secrets import secrets
from adafruit_display_shapes.rect import Rect
from adafruit_fakerequests import Fake_Requests

# --| USER CONFIG |--------------------------
METRIC = False  # set to True for metric units
# -------------------------------------------

# ----------------------------
# Define various assets
# ----------------------------
ICONS_SMALL_FILE = "/bmps/weather_icons_20px.bmp"
ICON_MAP = {"01d": 0, "01n": 9, "02d": 1, "02n": 10, "03X": 2, "04X": 3, "09X": 4, "10X": 5, "11X": 6, "13X": 7, "50X": 8}


magtag = MagTag()

icons_small_bmp, icons_small_pal = adafruit_imageload.load(ICONS_SMALL_FILE)


# /////////////////////////////////////////////////////////////////////////

def get_icon(code):
    for icon in ICON_MAP:
        if icon[:2] == code[:2]:
            if icon[2:3] == "X":
                return ICON_MAP[icon]
            elif icon[2:3] == code[2:3]:
                return ICON_MAP[icon]

def get_data_source_url(lat, long):
    """Build and return the URL for the OpenWeather API."""

    URL = "https://api.openweathermap.org/data/3.0/onecall?"
    URL += "&lat={}".format(lat)
    URL += "&lon={}".format(long)
    URL += "&units=imperial"

    return URL + "&appid=" + secrets["openweather_token"]


def get_forecast(lat, long):
    """Use OneCall API to fetch forecast and timezone data."""
    resp = magtag.network.fetch(get_data_source_url(lat=lat, long=long))
    #resp = Fake_Requests("response.txt")
    json_data = resp.json()
    # Would be nice to have error checking here
    return json_data["hourly"], json_data["current"]["dt"], json_data["timezone_offset"]

def format_forcast_data(forecast_data, local_tz_offset):
    hour_list = []

    # Assuming this is ordered list
    for hour_obj in forecast_data:
        hr_forecast = {};
        date = time.localtime(hour_obj["dt"]+local_tz_offset)
        hr_forecast["time"] = hour_obj["dt"]
        hr_forecast["hour"] = date[3]
        hr_forecast["temp"] = hour_obj["temp"]
        hr_forecast["icon"] =hour_obj["weather"][0]["icon"]
        hr_forecast["pop"] = hour_obj["pop"]
        hour_list.append(hr_forecast)

    return hour_list

def get_temp_range(hour_list, lookahead):
    max_temp = 0
    min_temp = 100
    range = 0

    for hour_obj in forecast_data:
        if hour_obj["temp"] > max_temp:
            max_temp = hour_obj["temp"]
        if hour_obj["temp"] < min_temp:
            min_temp = hour_obj["temp"]

    return min_temp, max_temp-min_temp


def build_temp_group(hour_list, x, y, group_height, num_hours, hour_step):

    width = magtag.graphics.display.width
    group = displayio.Group(x=x,y=y)

    col_width = int(width / num_hours)
    min_temp, temp_range = get_temp_range(hour_list, 24)

    icon_temp_height = 20 + 10

    group_height = group_height-icon_temp_height

    for col in range(num_hours):
        hour_index = col * hour_step
        x = int(col_width*col+5)

        diff = hour_list[hour_index]["temp"] - min_temp
        per_height = diff / temp_range
        y = int(per_height * group_height)

        temp_text = str(round(hour_list[hour_index]["temp"]))

        # Weather icon
        icon = displayio.TileGrid(
            icons_small_bmp,
            pixel_shader=icons_small_pal,
            x=x+5,
            y=group_height-y-2,
            width=1,
            height=1,
            tile_width=20,
            tile_height=20,
        )
        group.append(icon)
        icon_index = get_icon(hour_list[hour_index]["icon"])
        icon[0] = icon_index

        # Temperature
        temp_bar = label.Label(terminalio.FONT, text=temp_text, color=0x000000)
        temp_bar.anchor_point = (0, 0.5)
        temp_bar.anchored_position = (x+10, (group_height-y+23))
        group.append(temp_bar)

    return group

def build_precip_display(hour_list, x, y, group_height, num_hours, hour_step):

    group = displayio.Group(x=x,y=y)
    width = magtag.graphics.display.width
    col_width = int(width / num_hours)

    for col in range(num_hours):
        hour_index = col * hour_step
        x = int(col_width*col+5)

        # Probability of precep
        rect_height = int(group_height * hour_list[hour_index]["pop"])
        if (rect_height == 0):
            rect_height = 1

        pop_y = (group_height-rect_height)
        pop_rect = Rect(x, pop_y, col_width-2, rect_height, fill=0x999999)
        group.append(pop_rect)

        if (hour_list[hour_index]["pop"] > 0.3):
            pop_text = str(round(hour_list[hour_index]["pop"] * 100)) + "%"
            pop_label = label.Label(terminalio.FONT, text=pop_text, color=0x222222)
            pop_label.anchor_point = (0, 0.5)
            if hour_list[hour_index]["pop"] == 1:
                pop_offset = 4
            else:
                pop_offset = 7
            pop_label.anchored_position = (x+pop_offset, group_height-10)
            group.append(pop_label)

    return group


def build_hour_group(hour_list, x, y, group_height, num_hours, hour_step):

    width = magtag.graphics.display.width
    col_width = int(width / num_hours)

    group = displayio.Group(x=x,y=y)

    for col in range(num_hours):
        hour_index = col * hour_step
        x = int(col_width*col+5)

        # Hour labels
        hour_num = hour_list[hour_index]["hour"]
        if hour_num > 12:
            hour_text = str(hour_num % 12) + "P"
        else:
            hour_text = str(hour_num) + "A"

        hour_label = label.Label(terminalio.FONT, text=hour_text, color=0x000000)
        hour_label.anchor_point = (0, 0.5)
        hour_label.anchored_position = (x+10, 0)
        group.append(hour_label)

    return group

def go_to_sleep(current_time):
    """Enter deep sleep for time needed."""
    # compute current time offset in seconds
    hour, minutes, seconds = time.localtime(current_time)[3:6]

    # if after 8pm, sleep until 6am
    if hour > 20:
        seconds_to_sleep = ((((24-hour) * 60) - minutes) + (6 * 60)) * 60
    # else if after midnight, but before 6, sleep till 6am
    elif hour < 6:
        seconds_to_sleep = (((6-hour) * 60) - minutes) * 60
    # else, sleep until the next hour
    else:
        seconds_to_sleep = (((hour % 2) * 60) + (60-minutes)) * 60

    print(
        "Sleeping for {} hours, {} minutes".format(
            seconds_to_sleep // 3600, (seconds_to_sleep // 60) % 60
        )
    )
    magtag.exit_and_deep_sleep(seconds_to_sleep)





# ===========
#  M A I N
# ===========


print("Fetching forecast...")
lat = secrets["lat"]
long = secrets["long"]
forecast_data, utc_time, local_tz_offset = get_forecast(lat, long)

hour_list = format_forcast_data(forecast_data, local_tz_offset)


num_hours = 9
hour_step = 2

height = magtag.graphics.display.height
pop_height = 18
hour_height = 16
temp_height = int(height - pop_height - hour_height)+2

temp_group = build_temp_group(hour_list, 0, 0, temp_height, num_hours, hour_step)
precip_group = build_precip_display(hour_list, 0, temp_height, pop_height, num_hours, hour_step)
hour_group = build_hour_group(hour_list, 0, temp_height+pop_height+4, hour_height, num_hours, hour_step)

magtag.splash.append(temp_group)
magtag.splash.append(precip_group)
magtag.splash.append(hour_group)



print("Refreshing...")
time.sleep(magtag.display.time_to_refresh + 1)
magtag.display.refresh()
time.sleep(magtag.display.time_to_refresh + 1)

print("Sleeping...")
go_to_sleep(utc_time + local_tz_offset)
#  entire code will run again after deep sleep cycle
#  similar to hitting the reset button

