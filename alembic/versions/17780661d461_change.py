"""change

Revision ID: 17780661d461
Revises:
Create Date: 2024-11-03 21:50:40.840034

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "17780661d461"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "geo_locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("province", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("city", "province", "country", name="unique_location"),
    )
    op.create_index(op.f("ix_geo_locations_id"), "geo_locations", ["id"], unique=False)
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.Enum("ADMIN", "USER", name="role"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "images",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("relative_path", sa.String(), nullable=False),
        sa.Column("hash", sa.String(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("duration", sa.Float(), nullable=True),
        sa.Column("format", sa.String(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("is_motion_photo", sa.Boolean(), nullable=False),
        sa.Column("is_hdr", sa.Boolean(), nullable=False),
        sa.Column("is_night_sight", sa.Boolean(), nullable=False),
        sa.Column("is_selfie", sa.Boolean(), nullable=False),
        sa.Column("is_panorama", sa.Boolean(), nullable=False),
        sa.Column("datetime_local", sa.DateTime(), nullable=False),
        sa.Column("datetime_utc", sa.DateTime(), nullable=True),
        sa.Column("datetime_source", sa.String(), nullable=False),
        sa.Column("timezone_name", sa.String(), nullable=True),
        sa.Column("timezone_offset", sa.Interval(), nullable=True),
        sa.Column("data_url", sa.String(), nullable=False),
        sa.Column("exif_tool", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("file", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("composite", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("exif", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("xmp", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("jfif", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "icc_profile", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("gif", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("quicktime", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("matroska", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("altitude", sa.Float(), nullable=True),
        sa.Column("location_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("weather_recorded_at", sa.DateTime(), nullable=True),
        sa.Column("weather_temperature", sa.Float(), nullable=True),
        sa.Column("weather_dewpoint", sa.Float(), nullable=True),
        sa.Column("weather_relative_humidity", sa.Float(), nullable=True),
        sa.Column("weather_precipitation", sa.Float(), nullable=True),
        sa.Column("weather_wind_gust", sa.Float(), nullable=True),
        sa.Column("weather_pressure", sa.Float(), nullable=True),
        sa.Column("weather_sun_hours", sa.Float(), nullable=True),
        sa.Column(
            "weather_condition",
            sa.Enum(
                "CLEAR",
                "FAIR",
                "CLOUDY",
                "OVERCAST",
                "FOG",
                "FREEZING_FOG",
                "LIGHT_RAIN",
                "RAIN",
                "HEAVY_RAIN",
                "FREEZING_RAIN",
                "HEAVY_FREEZING_RAIN",
                "SLEET",
                "HEAVY_SLEET",
                "LIGHT_SNOWFALL",
                "SNOWFALL",
                "HEAVY_SNOWFALL",
                "RAIN_SHOWER",
                "HEAVY_RAIN_SHOWER",
                "SLEET_SHOWER",
                "HEAVY_SLEET_SHOWER",
                "SNOW_SHOWER",
                "HEAVY_SNOW_SHOWER",
                "LIGHTNING",
                "HAIL",
                "THUNDERSTORM",
                "HEAVY_THUNDERSTORM",
                "STORM",
                name="weathercondition",
            ),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["geo_locations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_images_datetime_local"), "images", ["datetime_local"], unique=False
    )
    op.create_index(
        op.f("ix_images_datetime_utc"), "images", ["datetime_utc"], unique=False
    )
    op.create_index(op.f("ix_images_filename"), "images", ["filename"], unique=False)
    op.create_index(op.f("ix_images_id"), "images", ["id"], unique=False)
    op.create_index(
        op.f("ix_images_relative_path"), "images", ["relative_path"], unique=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_images_relative_path"), table_name="images")
    op.drop_index(op.f("ix_images_id"), table_name="images")
    op.drop_index(op.f("ix_images_filename"), table_name="images")
    op.drop_index(op.f("ix_images_datetime_utc"), table_name="images")
    op.drop_index(op.f("ix_images_datetime_local"), table_name="images")
    op.drop_table("images")
    op.drop_table("users")
    op.drop_index(op.f("ix_geo_locations_id"), table_name="geo_locations")
    op.drop_table("geo_locations")
    # ### end Alembic commands ###
