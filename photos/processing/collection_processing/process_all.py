from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from photos.data.models.image_models import UserModel
from photos.processing.cleanup.cleanup_thumbnails import cleanup_thumbnails
from photos.processing.collection_processing.process_user import process_user_images


async def process_all(session: AsyncSession) -> None:
    result = await session.stream_scalars(select(UserModel))
    async for user in result:
        assert isinstance(user, UserModel)
        await process_user_images(user.id, user.username, session)
    await cleanup_thumbnails(session)
