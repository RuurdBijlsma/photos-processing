from pgvecto_rs.types import IndexOption, Hnsw


def upgrade(op):
    op.execute("CREATE EXTENSION IF NOT EXISTS vectors;")

    op.create_index(
        "emb_idx_2",
        "visual_information",
        ["embedding"],
        postgresql_using="vectors",
        postgresql_with={
            "options": f"$${IndexOption(index=Hnsw()).dumps()}$$"
        },
        postgresql_ops={"embedding": "vector_l2_ops"},
    )

    op.create_index(
        "face_emb_index",
        "face_boxes",
        ["embedding"],
        postgresql_using="vectors",
        postgresql_with={
            "options": f"$${IndexOption(index=Hnsw()).dumps()}$$"
        },
        postgresql_ops={"embedding": "vector_l2_ops"},
    )

    op.create_index(
        "centroid_index",
        "unique_faces",
        ["centroid"],
        postgresql_using="vectors",
        postgresql_with={
            "options": f"$${IndexOption(index=Hnsw()).dumps()}$$"
        },
        postgresql_ops={"centroid": "vector_l2_ops"},
    )


def downgrade(op):
    op.drop_index("centroid_index", table_name="unique_faces")
    op.drop_index("face_emb_index", table_name="face_boxes")
    op.drop_index("emb_idx_2", table_name="visual_information")
    op.execute("DROP EXTENSION IF EXISTS vectors;")
