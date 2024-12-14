from collections.abc import Sequence
from datetime import datetime

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Query

from app.data.database.database import SessionDep
from app.data.image_models import ImageModel
from app.data.interfaces.response_types import GridImageData
from app.routers.images.images_model import get_month_photos

images_router = APIRouter(prefix="/images", tags=["images"])


def default_start_date(n_months: int) -> datetime:
    now = datetime.now()
    start_of_month = (now - relativedelta(months=n_months)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return start_of_month


@images_router.get("/", response_model=list[GridImageData])
async def get_at_date(
        # _: UserDep,
        session: SessionDep,
        start_date: datetime = Query(default_factory=lambda: default_start_date(10)),
        end_date: datetime | None = Query(default=None),
) -> Sequence[ImageModel]:
    return await get_month_photos(session, start_date, end_date)
