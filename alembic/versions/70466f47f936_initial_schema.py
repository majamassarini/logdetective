"""Initial Schema

Revision ID: 70466f47f936
Revises:
Create Date: 2025-03-27 13:52:01.306405

"""

from typing import Sequence, Union
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "70466f47f936"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "analyze_request_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "endpoint",
            sa.Enum("ANALYZE", "ANALYZE_STAGED", "ANALYZE_STREAM", name="endpointtype"),
            nullable=False,
            comment="The service endpoint that was called",
        ),
        sa.Column(
            "request_received_at",
            sa.DateTime(),
            nullable=False,
            comment="Timestamp when the request was received",
        ),
        sa.Column(
            "log_url",
            sa.String(),
            nullable=False,
            comment="Log url for which analysis was requested",
        ),
        sa.Column(
            "response_sent_at",
            sa.DateTime(),
            nullable=True,
            comment="Timestamp when the response was sent back",
        ),
        sa.Column(
            "response_length",
            sa.Integer(),
            nullable=True,
            comment="Length of the response in chars",
        ),
        sa.Column(
            "response_certainty",
            sa.Float(),
            nullable=True,
            comment="Certainty for generated response",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_analyze_request_metrics_endpoint"),
        "analyze_request_metrics",
        ["endpoint"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analyze_request_metrics_request_received_at"),
        "analyze_request_metrics",
        ["request_received_at"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_analyze_request_metrics_request_received_at"),
        table_name="analyze_request_metrics",
    )
    op.drop_index(
        op.f("ix_analyze_request_metrics_endpoint"),
        table_name="analyze_request_metrics",
    )
    op.drop_table("analyze_request_metrics")
    # ### end Alembic commands ###
