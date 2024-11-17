from pgvecto_rs.types import IndexOption, Hnsw


def upgrade(op):
    op.execute("CREATE EXTENSION IF NOT EXISTS vectors;")

    index_name = "emb_idx_2"
    op.create_index(
        index_name,
        "visual_information",
        ["embedding"],
        postgresql_using="vectors",
        postgresql_with={
            "options": f"$${IndexOption(index=Hnsw()).dumps()}$$"
        },
        postgresql_ops={"embedding": "vector_l2_ops"},
    )


def downgrade(op):
    op.drop_index("emb_idx_2", table_name="visual_information")
    op.execute("DROP EXTENSION IF EXISTS vectors;")
