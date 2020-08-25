##############################################################################
#
# Copyright (C) Zenoss, Inc. 2020, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import base64
from kazoo.client import KazooClient
import logging

logging.basicConfig(
    filename="serviced-tool.log",
    level=logging.INFO,
    filemode='a',
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)
log = logging.getLogger('serviced-tool.Zookeeper')


class Zookeeper():
    """Uses Serviced.command to connect to isvcs-zookeeper and list tags."""

    def __init__(self, hosts='127.0.0.1:2181', timeout=10.0, client_id=None,
                handler=None, default_acl=None, auth_data=None,
                sasl_options=None, read_only=None, randomize_hosts=True,
                connection_retry=None, logger=None, keyfile=None,
                keyfile_password=None, certfile=None, ca=None, use_ssl=False,
                verify_certs=True, **kwargs):
        """ Establish connection to zk node(s) using provided options. """
        try:
            self.zk = KazooClient(hosts)
            self.zk.start()
            self.zk_connected = True
        except Exception as ex:
            self.zk_connected = False
            log.error("Exception establishing connection to zk.")
            log.error("Exception: %s" % ex)
            raise

    def getDockerTagCount(self):
        """Gets numberChildren from /docker/registry/tags node."""
        if self.zk_connected:
            try:
                results = self.zk.exists("/docker/registry/tags")
                log.info("Total tags: %d" % results.numChildren)
            except Exception as ex:
                log.error("Error getting docker tag count from zk.")
                log.error("Exception: %s" % ex)
                raise

        return{"count": results.numChildren}

    def getDockerTags(self):
        """ Gets the tags from /docker/registry/tags node. """
        if self.zk_connected:
            try:
                results = self.zk.get_children("/docker/registry/tags")
                log.info("Successfully retrieved tags")
            except Exception as ex:
                results = None
                log.error("Error getting docker tags from zk.")
                log.error("Exception: %s" % ex)
                raise

        if not results:
            zk_tags = []
        else:
            zk_tags = [
                base64.b64decode(node)
                for node in results
            ]
            zk_tags.sort()

        return{"zk_tags": zk_tags}

    def disconnect(self):
        self.zk.stop()
