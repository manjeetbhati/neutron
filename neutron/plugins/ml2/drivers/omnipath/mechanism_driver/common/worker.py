import time

from neutron_lib import worker

from oslo_log import log as logging
from oslo_service import loopingcall


LOG = logging.getLogger(__name__)


class OmnipathWorker(worker.BaseWorker):
    def __init__(self, sync_func, sync_time=None):
        self._sync_func = sync_func
        self._sync_time = 60
        if sync_time:
            self._sync_time = sync_time
        self._loop = None
        super(OmnipathWorker, self).__init__()

    def start(self):
        super(OmnipathWorker, self).start()
        if self._loop is None:
            self._loop = loopingcall.FixedIntervalLoopingCall(self._sync_func)
        LOG.INFO("Starting omnipath worker")
        self._loop.start(interval=self._sync_time)

    def stop(self):
        if self._loop is not None:
            LOG.INFO("Stopping omnipath worker")
            self._loop.stop()

    def wait(self):
        if self._loop is not None:
            LOG.INFO("Waiting omnipath worker")
            self._loop.wait()
        self._loop = None

    def reset(self):
        LOG.INFO("Reseting omnipath worker")
        self.stop()
        self.wait()
        self.start()
