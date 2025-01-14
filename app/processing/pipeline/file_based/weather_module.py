import math
from datetime import timedelta

from meteostat import Hourly, Point

from app.data.enums.classification.weather_condition import WeatherCondition
from app.data.interfaces.image_data import ImageData, TimeData, WeatherData
from app.processing.pipeline.base_module import FileModule


class WeatherModule(FileModule):
    def process(self, data: ImageData) -> WeatherData:
        assert isinstance(data, TimeData)
        if not data.datetime_utc or not data.latitude or not data.longitude:
            return WeatherData(**data.model_dump())
        meteo_data = Hourly(
            Point(lat=data.latitude, lon=data.longitude),
            data.datetime_utc - timedelta(minutes=30),
            data.datetime_utc + timedelta(minutes=30),
        )
        meteo_data = meteo_data.fetch()
        if len(meteo_data) == 0:
            return WeatherData(**data.model_dump())
        max_possible_rows = 2
        assert len(meteo_data) <= max_possible_rows
        weather = meteo_data.iloc[0]
        return WeatherData(
            **data.model_dump(),
            weather_recorded_at=weather.name.to_pydatetime(),
            weather_temperature=None if math.isnan(weather.temp) else weather.temp,
            weather_dewpoint=None if math.isnan(weather.dwpt) else weather.dwpt,
            weather_relative_humidity=None
            if math.isnan(
                weather.rhum,
            )
            else weather.rhum,
            weather_precipitation=None if math.isnan(weather.prcp) else weather.prcp,
            weather_wind_gust=None if math.isnan(weather.wpgt) else weather.wpgt,
            weather_pressure=None if math.isnan(weather.pres) else weather.pres,
            weather_sun_hours=None if math.isnan(weather.tsun) else weather.tsun,
            weather_condition=None if math.isnan(weather.coco) else WeatherCondition(int(weather.coco)),
        )
