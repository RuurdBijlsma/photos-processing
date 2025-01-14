from __future__ import annotations

from pgvecto_rs.sqlalchemy import VECTOR
from pgvecto_rs.types import Hnsw, IndexOption, Vector
from sqlalchemy import (
    ARRAY,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Interval,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.data.enums.classification.activity_type import ActivityType
from app.data.enums.classification.animal_type import AnimalType
from app.data.enums.classification.document_type import DocumentType
from app.data.enums.classification.event_type import EventType
from app.data.enums.classification.object_type import ObjectType
from app.data.enums.classification.people_type import PeopleType
from app.data.enums.classification.scene_type import SceneType
from app.data.enums.classification.weather_condition import WeatherCondition
from app.data.enums.face_sex import FaceSex
from app.data.enums.user_role import Role


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
        "GeoLocationModel",
        back_populates="images",
    )
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
    # Relations
    visual_information: Mapped[list[VisualInformationModel]] = relationship(
        "VisualInformationModel",
        back_populates="image",
        cascade="all, delete-orphan",
    )
    # User
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    owner: Mapped[UserModel] = relationship("UserModel", back_populates="images")

    __table_args__ = (Index("idx_datetime_local_utc", "datetime_local", "datetime_utc"),)


class VisualInformationModel(Base):
    __tablename__ = "visual_information"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[str] = mapped_column(String, ForeignKey("images.id"))
    image: Mapped[ImageModel] = relationship("ImageModel", back_populates="visual_information")
    frame_percentage = mapped_column(Integer, nullable=False)
    # AI shit
    embedding: Mapped[Vector] = mapped_column(VECTOR(768), nullable=False)
    # Objects
    objects: Mapped[list[ObjectBoxModel]] = relationship(
        "ObjectBoxModel",
        back_populates="visual_information",
        cascade="all, delete-orphan",
    )
    # OCR
    ocr_boxes: Mapped[list[OCRBoxModel]] = relationship(
        "OCRBoxModel",
        back_populates="visual_information",
        cascade="all, delete-orphan",
    )
    # Faces
    faces: Mapped[list[FaceBoxModel]] = relationship(
        "FaceBoxModel",
        back_populates="visual_information",
        cascade="all, delete-orphan",
    )
    # Classifications
    scene_type: Mapped[SceneType] = mapped_column(
        Enum(SceneType),
        nullable=False,
    )
    people_type: Mapped[PeopleType | None] = mapped_column(
        Enum(PeopleType),
        nullable=True,
    )
    animal_type: Mapped[AnimalType | None] = mapped_column(
        Enum(AnimalType),
        nullable=True,
    )
    document_type: Mapped[DocumentType | None] = mapped_column(
        Enum(DocumentType),
        nullable=True,
    )
    object_type: Mapped[ObjectType | None] = mapped_column(
        Enum(ObjectType),
        nullable=True,
    )
    activity_type: Mapped[ActivityType | None] = mapped_column(
        Enum(ActivityType),
        nullable=True,
    )
    event_type: Mapped[EventType | None] = mapped_column(
        Enum(EventType),
        nullable=True,
    )
    weather_condition: Mapped[WeatherCondition | None] = mapped_column(
        Enum(WeatherCondition),
        nullable=True,
    )
    is_outside = mapped_column(Boolean, nullable=False)
    is_landscape = mapped_column(Boolean, nullable=False)
    is_cityscape = mapped_column(Boolean, nullable=False)
    is_travel = mapped_column(Boolean, nullable=False)
    # Image to text
    #   OCR
    has_legible_text = mapped_column(Boolean, nullable=False)
    ocr_text = mapped_column(Text, nullable=True)
    document_summary = mapped_column(Text, nullable=True)
    # Quality measurements
    measured_sharpness = mapped_column(Float)
    measured_noise = mapped_column(Integer)
    measured_brightness = mapped_column(Float)
    measured_contrast = mapped_column(Float)
    measured_clipping = mapped_column(Float)
    measured_dynamic_range = mapped_column(Float)
    quality_score = mapped_column(Float)
    #   --
    summary = mapped_column(String, nullable=True)
    caption = mapped_column(String, nullable=False)

    __table_args__ = (
        Index(
            "emb_idx_2",
            "embedding",
            postgresql_using="vectors",
            postgresql_with={
                "options": f"$${IndexOption(index=Hnsw()).dumps()}$$",
            },
            postgresql_ops={"embedding": "vector_l2_ops"},
        ),
    )


