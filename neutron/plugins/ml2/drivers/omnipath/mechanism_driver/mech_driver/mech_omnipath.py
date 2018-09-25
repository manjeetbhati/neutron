import time

# from neutron_lib.db import api as db_api
from neutron_lib import context
from neutron_lib.callbacks import resources
from neutron_lib.plugins.ml2 import api
from oslo_log import log as logging

from neutron.db import provisioning_blocks
from neutron.objects import ports
# from neutron.objects import network
from neutron.plugins.ml2.drivers.omnipath import config
from neutron.plugins.ml2.drivers.omnipath.mechanism_driver.common.worker import OmnipathWorker
from neutron.plugins.ml2.drivers.omnipath.mechanism_driver.fabric_agent import FabricAgentClient

LOG = logging.getLogger(__name__)

sync_time = config.CONF.omnipath_config.POLL_INTERVAL


class OmnipathMechanismDriver(api.MechanismDriver):
    def __init__(self):
        self.opafmvf = FabricAgentClient()
        # sshank: Runs sync() every "sync_time" seconds
        OmnipathWorker(self.sync(), sync_time).start()

    def sync(self, guids_sync_info=None):
        """
        Get all of existing Ports from Neutron DB and sync.

        :param guids_sync_info:
        :return: status of sync operation
        """
        ctx = context.get_admin_context()
        ports_objects = ports.Port.get_objects(ctx)

        sync_dict = {}

        for port_object in ports_objects:
            port_id = port_object.id
            vf_name = port_object.network_id
            # TODO(sshank): Query Ironic/Nova DB to get the GUID for the physical node using port_id?
            guid = ""
            sync_dict[vf_name] = [guid]

        if guids_sync_info:
            for vf_name, guid in guids_sync_info:
                if vf_name not in sync_dict:
                    sync_dict[vf_name] = []
                sync_dict[vf_name].append(guid)

        try:
            status = self.opafmvf.full_sync(guids_sync_info)
        except Exception as e:
            LOG.error("Failed to do full sync %(exc)s", {'exc': e})
        else:
            # Send the newly added GUID vf_name info to the Fabric Agent to bind.
            return status

    @staticmethod
    def update_port_status_db(port_id, status):
        """
        Update Ports in DB

        :param port_id: ID of port to update status
        :param status: Status of the port
        :return: Updated Port Object
        """
        ctx = context.get_admin_context()
        return ports.Port.update_object(ctx, {'status': status}, port_id=port_id)

    def create_network_precommit(self, context):
        """Allocate resources for a new network.

        :param context: NetworkContext instance describing the new
        network.

        Create a new network, allocating resources as necessary in the
        database. Called inside transaction context on session. Call
        cannot block.  Raising an exception will result in a rollback
        of the current transaction.
        """
        pass

    def create_network_postcommit(self, context):
        """Create a network.

        :param context: NetworkContext instance describing the new
        network.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Raising an exception will
        cause the deletion of the resource.
        """
        network = context.current
        network_id = network['id']
        provider_type = network['provider:network_type']
        pkey = network['provider:segmentation_id']
        physnet = network['provider:physical_network']

        if provider_type == "omnipath" and pkey:
            # TODO(sshank): Associate pkey with Network ID in DB?
            try:
                status = self.opafmvf.cli.osfa_config_commands("create", network_id, pkey)
                if status == "2":
                    raise Exception
            except Exception as e:
                LOG.error("Failed to create network %(network_id)s with pkey %(pkey)s caused by %(exc)s",
                          {'network_id': network_id, 'pkey': pkey, 'exc': e})

    def update_network_precommit(self, context):
        """Update resources of a network.

        :param context: NetworkContext instance describing the new
        state of the network, as well as the original state prior
        to the update_network call.

        Update values of a network, updating the associated resources
        in the database. Called inside transaction context on session.
        Raising an exception will result in rollback of the
        transaction.

        update_network_precommit is called for all changes to the
        network state. It is up to the mechanism driver to ignore
        state or state changes that it does not know or care about.
        """
        pass

    def update_network_postcommit(self, context):
        """Update a network.

        :param context: NetworkContext instance describing the new
        state of the network, as well as the original state prior
        to the update_network call.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Raising an exception will
        cause the deletion of the resource.

        update_network_postcommit is called for all changes to the
        network state.  It is up to the mechanism driver to ignore
        state or state changes that it does not know or care about.
        """
        # TODO(sshank): Is Network update required for OPA?
        pass

    def delete_network_precommit(self, context):
        """Delete resources for a network.

        :param context: NetworkContext instance describing the current
        state of the network, prior to the call to delete it.

        Delete network resources previously allocated by this
        mechanism driver for a network. Called inside transaction
        context on session. Runtime errors are not expected, but
        raising an exception will result in rollback of the
        transaction.
        """
        pass

    def delete_network_postcommit(self, context):
        """Delete a network.

        :param context: NetworkContext instance describing the current
        state of the network, prior to the call to delete it.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Runtime errors are not
        expected, and will not prevent the resource from being
        deleted.
        """
        network = context.current
        network_id = network['id']
        provider_type = network['provider:network_type']
        pkey = network['provider:segmentation_id']
        physnet = network['provider:physical_network']

        if provider_type == "omnipath" and pkey:
            # TODO(sshank): Dissociate pkey with Network ID in DB?
            try:
                status = self.opafmvf.cli.osfa_config_commands("delete", network_id)
                if status == "2":
                    raise Exception
            except Exception as e:
                LOG.error("Failed to delete network %(network_id)s caused by %(exc)s",
                          {'network_id': network_id, 'exc': e})

    def create_subnet_precommit(self, context):
        """Allocate resources for a new subnet.

        :param context: SubnetContext instance describing the new
        subnet.
        rt = context.current
        device_id = port['device_id']
        device_owner = port['device_owner']
        Create a new subnet, allocating resources as necessary in the
        database. Called inside transaction context on session. Call
        cannot block.  Raising an exception will result in a rollback
        of the current transaction.
        """
        pass

    def create_subnet_postcommit(self, context):
        """Create a subnet.

        :param context: SubnetContext instance describing the new
        subnet.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Raising an exception will
        cause the deletion of the resource.
        """
        pass

    def update_subnet_precommit(self, context):
        """Update resources of a subnet.

        :param context: SubnetContext instance describing the new
        state of the subnet, as well as the original state prior
        to the update_subnet call.

        Update values of a subnet, updating the associated resources
        in the database. Called inside transaction context on session.
        Raising an exception will result in rollback of the
        transaction.

        update_subnet_precommit is called for all changes to the
        subnet state. It is up to the mechanism driver to ignore
        state or state changes that it does not know or care about.
        """
        pass

    def update_subnet_postcommit(self, context):
        """Update a subnet.

        :param context: SubnetContext instance describing the new
        state of the subnet, as well as the original state prior
        to the update_subnet call.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Raising an exception will
        cause the deletion of the resource.

        update_subnet_postcommit is called for all changes to the
        subnet state.  It is up to the mechanism driver to ignore
        state or state changes that it does not know or care about.
        """
        pass

    def delete_subnet_precommit(self, context):
        """Delete resources for a subnet.

        :param context: SubnetContext instance describing the current
        state of the subnet, prior to the call to delete it.

        Delete subnet resources previously allocated by this
        mechanism driver for a subnet. Called inside transaction
        context on session. Runtime errors are not expected, but
        raising an exception will result in rollback of the
        transaction.
        """
        pass

    def delete_subnet_postcommit(self, context):
        """Delete a subnet.

        :param context: SubnetContext instance describing the current
        state of the subnet, prior to the call to delete it.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Runtime errors are not
        expected, and will not prevent the resource from being
        deleted.
        """
        pass

    def create_port_precommit(self, context):
        """Allocate resources for a new port.

        :param context: PortContext instance describing the port.

        Create a new port, allocating resources as necessary in the
        database. Called inside transaction context on session. Call
        cannot block.  Raising an exception will result in a rollback
        of the current transaction.
        """
        pass

    def create_port_postcommit(self, context):
        """Create a port.

        :param context: PortContext instance describing the port.

        Called after the transaction completes. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance.  Raising an exception will
        result in the deletion of the resource.
        """
        pass

    def update_port_precommit(self, context):
        """Update resources of a port.

        :param context: PortContext instance describing the new
        state of the port, as well as the original state prior
        to the update_port call.

        Called inside transaction context on session to complete a
        port update as defined by this mechanism driver. Raising an
        exception will result in rollback of the transaction.

        update_port_precommit is called for all changes to the port
        state. It is up to the mechanism driver to ignore state or
        state changes that it does not know or care about.
        """
        pass

    def update_port_postcommit(self, context):
        """Update a port.

        :param context: PortContext instance describing the new
        state of the port, as well as the original state prior
        to the update_port call.

        Called after the transaction completes. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance.  Raising an exception will
        result in the deletion of the resource.

        update_port_postcommit is called for all changes to the port
        state. It is up to the mechanism driver to ignore state or
        state changes that it does not know or care about.
        """
        port = context.current

        # Get VF name from network context
        vf_name = context.network.current['name']

        # Get binding profile from port context
        binding_profile = port['binding:profile']

        # Get GUID which is essentially the physical server's ID.
        guid = binding_profile.get('guid')

        try:
            port_bind_status = self.opafmvf.get_port_status(vf_name, guid)

            # Keep running until the status of the particular Port changes to "UP".
            while port_bind_status != "UP":
                port_bind_status = self.opafmvf.get_port_status(vf_name, guid)

            # Update Neutron DB list of Ports with the updated list got from Open Management Agent.
            self.update_port_status_db(port_bind_status, port['id'])

            # Remove provisioning block for the port
            provisioning_blocks.provisioning_complete(
                context._plugin_context, port['id'], resources.PORT,
                "omnipath")

        except Exception as e:
            LOG.error("Failed to do update port: "
                      "%(port_id)s due to %(exc)s", {'port_id': port['id'], 'exc': e})

    def delete_port_precommit(self, context):
        """Delete resources of a port.

        :param context: PortContext instance describing the current
        state of the port, prior to the call to delete it.

        Called inside transaction context on session. Runtime errors
        are not expected, but raising an exception will result in
        rollback of the transaction.
        """
        pass

    def delete_port_postcommit(self, context):
        """Delete a port.

        :param context: PortContext instance describing the current
        state of the port, prior to the call to delete it.

        Called after the transaction completes. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance.  Runtime errors are not
        expected, and will not prevent the resource from being
        deleted.
        """
        port = context.current

        # Remove port from DB. Once removed, it will be synced every "sync_time" as done in
        # __init__
        ctx = context.get_admin_context()
        ports.Port.delete_objects(ctx, port_id=port['id'])

    def bind_port(self, context):
        """Attempt to bind a port.

        :param context: PortContext instance describing the port

        This method is called outside any transaction to attempt to
        establish a port binding using this mechanism driver. Bindings
        may be created at each of multiple levels of a hierarchical
        network, and are established from the top level downward. At
        each level, the mechanism driver determines whether it can
        bind to any of the network segments in the
        context.segments_to_bind property, based on the value of the
        context.host property, any relevant port or network
        attributes, and its own knowledge of the network topology. At
        the top level, context.segments_to_bind contains the static
        segments of the port's network. At each lower level of
        binding, it contains static or dynamic segments supplied by
        the driver that bound at the level above. If the driver is
        able to complete the binding of the port to any segment in
        context.segments_to_bind, it must call context.set_binding
        with the binding details. If it can partially bind the port,
        it must call context.continue_binding with the network
        segments to be used to bind at the next lower level.

        If the binding results are committed after bind_port returns,
        they will be seen by all mechanism drivers as
        update_port_precommit and update_port_postcommit calls. But if
        some other thread or process concurrently binds or updates the
        port, these binding results will not be committed, and
        update_port_precommit and update_port_postcommit will not be
        called on the mechanism drivers with these results. Because
        binding results can be discarded rather than committed,
        drivers should avoid making persistent state changes in
        bind_port, or else must ensure that such state changes are
        eventually cleaned up.

        Implementing this method explicitly declares the mechanism
        driver as having the intention to bind ports. This is inspected
        by the QoS service to identify the available QoS rules you
        can use with ports.
        """
        port = context.current

        # Get VF name from network context
        vf_name = context.network.current['name']

        # Get binding profile from port context
        binding_profile = port['binding:profile']

        # Get GUID which is essentially the physical server's ID.
        guid = binding_profile.get('guid')

        self.sync({vf_name: guid})
