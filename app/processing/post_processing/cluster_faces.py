import asyncio
import os

import cv2
import numpy as np
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_config import app_config
from app.data.database.database import get_session
from app.data.image_models import FaceBoxModel, VisualInformationModel, ImageModel, \
    UniqueFaceModel
from app.machine_learning.clustering.hdbscan_clustering import perform_clustering


async def cluster_faces(session: AsyncSession) -> None:
    # TODO:
    #   Preserve user provided labels for new clusters
    await session.execute(delete(UniqueFaceModel))
    faces = (await session.execute(
        select(FaceBoxModel)
        .order_by(FaceBoxModel.id)
    )).scalars().all()
    embeddings = np.vstack([face.embedding.to_numpy() for face in faces])
    cluster_labels = perform_clustering(
        embeddings,
        min_samples=2,
        min_cluster_size=4
    )
    # make set of unique labels:
    unique_labels = np.unique(cluster_labels)
    # create UniqueFaceModel and insert it to db
    for label in unique_labels:
        if label == -1:
            continue
        # Filter faces by label and extract embeddings
        label_faces = [face for face_label, face in
                       zip(cluster_labels, faces) if face_label == label]
        label_embeddings = [face.embedding.to_numpy() for face in label_faces]

        unique_face = UniqueFaceModel(
            id=label,
            centroid=np.mean(label_embeddings, axis=0),
        )
        session.add(unique_face)
        for face in label_faces:
            face.unique_face = unique_face
            session.add(face)

    await session.commit()


async def experiment(draw_face_experiment: bool = False):
    if not draw_face_experiment:
        async with get_session() as session:
            await cluster_faces(session)
        return

    async with get_session() as session:
        faces = (await session.execute(
            select(FaceBoxModel, ImageModel.relative_path)
            .join(FaceBoxModel.visual_information)
            .join(VisualInformationModel.image)
            .order_by(FaceBoxModel.id)
        )).all()
        embeddings = np.vstack([face[0].embedding.to_numpy() for face in faces])
        cluster_labels = perform_clustering(
            embeddings,
            min_samples=2,
            min_cluster_size=4
        )

        for i, (face, relative_path) in enumerate(faces):
            image = cv2.imread(app_config.images_dir / relative_path)
            if image is None:
                print(f"SKIP: {relative_path}")
                continue
            height, width, channels = image.shape
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
                        f"{label}_i{i}_{os.path.basename(relative_path)}.jpg")
            cv2.imwrite(out_path, image)


if __name__ == "__main__":
    asyncio.run(experiment(draw_face_experiment=True))
