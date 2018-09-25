from oslo_versionedobjects import fields as obj_fields

from neutron.objects import base
from neutron.plugins.ml2.drivers.omnipath.type_driver.db import models as pkey_alloc_model


@base.NeutronObjectRegistry.register
class OmniPathPKeyAllocation(base.NeutronDbObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    db_model = pkey_alloc_model.OmniPathPKeyAllocation

    fields = {
        'physical_network': obj_fields.StringField(),
        'pkey': obj_fields.StringField(),
        'allocated': obj_fields.BooleanField(),
    }

    primary_keys = ['physical_network', 'pkey']
