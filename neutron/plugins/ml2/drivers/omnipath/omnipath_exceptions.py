import paramiko

from neutron_lib.exceptions import InUse

from neutron._i18n import _


class FabricAgentCLIError(Exception):
    pass


class FabricAgentUnknownCommandError(Exception):
    pass


class FabricAgentSSHError(paramiko.SSHException):
    pass


class OmnipathPkeyInUse(InUse):
    """An exception indicating Omnipath network with Pkey creation failed because it's already in use.

    A specialization of the InUse exception indicating network creation failed
    because a specified Omnipath Pkey is already in use on the physical network.

    :param pkey: The Pkey value.
    :param physical_network: The physical network.
    """
    message = _("Unable to create the network. The Omnipath pkey %(pkey)s on physical network "
               "%(physical_network)s is in use.")
