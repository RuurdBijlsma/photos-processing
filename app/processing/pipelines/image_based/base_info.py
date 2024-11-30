import os
import uuid
from pathlib import Path

from app.data.database.db_utils import rel_path
from app.data.interfaces.image_info_types import BaseImageInfo


def base_info(
    image_path: Path,
    image_hash: str,
) -> BaseImageInfo:
    return BaseImageInfo(
        id=uuid.uuid4().hex,
        relative_path=rel_path(image_path),
        filename=os.path.basename(image_path),
        hash=image_hash,
    )
