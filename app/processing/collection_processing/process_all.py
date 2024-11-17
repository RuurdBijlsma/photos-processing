from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models.image_models import UserModel
from app.processing.cleanup.cleanup_thumbnails import cleanup_thumbnails
from app.processing.collection_processing.process_user import process_user_images


async def process_all(session: AsyncSession) -> None:
    users = (await session.execute(select(UserModel))).scalars().all()
    for user_id, username in [(user.id, user.username) for user in users]:
        await process_user_images(user_id, username, session)
    await cleanup_thumbnails(session)
