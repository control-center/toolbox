##############################################################################
#
# Copyright (C) Zenoss, Inc. 2020, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from __future__ import absolute_import, print_function

import base64

from .serviced import Serviced


class Zookeeper(Serviced):
    """Uses Serviced.command to connect to isvcs-zookeeper and list tags."""

    def __init__(self):
        self.connected = False

    def getDockerTagCount(self):
        """Gets numberChildren from /docker/registry/tags node."""
        cmd = [
            "docker",
            "exec",
            "-it",
            "serviced-isvcs_zookeeper",
            "/bin/bash",
            "-c",
            "$ZK_PATH/bin/zkCli.sh stat /docker/registry/tags",
        ]

        zk_output = self.command(cmd)[0]

        total = 0
        for line in zk_output.split("\n"):
            if "numChildren =" in line:
                total = int(line.split()[2])
        return total

    def getDockerTags(self):
        """ Gets the tags from /docker/registry/tags node. """
        zk_tags = []
        cmd = [
            "docker",
            "exec",
            "-it",
            "serviced-isvcs_zookeeper",
            "/bin/bash",
            "-c",
            "$ZK_PATH/bin/zkCli.sh ls /docker/registry/tags",
        ]

        zk_output = self.command(cmd)[0]

        for line in zk_output.split("\n"):
            if "Session establishment complete" in line:
                self.connected = True
            elif line.startswith("["):
                zk_data_string = line

        if self.connected:
            encoded_zk_docker_tags = zk_data_string.translate(
                None, "[]\r,"
            ).split()

        if encoded_zk_docker_tags:
            for line in encoded_zk_docker_tags:
                zk_tags.append(base64.decodestring(line))

            if zk_tags:
                zk_tags.sort()

        return zk_tags
