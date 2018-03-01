# pylint: disable=E1101

"""Create Icocountdown Table

Revision ID: b87e3608e7e3
Revises: 59fc518943ef
Create Date: 2018-03-01 13:10:02.806927

"""

# Core Dependencies
from datetime import datetime

# Other Dependencies
from alembic import op
from sqlalchemy import Column, Integer, String, TEXT, TIMESTAMP


# Revision identifiers, used by Alembic.
revision = 'b87e3608e7e3'
down_revision = '59fc518943ef'
branch_labels = None
depends_on = None

# Table Name Constant
TABLE = "icocountdown"

def upgrade():
  """Migration Up"""
  op.create_table(
    TABLE,
    Column( "id", Integer, primary_key = True, autoincrement = True ),
    Column( "created", TIMESTAMP, nullable = False, default = datetime.now ),
    Column( "name", String(100), nullable = False ),
    Column( "start", TIMESTAMP, nullable = False ),
    Column( "end", TIMESTAMP, nullable = False ),
    Column( "site", String(100), nullable = False ),
    Column( "description", TEXT, nullable = False ),
    Column( "presale_start", TIMESTAMP, nullable = False ),
    Column( "presale_end", TIMESTAMP, nullable = False )
  )


def downgrade():
  """Migration Down"""
  op.drop_table(TABLE)
