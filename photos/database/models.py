from __future__ import annotations

import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Interval,
    UniqueConstraint,
    Enum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped

Base = declarative_base()


class ImageModel(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False, index=True)
    relative_path = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    duration = Column(Float, nullable=True)
    format = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    datetime_local = Column(DateTime(timezone=False), nullable=False)
    timezone_name = Column(String, nullable=True)
    timezone_offset = Column(Interval, nullable=True)
    datetime_source = Column(String, nullable=False)
    # EXIF
    exif_tool = Column(JSONB, nullable=False)
    file = Column(JSONB, nullable=False)
    composite = Column(JSONB, nullable=False)
    exif = Column(JSONB, nullable=True)
    xmp = Column(JSONB, nullable=True)
    jfif = Column(JSONB, nullable=True)
    icc_profile = Column(JSONB, nullable=True)
    gif = Column(JSONB, nullable=True)
    quicktime = Column(JSONB, nullable=True)
    matroska = Column(JSONB, nullable=True)
    # GPS
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    datetime_utc = Column(DateTime(timezone=True), nullable=True)
    location_id = Column(Integer, ForeignKey("geo_locations.id"), nullable=True)
    location: Mapped[GeoLocationModel | None] = relationship(
        "GeoLocationModel", back_populates="images"
    )


class GeoLocationModel(Base):
    __tablename__ = "geo_locations"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, nullable=False)
    province = Column(String, nullable=True)
    city = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    # One-to-many relationship with ImageLocation
    images: Mapped[list[ImageModel]] = relationship(
        "ImageModel", back_populates="location"
    )
    __table_args__ = (
        UniqueConstraint("city", "province", "country", name="unique_location"),
    )


class Role(enum.Enum):
    ADMIN = 1
    USER = 2


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)
