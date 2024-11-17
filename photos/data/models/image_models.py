from __future__ import annotations

from pgvecto_rs.sqlalchemy import VECTOR
from sqlalchemy import (
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Interval,
    UniqueConstraint,
    Enum,
    Boolean, Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase

from photos.data.interfaces.auth_types import Role
from photos.data.interfaces.weather_condition_codes import WeatherCondition


class Base(AsyncAttrs, DeclarativeBase):
    pass


class ImageModel(Base):
    __tablename__ = "images"
    # base info
    id = mapped_column(String, primary_key=True, index=True)
    filename = mapped_column(String, nullable=False, index=True)
    relative_path = mapped_column(String, nullable=False, unique=True, index=True)
    hash = mapped_column(String, nullable=False)
    # image dimensions
    width = mapped_column(Integer, nullable=False)
    height = mapped_column(Integer, nullable=False)
    duration = mapped_column(Float, nullable=True)
    format = mapped_column(String, nullable=False)
    size_bytes = mapped_column(Integer, nullable=False)
    # frontend stuff
    is_motion_photo = mapped_column(Boolean, nullable=False)
    is_hdr = mapped_column(Boolean, nullable=False)
    is_night_sight = mapped_column(Boolean, nullable=False)
    is_selfie = mapped_column(Boolean, nullable=False)
    is_panorama = mapped_column(Boolean, nullable=False)
    # datetime
    datetime_local = mapped_column(DateTime(timezone=False), nullable=False, index=True)
    datetime_utc = mapped_column(DateTime(timezone=False), nullable=True, index=True)
    datetime_source = mapped_column(String, nullable=False)
    timezone_name = mapped_column(String, nullable=True)
    timezone_offset = mapped_column(Interval, nullable=True)
    # data url
    data_url = mapped_column(String, nullable=False)
    # EXIF
    exif_tool = mapped_column(JSONB, nullable=False)
    file = mapped_column(JSONB, nullable=False)
    composite = mapped_column(JSONB, nullable=False)
    exif = mapped_column(JSONB, nullable=True)
    xmp = mapped_column(JSONB, nullable=True)
    jfif = mapped_column(JSONB, nullable=True)
    icc_profile = mapped_column(JSONB, nullable=True)
    gif = mapped_column(JSONB, nullable=True)
    quicktime = mapped_column(JSONB, nullable=True)
    matroska = mapped_column(JSONB, nullable=True)
    # GPS
    latitude = mapped_column(Float, nullable=True)
    longitude = mapped_column(Float, nullable=True)
    altitude = mapped_column(Float, nullable=True)
    location_id = mapped_column(Integer, ForeignKey("geo_locations.id"), nullable=True)
    location: Mapped[GeoLocationModel | None] = relationship(
        "GeoLocationModel", back_populates="images"
    )
    # User
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    owner: Mapped[UserModel] = relationship("UserModel", back_populates="images")
    # Weather https://dev.meteostat.net/formats.html#weather-condition-codes
    weather_recorded_at = mapped_column(DateTime(timezone=False), nullable=True)
    weather_temperature = mapped_column(Float, nullable=True)
    weather_dewpoint = mapped_column(Float, nullable=True)
    weather_relative_humidity = mapped_column(Float, nullable=True)
    weather_precipitation = mapped_column(Float, nullable=True)
    weather_wind_gust = mapped_column(Float, nullable=True)
    weather_pressure = mapped_column(Float, nullable=True)
    weather_sun_hours = mapped_column(Float, nullable=True)
    weather_condition = mapped_column(Enum(WeatherCondition), nullable=True)
    # Visual info
    visual_information: Mapped[list["VisualInformationModel"]] = relationship(
        "VisualInformationModel",
        back_populates="image",
        cascade="all, delete-orphan"
    )


class VisualInformationModel(Base):
    __tablename__ = "visual_information"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[str] = mapped_column(String, ForeignKey("images.id"))
    image: Mapped["ImageModel"] = relationship("ImageModel",
                                               back_populates="visual_information")
    snapshot_time_ms = mapped_column(Integer, nullable=False)
    # AI shit
    embedding = mapped_column(VECTOR(768), nullable=False)
    has_legible_text = mapped_column(Boolean, nullable=False)
    ocr_text = mapped_column(Text, nullable=True)


class GeoLocationModel(Base):
    __tablename__ = "geo_locations"

    id = mapped_column(Integer, primary_key=True, index=True)
    country = mapped_column(String, nullable=False)
    province = mapped_column(String, nullable=True)
    city = mapped_column(String, nullable=False)
    latitude = mapped_column(Float, nullable=False)
    longitude = mapped_column(Float, nullable=False)
    # One-to-many relationship with ImageLocation
    images: Mapped[list[ImageModel]] = relationship(
        ImageModel, back_populates="location"
    )
    __table_args__ = (
        UniqueConstraint("city", "province", "country", name="unique_location"),
    )


class UserModel(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String, nullable=False, unique=True)
    hashed_password = mapped_column(String, nullable=False)
    role = mapped_column(Enum(Role), nullable=False)
    images: Mapped[list[ImageModel]] = relationship(ImageModel, back_populates="owner")
