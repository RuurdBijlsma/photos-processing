import math
from datetime import timedelta

from meteostat import Hourly, Point

from app.data.enums.weather_condition import WeatherCondition
from app.data.interfaces.image_info_types import TimeImageInfo, WeatherImageInfo


def image_weather(image_info: TimeImageInfo) -> WeatherImageInfo:
    if (
        not image_info.datetime_utc
        or not image_info.latitude
        or not image_info.longitude
    ):
        return WeatherImageInfo(**image_info.model_dump())
    data = Hourly(
        Point(lat=image_info.latitude, lon=image_info.longitude),
        image_info.datetime_utc - timedelta(minutes=30),
        image_info.datetime_utc + timedelta(minutes=30),
    )
    data = data.fetch()
    if len(data) == 0:
        return WeatherImageInfo(**image_info.model_dump())
    assert len(data) == 1
    weather = data.iloc[0]
    return WeatherImageInfo(
        **image_info.model_dump(),
        weather_recorded_at=weather.name.to_pydatetime(),
        weather_temperature=None if math.isnan(weather.temp) else weather.temp,
        weather_dewpoint=None if math.isnan(weather.dwpt) else weather.dwpt,
        weather_relative_humidity=None if math.isnan(weather.rhum) else weather.rhum,
        weather_precipitation=None if math.isnan(weather.prcp) else weather.prcp,
        weather_wind_gust=None if math.isnan(weather.wpgt) else weather.wpgt,
        weather_pressure=None if math.isnan(weather.pres) else weather.pres,
        weather_sun_hours=None if math.isnan(weather.tsun) else weather.tsun,
        weather_condition=None
        if math.isnan(weather.coco)
        else WeatherCondition(int(weather.coco)),
    )
