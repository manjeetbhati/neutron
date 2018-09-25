import paramiko

from oslo_log import log as logging

from neutron.plugins.ml2.drivers.omnipath import config
from neutron.plugins.ml2.drivers.omnipath import omnipath_exceptions

LOG = logging.getLogger(__name__)
OPA_BINARY = "opafmvf"


class FabricAgentCLI(object):
    def __init__(self):
        self._agent_hostname = None
        self._agent_username = None
        self._agent_key_path = None

        self._read_config()

        self.client = paramiko.SSHClient()
        self.connect()

    def _read_config(self):
        self._agent_hostname = config.CONF.omnipath_config.IP_ADDRESS
        LOG.debug("Fabric Agent IP address: %s", self._agent_hostname)
        self._agent_username = config.CONF.omnipath_config.USERNAME
        self._agent_key_path = config.CONF.omnipath_config.KEY

    def connect(self):
        try:
            key = paramiko.RSAKey.from_private_key_file(self._agent_key_path)
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                self._agent_hostname, port=22, username=self._agent_username, pkey=key)
        except omnipath_exceptions.FabricAgentSSHError:
            LOG.error("Error connecting to Omnipath FM")

    def execute_command(self, command):
        # out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # stdout, stderr = out.communicate()
        stdin, stdout, stderr = self.client.exec_command(command)
        if stderr:
            raise omnipath_exceptions.FabricAgentCLIError
        return stdout.read()

    def osfa_config_commands(self, command, vf_name, *args):
        try:
            if command == "create":
                cmd = [OPA_BINARY, "create", vf_name]
            elif command == "delete":
                cmd = [OPA_BINARY, "delete", vf_name]
            elif command == "add":
                cmd = [OPA_BINARY, "add", vf_name, "".join(str(x + " ") for x in args).rstrip()]
            elif command == "remove":
                cmd = [OPA_BINARY, "remove", vf_name, "".join(str(x + " ") for x in args).rstrip()]
            else:
                raise omnipath_exceptions.FabricAgentUnknownCommandError
            return self.execute_command(cmd)
        except omnipath_exceptions.FabricAgentUnknownCommandError:
            LOG.error(command + " not supported in opafmvf CLI")

    def osfa_query_commands(self, command, vf_name, *args):
        try:
            if command == "exist":
                cmd = [OPA_BINARY, "exist", vf_name]
            elif command == "ismember":
                cmd = [OPA_BINARY, "ismember", vf_name, "".join(str(x + " ") for x in args).rstrip()]
            elif command == "isnotmember":
                cmd = [OPA_BINARY, "isnotmember", vf_name, "".join(str(x + " ") for x in args).rstrip()]
            else:
                raise omnipath_exceptions.FabricAgentUnknownCommandError
            return self.execute_command(cmd)
        except omnipath_exceptions.FabricAgentUnknownCommandError:
            LOG.error(command + " not supported in opafmvf CLI")

    def osfa_management_commands(self, command):
        try:
            if command == "reset":
                cmd = [OPA_BINARY, "reset"]
            elif command == "commit":
                cmd = [OPA_BINARY, "commit"]
            elif command == "reload":
                cmd = [OPA_BINARY, "reload"]
            elif command == "restart":
                cmd = [OPA_BINARY, "restart"]
            else:
                raise omnipath_exceptions.FabricAgentUnknownCommandError
            return self.execute_command(cmd)
        except omnipath_exceptions.FabricAgentUnknownCommandError:
            LOG.error(command + " not supported in opafmvf CLI")


class FabricAgentClient(object):
    def __init__(self):
        self.cli = FabricAgentCLI()

    # Neutron FabricAgentClient sending requests to Fabric Agent:
    def full_sync(self, guids_info):
        """Will send list of GUIDs to be created/deleted to OpenStack Fabric Agent. The creates/deletes are implicit.

        :param guid_info: {vf_name1: [guid1, guid2], vf_name2: [guid3, guid4]}
        :return: bind status
        """

        # lock
        # Add global lock so that this command is sent by only one neutron server
        for vf_name, guids in guids_info:
            config_status = self.cli.osfa_config_commands("add", vf_name, guids)
            if config_status == 2:
                return "ERROR" # Port Status ERROR

        commit_status = self.cli.osfa_management_commands("commit")
        if commit_status != 0:
            return "ERROR" # Port Status ERROR

        reload_status = self.cli.osfa_management_commands("reload")
        if reload_status != 0:
            return "ERROR" # Port Status ERROR

        return "DOWN" # Port Status DOWN
        # unlock

    # Neutron retrieving status from Fabric Agent:

    def get_port_status(self, vf_name, guid):
        """

        :param vf_name: Name of the VF
        :param guid: ID of the physical server
        :return: bind status
        """

        query_status = self.cli.osfa_query_commands("ismember", vf_name, [guid])
        if query_status == 0:
            return "UP"
        else:
            return "DOWN"
