from neutron_lib.db import model_base
import sqlalchemy as sa


class OmniPathPKeyAllocation(model_base.BASEV2):
    __tablename__ = 'ml2_omnipathpkey_allocations'
    __table_args__ = (
        sa.Index('ix_ml2_omnipathpkey_allocations_physical_network_allocated',
                 'physical_network', 'allocated'),
        model_base.BASEV2.__table_args__,)

    physical_network = sa.Column(sa.String(64), nullable=False,
                                 primary_key=True)
    p_key = sa.Column(sa.Integer, nullable=False, primary_key=True,
                        autoincrement=False)
    allocated = sa.Column(sa.Boolean, nullable=False)
