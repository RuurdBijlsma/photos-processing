import asyncio
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray
from scipy.spatial.distance import cdist
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_config import app_config
from app.data.database.database import get_session
from app.data.image_models import (
    FaceBoxModel,
    ImageModel,
    UniqueFaceModel,
    VisualInformationModel,
)
from app.machine_learning.clustering.hdbscan_clustering import perform_clustering


def index_of_closest_embedding(
    embedding: NDArray[Any],
    embedding_list: NDArray[Any],
) -> int:
    embedding = embedding[np.newaxis, :]  # Add batch dimension
    similarities = 1 - cdist(embedding, embedding_list, metric="cosine")
    closest_index = np.argmax(similarities)
    return int(closest_index)


async def re_cluster_faces(session: AsyncSession) -> None:
    existing_unique_faces = (await session.execute(
        select(UniqueFaceModel)
        .where(UniqueFaceModel.user_provided_label.isnot(None)),
    )).scalars().all()
    await session.execute(update(FaceBoxModel).values(unique_face_id=None))
    await session.execute(delete(UniqueFaceModel))
    faces = (await session.execute(
        select(FaceBoxModel)
        .order_by(FaceBoxModel.id),
    )).scalars().all()
    if len(faces) < 1:
        return
    embeddings = np.vstack([face.embedding.to_numpy() for face in faces])
    cluster_labels = perform_clustering(
        embeddings,
        min_samples=2,
        min_cluster_size=4,
    )
    # make set of unique labels:
    unique_labels = np.unique(cluster_labels)
    unique_faces: list[UniqueFaceModel] = []
    # create UniqueFaceModel and insert it to db
    for label in unique_labels:
        if label == -1:
            continue
        # Filter faces by label and get embeddings
        label_faces = [face for face_label, face in
                       zip(cluster_labels, faces, strict=False) if face_label == label]
        label_embeddings = [face.embedding.to_numpy() for face in label_faces]

        unique_face = UniqueFaceModel(
            id=label,
            centroid=np.mean(label_embeddings, axis=0),
        )
        unique_faces.append(unique_face)
        session.add(unique_face)
        for face in label_faces:
            face.unique_face = unique_face
            session.add(face)

    for existing_unique_face in existing_unique_faces:
        centroids = np.vstack([face.centroid for face in unique_faces])
        closest_i = index_of_closest_embedding(
            existing_unique_face.centroid.to_numpy(),
            centroids,
        )
        unique_faces[closest_i].user_provided_label = (
            existing_unique_face.user_provided_label
        )

    await session.commit()


async def experiment(draw_face_experiment: bool = False) -> None:
    if not draw_face_experiment:
        async with get_session() as session:
            await re_cluster_faces(session)
        return

    async with get_session() as session:
        faces = (await session.execute(
            select(FaceBoxModel, ImageModel.relative_path)
            .join(FaceBoxModel.visual_information)
            .join(VisualInformationModel.image)
            .order_by(FaceBoxModel.id),
        )).all()
        embeddings = np.vstack([face[0].embedding.to_numpy() for face in faces])
        cluster_labels = perform_clustering(
            embeddings,
            min_samples=2,
            min_cluster_size=4,
        )

        for i, (face, relative_path_str) in enumerate(faces):
            relative_path = Path(relative_path_str)
            image = cv2.imread(str(app_config.images_dir / relative_path))
            if image is None:
                print(f"SKIP: {relative_path}")
                continue
            height, width, _ = image.shape
            x1 = int(face.position[0] * width)
            y1 = int(face.position[1] * height)
            x2 = int((face.position[0] + face.width) * width)
            y2 = int((face.position[1] + face.height) * height)
            cv2.rectangle(image,
                          (x1, y1),
                          (x2, y2),
                          (0, 255, 0),
                          2)
            print(f"Face ID: {face.id}, Image Relative Path: {relative_path}")

            label = cluster_labels[i]
            if label == -1:
                label = 9999
            out_path = (f"./test_img_out/face_"
                        f"{label}_i{i}_{relative_path.name}.jpg")
            cv2.imwrite(out_path, image)


if __name__ == "__main__":
    asyncio.run(experiment(draw_face_experiment=True))
