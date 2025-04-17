"""Add gitlab_merge_request_jobs, comments, reactions tables

Revision ID: 6899db36b88f
Revises: 70466f47f936
Create Date: 2025-04-17 13:54:43.827678

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6899db36b88f"
down_revision: Union[str, None] = "70466f47f936"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "gitlab_merge_request_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "forge",
            sa.Enum("gitlab_com", "gitlab_cee_redhat_com", name="forge"),
            nullable=False,
            comment="The forge name",
        ),
        sa.Column(
            "project_id", sa.Integer(), nullable=False, comment="The project gitlab id"
        ),
        sa.Column(
            "mr_iid",
            sa.Integer(),
            nullable=False,
            comment="The merge request gitlab iid",
        ),
        sa.Column("job_id", sa.Integer(), nullable=False, comment="The job gitlab id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("forge", "job_id", name="uix_forge_job"),
        sa.UniqueConstraint(
            "forge", "project_id", "mr_iid", "job_id", name="uix_mr_project_job"
        ),
    )
    op.create_index(
        op.f("ix_gitlab_merge_request_jobs_forge"),
        "gitlab_merge_request_jobs",
        ["forge"],
        unique=False,
    )
    op.create_index(
        op.f("ix_gitlab_merge_request_jobs_job_id"),
        "gitlab_merge_request_jobs",
        ["job_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_gitlab_merge_request_jobs_project_id"),
        "gitlab_merge_request_jobs",
        ["project_id"],
        unique=False,
    )
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "merge_request_job_id",
            sa.Integer(),
            nullable=False,
            comment="The associated merge request job (db) id",
        ),
        sa.Column(
            "forge",
            sa.Enum("gitlab_com", "gitlab_cee_redhat_com", name="forge"),
            nullable=False,
            comment="The forge name",
        ),
        sa.Column(
            "comment_id",
            sa.String(length=50),
            nullable=False,
            comment="The comment gitlab id",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            comment="Timestamp when the comment was created",
        ),
        sa.ForeignKeyConstraint(
            ["merge_request_job_id"],
            ["gitlab_merge_request_jobs.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("forge", "comment_id", name="uix_forge_comment_id"),
    )
    op.create_index(
        op.f("ix_comments_comment_id"), "comments", ["comment_id"], unique=False
    )
    op.create_index(op.f("ix_comments_forge"), "comments", ["forge"], unique=False)
    op.create_index(
        op.f("ix_comments_merge_request_job_id"),
        "comments",
        ["merge_request_job_id"],
        unique=True,
    )
    op.create_table(
        "reactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "comment_id",
            sa.Integer(),
            nullable=False,
            comment="The associated comment (db) id",
        ),
        sa.Column(
            "reaction_type",
            sa.String(length=127),
            nullable=False,
            comment="The type of reaction",
        ),
        sa.Column(
            "count",
            sa.Integer(),
            nullable=False,
            comment="The number of reactions, of this type, given in the comment",
        ),
        sa.ForeignKeyConstraint(
            ["comment_id"],
            ["comments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("comment_id", "reaction_type", name="uix_comment_reaction"),
    )
    op.create_index(
        op.f("ix_reactions_comment_id"), "reactions", ["comment_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_reactions_comment_id"), table_name="reactions")
    op.drop_table("reactions")
    op.drop_index(op.f("ix_comments_merge_request_job_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_forge"), table_name="comments")
    op.drop_index(op.f("ix_comments_comment_id"), table_name="comments")
    op.drop_table("comments")
    op.drop_index(
        op.f("ix_gitlab_merge_request_jobs_project_id"),
        table_name="gitlab_merge_request_jobs",
    )
    op.drop_index(
        op.f("ix_gitlab_merge_request_jobs_job_id"),
        table_name="gitlab_merge_request_jobs",
    )
    op.drop_index(
        op.f("ix_gitlab_merge_request_jobs_forge"),
        table_name="gitlab_merge_request_jobs",
    )
    op.drop_table("gitlab_merge_request_jobs")
    # ### end Alembic commands ###
