"""empty message

Revision ID: 79565462b99b
Revises: 
Create Date: 2024-12-13 21:25:47.274779

"""
from collections.abc import Sequence

import sqlalchemy as sa
from pgvecto_rs.sqlalchemy import VECTOR
from pgvecto_rs.types import Hnsw, IndexOption
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "79565462b99b"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### end Alembic commands ###
    op.execute("CREATE EXTENSION IF NOT EXISTS vectors;")
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table("geo_locations",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("country", sa.String(), nullable=False),
    sa.Column("province", sa.String(), nullable=True),
    sa.Column("city", sa.String(), nullable=False),
    sa.Column("latitude", sa.Float(), nullable=False),
    sa.Column("longitude", sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("city", "province", "country", name="unique_location"),
    )
    op.create_table("unique_faces",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("centroid", VECTOR(512), nullable=False),
    sa.Column("user_provided_label", sa.String(), nullable=True),
    sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("users",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("username", sa.String(), nullable=False),
    sa.Column("hashed_password", sa.String(), nullable=False),
    sa.Column("role", sa.Enum("ADMIN", "USER", name="role"), nullable=False),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("username"),
    )
    op.create_table("images",
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
    sa.Column("icc_profile", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column("gif", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column("quicktime", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column("matroska", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column("latitude", sa.Float(), nullable=True),
    sa.Column("longitude", sa.Float(), nullable=True),
    sa.Column("altitude", sa.Float(), nullable=True),
    sa.Column("location_id", sa.Integer(), nullable=True),
    sa.Column("weather_recorded_at", sa.DateTime(), nullable=True),
    sa.Column("weather_temperature", sa.Float(), nullable=True),
    sa.Column("weather_dewpoint", sa.Float(), nullable=True),
    sa.Column("weather_relative_humidity", sa.Float(), nullable=True),
    sa.Column("weather_precipitation", sa.Float(), nullable=True),
    sa.Column("weather_wind_gust", sa.Float(), nullable=True),
    sa.Column("weather_pressure", sa.Float(), nullable=True),
    sa.Column("weather_sun_hours", sa.Float(), nullable=True),
    sa.Column("weather_condition", sa.Enum("CLEAR", "FAIR", "CLOUDY", "OVERCAST", "FOG", "FREEZING_FOG", "LIGHT_RAIN", "RAIN", "HEAVY_RAIN", "FREEZING_RAIN", "HEAVY_FREEZING_RAIN", "SLEET", "HEAVY_SLEET", "LIGHT_SNOWFALL", "SNOWFALL", "HEAVY_SNOWFALL", "RAIN_SHOWER", "HEAVY_RAIN_SHOWER", "SLEET_SHOWER", "HEAVY_SLEET_SHOWER", "SNOW_SHOWER", "HEAVY_SNOW_SHOWER", "LIGHTNING", "HAIL", "THUNDERSTORM", "HEAVY_THUNDERSTORM", "STORM", name="weathercondition"), nullable=True),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(["location_id"], ["geo_locations.id"] ),
    sa.ForeignKeyConstraint(["user_id"], ["users.id"] ),
    sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_images_datetime_local"), "images", ["datetime_local"], unique=False)
    op.create_index(op.f("ix_images_datetime_utc"), "images", ["datetime_utc"], unique=False)
    op.create_index(op.f("ix_images_filename"), "images", ["filename"], unique=False)
    op.create_index(op.f("ix_images_id"), "images", ["id"], unique=False)
    op.create_index(op.f("ix_images_relative_path"), "images", ["relative_path"], unique=True)
    op.create_table("visual_information",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("image_id", sa.String(), nullable=False),
    sa.Column("frame_percentage", sa.Integer(), nullable=False),
    sa.Column("embedding", VECTOR(768), nullable=False),
    sa.Column("scene_type", sa.Enum("AIRFIELD", "AIRPLANE_CABIN", "AIRPORT_TERMINAL", "ALCOVE", "ALLEY", "AMPHITHEATER", "AMUSEMENT_ARCADE", "AMUSEMENT_PARK", "APARTMENT_BUILDING", "AQUARIUM", "AQUEDUCT", "ARCADE", "ARCH", "ARCHAEOLOGICAL_EXCAVATION", "ARCHIVE", "HOCKEY_ARENA", "PERFORMANCE_ARENA", "RODEO_ARENA", "ARMY_BASE", "ART_GALLERY", "ART_SCHOOL", "ART_STUDIO", "ARTISTS_LOFT", "ASSEMBLY_LINE", "ATHLETIC_FIELD", "ATRIUM", "ATTIC", "AUDITORIUM", "AUTO_FACTORY", "AUTO_SHOWROOM", "BADLANDS", "BAKERY", "BALCONY_EXTERIOR", "BALCONY_INTERIOR", "BALL_PIT", "BALLROOM", "BAMBOO_FOREST", "BANK_VAULT", "BANQUET_HALL", "BAR", "BARN", "BARN_DOOR", "BASEBALL_FIELD", "BASEMENT", "BASKETBALL_COURT", "BATHROOM", "INDOOR_BAZAAR", "OUTDOOR_BAZAAR", "BEACH", "BEACH_HOUSE", "BEAUTY_SALON", "BEDCHAMBER", "BEDROOM", "BEER_GARDEN", "BEER_HALL", "BERTH", "BIOLOGY_LABORATORY", "BOARDWALK", "BOAT_DECK", "BOATHOUSE", "BOOKSTORE", "BOOTH", "BOTANICAL_GARDEN", "BOW_WINDOW", "BOWLING_ALLEY", "BOXING_RING", "BRIDGE", "BUILDING_FACADE", "BULLRING", "BURIAL_CHAMBER", "BUS_INTERIOR", "BUS_STATION", "BUTCHERS_SHOP", "BUTTE", "CABIN", "CAFETERIA", "CAMPSITE", "CAMPUS", "NATURAL_CANAL", "URBAN_CANAL", "CANDY_STORE", "CANYON", "CAR_INTERIOR", "CARROUSEL", "CASTLE", "CATACOMB", "CEMETERY", "CHALET", "CHEMISTRY_LAB", "CHILDS_ROOM", "CHURCH_INTERIOR", "CHURCH_EXTERIOR", "CLASSROOM", "CLEAN_ROOM", "CLIFF", "CLOSET", "CLOTHING_STORE", "COAST", "COCKPIT", "COFFEE_SHOP", "COMPUTER_ROOM", "CONFERENCE_CENTER", "CONFERENCE_ROOM", "CONSTRUCTION_SITE", "CORN_FIELD", "CORRAL", "CORRIDOR", "COTTAGE", "COURTHOUSE", "COURTYARD", "CREEK", "CREVASSE", "CROSSWALK", "DAM", "DELICATESSEN", "DEPARTMENT_STORE", "DESERT_SAND", "DESERT_VEGETATION", "DESERT_ROAD", "DINER", "DINING_HALL", "DINING_ROOM", "DISCOTHEQUE", "DOORWAY", "DORM_ROOM", "DOWNTOWN", "DRESSING_ROOM", "DRIVEWAY", "DRUGSTORE", "ELEVATOR", "ELEVATOR_LOBBY", "ELEVATOR_SHAFT", "EMBASSY", "ENGINE_ROOM", "ENTRANCE_HALL", "ESCALATOR", "EXCAVATION", "FABRIC_STORE", "FARM", "FASTFOOD_RESTAURANT", "CULTIVATED_FIELD", "WILD_FIELD", "FIELD_ROAD", "FIRE_ESCAPE", "FIRE_STATION", "FISHPOND", "FLEA_MARKET", "FLORIST_SHOP", "FOOD_COURT", "FOOTBALL_FIELD", "FOREST", "FOREST_PATH", "FOREST_ROAD", "FORMAL_GARDEN", "FOUNTAIN", "GALLEY", "GARAGE_INDOOR", "GARAGE_OUTDOOR", "GAS_STATION", "GAZEBO", "GENERAL_STORE_INTERIOR", "GENERAL_STORE_EXTERIOR", "GIFT_SHOP", "GLACIER", "GOLF_COURSE", "GREENHOUSE_INTERIOR", "GREENHOUSE_EXTERIOR", "GROTTO", "GYMNASIUM", "HANGAR_INTERIOR", "HANGAR_EXTERIOR", "HARBOR", "HARDWARE_STORE", "HAYFIELD", "HELIPORT", "HIGHWAY", "HOME_OFFICE", "HOME_THEATER", "HOSPITAL", "HOSPITAL_ROOM", "HOT_SPRING", "HOTEL", "HOTEL_ROOM", "HOUSE", "HUNTING_LODGE", "ICE_CREAM_PARLOR", "ICE_FLOE", "ICE_SHELF", "ICE_SKATING_RINK", "ICEBERG", "IGLOO", "INDUSTRIAL_AREA", "INN", "ISLET", "JACUZZI", "JAIL_CELL", "JAPANESE_GARDEN", "JEWELRY_SHOP", "JUNKYARD", "KASBAH", "KENNEL", "KINDERGARTEN_CLASSROOM", "KITCHEN", "LAGOON", "LAKE", "LANDFILL", "LANDING_DECK", "LAUNDROMAT", "LAWN", "LECTURE_ROOM", "LEGISLATIVE_CHAMBER", "LIBRARY_INTERIOR", "LIBRARY_EXTERIOR", "LIGHTHOUSE", "LIVING_ROOM", "LOADING_DOCK", "LOBBY", "LOCK_CHAMBER", "LOCKER_ROOM", "MANSION", "MANUFACTURED_HOME", "MARKET", "MARSH", "MARTIAL_ARTS_GYM", "MAUSOLEUM", "MEDINA", "MEZZANINE", "MOAT", "MOSQUE", "MOTEL", "MOUNTAIN", "MOUNTAIN_PATH", "MOUNTAIN_SNOWY", "MOVIE_THEATER", "MUSEUM_INTERIOR", "MUSEUM_EXTERIOR", "MUSIC_STUDIO", "NATURAL_HISTORY_MUSEUM", "NURSERY", "NURSING_HOME", "OAST_HOUSE", "OCEAN", "OFFICE", "OFFICE_BUILDING", "OFFICE_CUBICLES", "OIL_RIG", "OPERATING_ROOM", "ORCHARD", "ORCHESTRA_PIT", "PAGODA", "PALACE", "PANTRY", "PARK", "PARKING_GARAGE_INTERIOR", "PARKING_GARAGE_EXTERIOR", "PARKING_LOT", "PASTURE", "PATIO", "PAVILION", "PET_SHOP", "PHARMACY", "PHONE_BOOTH", "PHYSICS_LABORATORY", "PICNIC_AREA", "PIER", "PIZZERIA", "PLAYGROUND", "PLAYROOM", "PLAZA", "POND", "PORCH", "PROMENADE", "PUB", "RACECOURSE", "RACEWAY", "RAFT", "RAILROAD_TRACK", "RAINFOREST", "RECEPTION", "RECREATION_ROOM", "REPAIR_SHOP", "RESIDENTIAL_NEIGHBORHOOD", "RESTAURANT", "RESTAURANT_KITCHEN", "RESTAURANT_PATIO", "RICE_PADDY", "RIVER", "ROCK_ARCH", "ROOF_GARDEN", "ROPE_BRIDGE", "RUIN", "RUNWAY", "SANDBOX", "SAUNA", "SCHOOLHOUSE", "SCIENCE_MUSEUM", "SERVER_ROOM", "SHED", "SHOE_SHOP", "SHOPFRONT", "SHOPPING_MALL", "SHOWER", "SKI_RESORT", "SKI_SLOPE", "SKY", "SKYSCRAPER", "SLUM", "SNOWFIELD", "SOCCER_FIELD", "STABLE", "BASEBALL_STADIUM", "FOOTBALL_OR_SOCCER_STADIUM", "STAGE", "STAIRCASE", "STORAGE_ROOM", "STREET", "SUBWAY_STATION", "SUPERMARKET", "SUSHI_BAR", "SWAMP", "SWIMMING_HOLE", "SWIMMING_POOL", "SYNAGOGUE", "TELEVISION_ROOM", "TELEVISION_STUDIO", "TEMPLE", "THRONE_ROOM", "TICKET_BOOTH", "TOPIARY_GARDEN", "TOWER", "TOYSHOP", "TRAIN_INTERIOR", "TRAIN_STATION", "TREE_FARM", "TREE_HOUSE", "TRENCH", "TUNDRA", "UNDERWATER", "UTILITY_ROOM", "VALLEY", "VEGETABLE_GARDEN", "VETERINARIANS_OFFICE", "VIADUCT", "VILLAGE", "VINEYARD", "VOLCANO", "VOLLEYBALL_COURT", "WAITING_ROOM", "WATER_PARK", "WATER_TOWER", "WATERFALL", "WATERING_HOLE", "WAVE", "WET_BAR", "WHEAT_FIELD", "WIND_FARM", "WINDMILL", "YARD", "YOUTH_HOSTEL", "ZEN_GARDEN", "UNKNOWN", name="scenetype"), nullable=False),
    sa.Column("people_type", sa.Enum("SELFIE", "GROUP", "PORTRAIT", "CROWD", name="peopletype"), nullable=True),
    sa.Column("animal_type", sa.Enum("CAT", "DOG", "HAMSTER", "RAT", "GUINEA_PIG", "RABBIT", "BIRD", "WILDLIFE", name="animaltype"), nullable=True),
    sa.Column("document_type", sa.Enum("BOOK_OR_MAGAZINE", "RECEIPT", "SCREENSHOT", "TICKET", "IDENTITY", "NOTES", "PAYMENT_METHOD", "MENU", "RECIPE", name="documenttype"), nullable=True),
    sa.Column("object_type", sa.Enum("FOOD", "CAR", "BOAT", "PLANE", "PAINTING", "SCULPTURE", "DEVICE", "CLOTHING", "DRINK", "SPORTS", "DOCUMENT", "TOY", name="objecttype"), nullable=True),
    sa.Column("activity_type", sa.Enum("RUNNING", "SWIMMING", "CYCLING", "SOCCER", "BASKETBALL", "TENNIS", "BASEBALL", "SKATEBOARDING", "SURFING", "SKIING", "SNOWBOARDING", "GOLF", "HIKING", "CLIMBING", "KAYAKING", "YOGA", "PILATES", "WEIGHTLIFTING", "AEROBICS", "CROSSFIT", "DANCING", "PAINTING", "DRAWING", "PHOTOGRAPHY", "WRITING", "SCULPTING", "READING", "GARDENING", "COOKING", "BAKING", "FISHING", "BOARD_GAMES", "TRAVELING", "CAMPING", "BARBECUE", "SHOPPING", "DIVING", "SNORKELING", "ROWING", "WAKEBOARDING", "SAILING", "WORKING", "STUDYING", "RELAXING", "MEDITATING", name="activitytype"), nullable=True),
    sa.Column("event_type", sa.Enum("WEDDING", "BIRTHDAY", "ANNIVERSARY", "GRADUATION", "BABY_SHOWER", "HOUSEWARMING", "PARTY", "CONCERT", "FESTIVAL", "NIGHTCLUB", "MOVIE_NIGHT", "CONFERENCE", "WORKSHOP", "MEETING", "SEMINAR", "CORPORATE_EVENT", "FUNERAL", "RELIGIOUS_CEREMONY", "CULTURAL_CELEBRATION", "CHRISTMAS", "HALLOWEEN", "NEW_YEAR", "SPORTS_GAME", "TOURNAMENT", "MARATHON", "CHARITY_EVENT", "PROTEST", "PARADE", "EXHIBITION", "CARNIVAL", "TRIP", "PICNIC", "REUNION", "DATE", "WORK_EVENT", name="eventtype"), nullable=True),
    sa.Column("weather_condition", sa.Enum("CLEAR", "FAIR", "CLOUDY", "OVERCAST", "FOG", "FREEZING_FOG", "LIGHT_RAIN", "RAIN", "HEAVY_RAIN", "FREEZING_RAIN", "HEAVY_FREEZING_RAIN", "SLEET", "HEAVY_SLEET", "LIGHT_SNOWFALL", "SNOWFALL", "HEAVY_SNOWFALL", "RAIN_SHOWER", "HEAVY_RAIN_SHOWER", "SLEET_SHOWER", "HEAVY_SLEET_SHOWER", "SNOW_SHOWER", "HEAVY_SNOW_SHOWER", "LIGHTNING", "HAIL", "THUNDERSTORM", "HEAVY_THUNDERSTORM", "STORM", name="weathercondition"), nullable=True),
    sa.Column("is_outside", sa.Boolean(), nullable=False),
    sa.Column("is_landscape", sa.Boolean(), nullable=False),
    sa.Column("is_cityscape", sa.Boolean(), nullable=False),
    sa.Column("is_travel", sa.Boolean(), nullable=False),
    sa.Column("has_legible_text", sa.Boolean(), nullable=False),
    sa.Column("ocr_text", sa.Text(), nullable=True),
    sa.Column("document_summary", sa.Text(), nullable=True),
    sa.Column("summary", sa.String(), nullable=True),
    sa.Column("caption", sa.String(), nullable=False),
    sa.ForeignKeyConstraint(["image_id"], ["images.id"] ),
    sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("face_boxes",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("visual_information_id", sa.Integer(), nullable=True),
    sa.Column("unique_face_id", sa.Integer(), nullable=True),
    sa.Column("position", sa.ARRAY(sa.Float()), nullable=False),
    sa.Column("width", sa.Float(), nullable=False),
    sa.Column("height", sa.Float(), nullable=False),
    sa.Column("age", sa.Integer(), nullable=False),
    sa.Column("confidence", sa.Float(), nullable=False),
    sa.Column("sex", sa.Enum("MALE", "FEMALE", name="facesex"), nullable=False),
    sa.Column("mouth_left", sa.ARRAY(sa.Float()), nullable=False),
    sa.Column("mouth_right", sa.ARRAY(sa.Float()), nullable=False),
    sa.Column("nose_tip", sa.ARRAY(sa.Float()), nullable=False),
    sa.Column("eye_left", sa.ARRAY(sa.Float()), nullable=False),
    sa.Column("eye_right", sa.ARRAY(sa.Float()), nullable=False),
    sa.Column("embedding", VECTOR(512), nullable=False),
    sa.ForeignKeyConstraint(["unique_face_id"], ["unique_faces.id"] ),
    sa.ForeignKeyConstraint(["visual_information_id"], ["visual_information.id"] ),
    sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("object_boxes",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("visual_information_id", sa.Integer(), nullable=True),
    sa.Column("position", sa.ARRAY(sa.Float()), nullable=False),
    sa.Column("width", sa.Float(), nullable=False),
    sa.Column("height", sa.Float(), nullable=False),
    sa.Column("label", sa.String(), nullable=False),
    sa.Column("confidence", sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(["visual_information_id"], ["visual_information.id"] ),
    sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("ocr_boxes",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("visual_information_id", sa.Integer(), nullable=True),
    sa.Column("position", sa.ARRAY(sa.Float()), nullable=False),
    sa.Column("width", sa.Float(), nullable=False),
    sa.Column("height", sa.Float(), nullable=False),
    sa.Column("text", sa.String(), nullable=False),
    sa.Column("confidence", sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(["visual_information_id"], ["visual_information.id"] ),
    sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "emb_idx_2",
        "visual_information",
        ["embedding"],
        postgresql_using="vectors",
        postgresql_with={
            "options": f"$${IndexOption(index=Hnsw()).dumps()}$$",
        },
        postgresql_ops={"embedding": "vector_l2_ops"},
    )

    op.create_index(
        "face_emb_index",
        "face_boxes",
        ["embedding"],
        postgresql_using="vectors",
        postgresql_with={
            "options": f"$${IndexOption(index=Hnsw()).dumps()}$$",
        },
        postgresql_ops={"embedding": "vector_l2_ops"},
    )

    op.create_index(
        "centroid_index",
        "unique_faces",
        ["centroid"],
        postgresql_using="vectors",
        postgresql_with={
            "options": f"$${IndexOption(index=Hnsw()).dumps()}$$",
        },
        postgresql_ops={"centroid": "vector_l2_ops"},
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("ocr_boxes")
    op.drop_table("object_boxes")
    op.drop_table("face_boxes")
    op.drop_table("visual_information")
    op.drop_index(op.f("ix_images_relative_path"), table_name="images")
    op.drop_index(op.f("ix_images_id"), table_name="images")
    op.drop_index(op.f("ix_images_filename"), table_name="images")
    op.drop_index(op.f("ix_images_datetime_utc"), table_name="images")
    op.drop_index(op.f("ix_images_datetime_local"), table_name="images")
    op.drop_table("images")
    op.drop_table("users")
    op.drop_table("unique_faces")
    op.drop_table("geo_locations")
    # ### end Alembic commands ###
    op.drop_index("centroid_index", table_name="unique_faces")
    op.drop_index("face_emb_index", table_name="face_boxes")
    op.drop_index("emb_idx_2", table_name="visual_information")
    op.execute("DROP EXTENSION IF EXISTS vectors;")
