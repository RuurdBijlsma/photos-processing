from photos.data.interfaces.image_info_types import DominantColorImageInfo, DataUrlImageInfo


def add_dominant_color(image_info: DataUrlImageInfo) -> DominantColorImageInfo:
    return DominantColorImageInfo(
        **image_info.model_dump(),
        dominant_colors=["hi", 'HI', 'hi']
    )
