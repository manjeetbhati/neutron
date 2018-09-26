from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

opt_group = cfg.OptGroup(name="omnipath_config",
                         title="Omnipath configuration")

omnipath_opts = [
    cfg.StrOpt(
        "ip_address",
        default="localhost",
        help="Host IP Address of the OPA FM Agent"
    ),
    cfg.StrOpt(
        "username",
        help="Username of the OPA FM Agent"
    ),
    cfg.StrOpt(
        "ssh_key",
        help="Private key path to access OPA FM Agent"
    ),
    cfg.StrOpt(
        "poll_interval",
        help="Interval in seconds which a full sync is done with OPA FM Agent"
    ),
    cfg.StrOpt(
        "pkey_ranges",
        help="Interval in seconds which a full sync is done with OPA FM Agent"
    ),
]

#CONF = cfg.CONF
#CONF.register_group(opt_group)
cfg.CONF.register_opts(omnipath_opts, "ml2_omnipath")
#CONF.default_config_files=["/etc/omnipath.conf"]
