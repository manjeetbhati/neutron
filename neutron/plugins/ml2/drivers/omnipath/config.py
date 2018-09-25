from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

opt_group = cfg.OptGroup(name="omnipath_config",
                         title="Omnipath configuration")

fields = [
    cfg.StrOpt(
        "IP_ADDRESS",
        default="localhost",
        help="Host IP Address of the OPA FM Agent"
    ),
    cfg.StrOpt(
        "USERNAME",
        help="Username of the OPA FM Agent"
    ),
    cfg.StrOpt(
        "KEY",
        help="Private key path to access OPA FM Agent"
    ),
    cfg.StrOpt(
        "POLL_INTERVAL",
        help="Interval in seconds which a full sync is done with OPA FM Agent"
    ),
    cfg.StrOpt(
        "PKEY_RANGE",
        help="Interval in seconds which a full sync is done with OPA FM Agent"
    ),
]

CONF = cfg.CONF
CONF.register_group(opt_group)
CONF.register_opts(fields, opt_group)
CONF.default_config_files=["/etc/omnipath.conf"]
