"""Initial migration with all tables

Revision ID: c44b7eb9fbad
Revises: 
Create Date: 2025-05-28 04:19:23.255891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c44b7eb9fbad'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('category_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('parent_id', sa.String(length=36), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['categories.category_id'], ),
    sa.PrimaryKeyConstraint('category_id')
    )
    op.create_index(op.f('ix_categories_category_id'), 'categories', ['category_id'], unique=False)
    op.create_table('users',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('google_user_id', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('display_name', sa.String(length=100), nullable=False),
    sa.Column('department', sa.String(length=100), nullable=True),
    sa.Column('position', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_google_user_id'), 'users', ['google_user_id'], unique=True)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_table('contents',
    sa.Column('content_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category_id', sa.String(length=36), nullable=True),
    sa.Column('content_type', sa.String(length=50), nullable=False),
    sa.Column('file_path', sa.String(length=500), nullable=True),
    sa.Column('duration_minutes', sa.Integer(), nullable=True),
    sa.Column('is_published', sa.Boolean(), nullable=False),
    sa.Column('created_by', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.category_id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('content_id')
    )
    op.create_index(op.f('ix_contents_content_id'), 'contents', ['content_id'], unique=False)
    op.create_table('learning_assignments',
    sa.Column('assignment_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=True),
    sa.Column('content_id', sa.String(length=36), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['content_id'], ['contents.content_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('assignment_id')
    )
    op.create_index(op.f('ix_learning_assignments_assignment_id'), 'learning_assignments', ['assignment_id'], unique=False)
    op.create_table('learning_progress',
    sa.Column('progress_id', sa.String(length=36), nullable=False),
    sa.Column('assignment_id', sa.String(length=36), nullable=True),
    sa.Column('progress_percentage', sa.Integer(), nullable=True),
    sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['assignment_id'], ['learning_assignments.assignment_id'], ),
    sa.PrimaryKeyConstraint('progress_id')
    )
    op.create_index(op.f('ix_learning_progress_progress_id'), 'learning_progress', ['progress_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_learning_progress_progress_id'), table_name='learning_progress')
    op.drop_table('learning_progress')
    op.drop_index(op.f('ix_learning_assignments_assignment_id'), table_name='learning_assignments')
    op.drop_table('learning_assignments')
    op.drop_index(op.f('ix_contents_content_id'), table_name='contents')
    op.drop_table('contents')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_google_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_categories_category_id'), table_name='categories')
    op.drop_table('categories')
    # ### end Alembic commands ###