class ObjectBoxModel(Base):
    __tablename__ = "object_boxes"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    visual_information_id = mapped_column(Integer, ForeignKey("visual_information.id"))
    visual_information: Mapped[VisualInformationModel] = relationship(
        "VisualInformationModel",
        back_populates="objects",
    )

    position: Mapped[tuple[float, float]] = mapped_column(ARRAY(Float), nullable=False)
    width = mapped_column(Float, nullable=False)
    height = mapped_column(Float, nullable=False)
    label = mapped_column(String, nullable=False)
    confidence = mapped_column(Float, nullable=False)


class OCRBoxModel(Base):
    __tablename__ = "ocr_boxes"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    visual_information_id = mapped_column(Integer, ForeignKey("visual_information.id"))
    visual_information: Mapped[VisualInformationModel] = relationship(
        "VisualInformationModel",
        back_populates="ocr_boxes",
    )

    position: Mapped[tuple[float, float]] = mapped_column(ARRAY(Float), nullable=False)
    width = mapped_column(Float, nullable=False)
    height = mapped_column(Float, nullable=False)
    text = mapped_column(String, nullable=False)
    confidence = mapped_column(Float, nullable=False)


class FaceBoxModel(Base):
    __tablename__ = "face_boxes"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    visual_information_id = mapped_column(Integer, ForeignKey("visual_information.id"))
    visual_information: Mapped[VisualInformationModel] = relationship(
        "VisualInformationModel",
        back_populates="faces",
    )
    unique_face_id = mapped_column(Integer, ForeignKey("unique_faces.id"))
    unique_face: Mapped[UniqueFaceModel] = relationship(
        "UniqueFaceModel",
        back_populates="faces",
    )

    # Position and dimensions
    position: Mapped[tuple[float, float]] = mapped_column(ARRAY(Float), nullable=False)
    width = mapped_column(Float, nullable=False)
    height = mapped_column(Float, nullable=False)

    # Attributes
    age = mapped_column(Integer, nullable=False)
    confidence = mapped_column(Float, nullable=False)
    sex = mapped_column(Enum(FaceSex), nullable=False)

    # Facial feature points
    mouth_left: Mapped[tuple[float, float]] = mapped_column(ARRAY(Float), nullable=False)
    mouth_right: Mapped[tuple[float, float]] = mapped_column(ARRAY(Float), nullable=False)
    nose_tip: Mapped[tuple[float, float]] = mapped_column(ARRAY(Float), nullable=False)
    eye_left: Mapped[tuple[float, float]] = mapped_column(ARRAY(Float), nullable=False)
    eye_right: Mapped[tuple[float, float]] = mapped_column(ARRAY(Float), nullable=False)

    # Embedding
    embedding: Mapped[Vector] = mapped_column(VECTOR(512), nullable=False)

    __table_args__ = (
        Index(
            "face_emb_index",
            "embedding",
            postgresql_using="vectors",
            postgresql_with={
                "options": f"$${IndexOption(index=Hnsw()).dumps()}$$",
            },
            postgresql_ops={"embedding": "vector_l2_ops"},
        ),
    )


class UniqueFaceModel(Base):
    __tablename__ = "unique_faces"

    id = mapped_column(Integer, primary_key=True)
    centroid: Mapped[Vector] = mapped_column(VECTOR(512), nullable=False)
    user_provided_label = mapped_column(String, nullable=True)

    # One-to-many relationship with FaceBox
    faces: Mapped[list[FaceBoxModel]] = relationship(
        FaceBoxModel,
        back_populates="unique_face",
    )

    __table_args__ = (
        Index(
            "centroid_index",
            "centroid",
            postgresql_using="vectors",
            postgresql_with={
                "options": f"$${IndexOption(index=Hnsw()).dumps()}$$",
            },
            postgresql_ops={"centroid": "vector_l2_ops"},
        ),
    )


class GeoLocationModel(Base):
    __tablename__ = "geo_locations"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    country = mapped_column(String, nullable=False)
    province = mapped_column(String, nullable=True)
    city = mapped_column(String, nullable=False)
    latitude = mapped_column(Float, nullable=False)
    longitude = mapped_column(Float, nullable=False)
    # One-to-many relationship with ImageLocation
    images: Mapped[list[ImageModel]] = relationship(
        ImageModel,
        back_populates="location",
    )
    __table_args__ = (UniqueConstraint("city", "province", "country", name="unique_location"),)


class UserModel(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String, nullable=False, unique=True)
    hashed_password = mapped_column(String, nullable=False)
    role = mapped_column(Enum(Role), nullable=False)
    images: Mapped[list[ImageModel]] = relationship(ImageModel, back_populates="owner")
