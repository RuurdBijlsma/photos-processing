

def upgrade(op):
    op.execute("CREATE EXTENSION IF NOT EXISTS vectors;")


def downgrade(op):
    op.execute("DROP EXTENSION IF EXISTS vectors;")
