"""Add learning progress tables

Revision ID: d320f16aa387
Revises: 96e174832c9c
Create Date: 2025-05-28 08:09:13.599980

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd320f16aa387'
down_revision = '96e174832c9c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('learning_paths',
    sa.Column('path_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('created_by', sa.String(length=36), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('path_id')
    )
    op.create_table('learning_path_contents',
    sa.Column('path_content_id', sa.String(length=36), nullable=False),
    sa.Column('path_id', sa.String(length=36), nullable=False),
    sa.Column('content_id', sa.String(length=36), nullable=False),
    sa.Column('order_index', sa.Integer(), nullable=False),
    sa.Column('is_required', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['content_id'], ['contents.content_id'], ),
    sa.ForeignKeyConstraint(['path_id'], ['learning_paths.path_id'], ),
    sa.PrimaryKeyConstraint('path_content_id')
    )
    op.add_column('learning_assignments', sa.Column('assigned_by', sa.String(length=36), nullable=False))
    op.add_column('learning_assignments', sa.Column('assigned_at', sa.DateTime(), nullable=False))
    op.add_column('learning_assignments', sa.Column('is_mandatory', sa.Boolean(), nullable=False))
    op.add_column('learning_assignments', sa.Column('notes', sa.String(length=500), nullable=True))
    op.alter_column('learning_assignments', 'user_id',
               existing_type=mysql.VARCHAR(length=36),
               nullable=False)
    op.alter_column('learning_assignments', 'content_id',
               existing_type=mysql.VARCHAR(length=36),
               nullable=False)
    op.drop_index(op.f('ix_learning_assignments_assignment_id'), table_name='learning_assignments')
    op.create_foreign_key(None, 'learning_assignments', 'users', ['assigned_by'], ['user_id'])
    op.drop_column('learning_assignments', 'status')
    op.drop_column('learning_assignments', 'updated_at')
    op.drop_column('learning_assignments', 'completed_at')
    op.drop_column('learning_assignments', 'created_at')
    op.add_column('learning_progress', sa.Column('user_id', sa.String(length=36), nullable=False))
    op.add_column('learning_progress', sa.Column('content_id', sa.String(length=36), nullable=False))
    op.add_column('learning_progress', sa.Column('time_spent_minutes', sa.Integer(), nullable=False))
    op.add_column('learning_progress', sa.Column('is_completed', sa.Boolean(), nullable=False))
    op.add_column('learning_progress', sa.Column('started_at', sa.DateTime(), nullable=False))
    op.add_column('learning_progress', sa.Column('completed_at', sa.DateTime(), nullable=True))
    op.alter_column('learning_progress', 'progress_percentage',
               existing_type=mysql.INTEGER(),
               type_=sa.Float(),
               nullable=False)
    op.alter_column('learning_progress', 'last_accessed_at',
               existing_type=mysql.DATETIME(),
               nullable=False)
    op.drop_index(op.f('ix_learning_progress_progress_id'), table_name='learning_progress')
    op.drop_constraint(op.f('learning_progress_ibfk_1'), 'learning_progress', type_='foreignkey')
    op.create_foreign_key(None, 'learning_progress', 'contents', ['content_id'], ['content_id'])
    op.create_foreign_key(None, 'learning_progress', 'users', ['user_id'], ['user_id'])
    op.drop_column('learning_progress', 'updated_at')
    op.drop_column('learning_progress', 'assignment_id')
    op.drop_column('learning_progress', 'created_at')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('learning_progress', sa.Column('created_at', mysql.DATETIME(), nullable=False))
    op.add_column('learning_progress', sa.Column('assignment_id', mysql.VARCHAR(length=36), nullable=True))
    op.add_column('learning_progress', sa.Column('updated_at', mysql.DATETIME(), nullable=False))
    op.drop_constraint(None, 'learning_progress', type_='foreignkey')
    op.drop_constraint(None, 'learning_progress', type_='foreignkey')
    op.create_foreign_key(op.f('learning_progress_ibfk_1'), 'learning_progress', 'learning_assignments', ['assignment_id'], ['assignment_id'])
    op.create_index(op.f('ix_learning_progress_progress_id'), 'learning_progress', ['progress_id'], unique=False)
    op.alter_column('learning_progress', 'last_accessed_at',
               existing_type=mysql.DATETIME(),
               nullable=True)
    op.alter_column('learning_progress', 'progress_percentage',
               existing_type=sa.Float(),
               type_=mysql.INTEGER(),
               nullable=True)
    op.drop_column('learning_progress', 'completed_at')
    op.drop_column('learning_progress', 'started_at')
    op.drop_column('learning_progress', 'is_completed')
    op.drop_column('learning_progress', 'time_spent_minutes')
    op.drop_column('learning_progress', 'content_id')
    op.drop_column('learning_progress', 'user_id')
    op.add_column('learning_assignments', sa.Column('created_at', mysql.DATETIME(), nullable=False))
    op.add_column('learning_assignments', sa.Column('completed_at', mysql.DATETIME(), nullable=True))
    op.add_column('learning_assignments', sa.Column('updated_at', mysql.DATETIME(), nullable=False))
    op.add_column('learning_assignments', sa.Column('status', mysql.VARCHAR(length=20), nullable=False))
    op.drop_constraint(None, 'learning_assignments', type_='foreignkey')
    op.create_index(op.f('ix_learning_assignments_assignment_id'), 'learning_assignments', ['assignment_id'], unique=False)
    op.alter_column('learning_assignments', 'content_id',
               existing_type=mysql.VARCHAR(length=36),
               nullable=True)
    op.alter_column('learning_assignments', 'user_id',
               existing_type=mysql.VARCHAR(length=36),
               nullable=True)
    op.drop_column('learning_assignments', 'notes')
    op.drop_column('learning_assignments', 'is_mandatory')
    op.drop_column('learning_assignments', 'assigned_at')
    op.drop_column('learning_assignments', 'assigned_by')
    op.drop_table('learning_path_contents')
    op.drop_table('learning_paths')
    # ### end Alembic commands ###