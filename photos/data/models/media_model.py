from __future__ import annotations

from sqlalchemy import (
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Interval, UniqueConstraint, Enum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from photos.data.database.database import Base
from photos.data.interfaces.auth_types import Role


class ImageModel(Base):
    __tablename__ = "images"

    id = mapped_column(String, primary_key=True, index=True)
    filename = mapped_column(String, nullable=False, index=True)
    relative_path = mapped_column(String, nullable=False, unique=True)
    hash = mapped_column(String, nullable=False)
    width = mapped_column(Integer, nullable=False)
    height = mapped_column(Integer, nullable=False)
    duration = mapped_column(Float, nullable=True)
    format = mapped_column(String, nullable=False)
    size_bytes = mapped_column(Integer, nullable=False)
    datetime_local = mapped_column(DateTime(timezone=False), nullable=False)
    timezone_name = mapped_column(String, nullable=True)
    timezone_offset = mapped_column(Interval, nullable=True)
    datetime_source = mapped_column(String, nullable=False)
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
    datetime_utc = mapped_column(DateTime(timezone=True), nullable=True)
    location_id = mapped_column(Integer, ForeignKey("geo_locations.id"), nullable=True)
    location: Mapped[GeoLocationModel | None] = relationship(
        "GeoLocationModel", back_populates="images"
    )
    # User
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    owner: Mapped[UserModel] = relationship("UserModel", back_populates="images")


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
    images: Mapped[list[ImageModel]] = relationship(
        ImageModel, back_populates="owner"
    )
