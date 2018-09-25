from neutron_lib.db import model_base
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


class OmniPathRevisionNumbers(model_base.BASEV2):
    __tablename__ = 'omnipath_revision_numbers'
    __table_args__ = (
        model_base.BASEV2.__table_args__
    )
    standard_attr_id = sa.Column(
        sa.BigInteger().with_variant(sa.Integer(), 'sqlite'),
        sa.ForeignKey('standardattributes.id', ondelete='SET NULL'),
        nullable=True)
    resource_uuid = sa.Column(sa.String(36), nullable=False, primary_key=True)
    resource_type = sa.Column(sa.String(36), nullable=False, primary_key=True)
    revision_number = sa.Column(
        sa.BigInteger().with_variant(sa.Integer(), 'sqlite'),
        default=0, nullable=False)
    created_at = sa.Column(
        sa.DateTime().with_variant(
            sqlite.DATETIME(truncate_microseconds=True), 'sqlite'),
        default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.TIMESTAMP, default=sa.func.now(),
                           onupdate=sa.func.now(), nullable=True)

