##############################################################################
#
# Copyright (C) Zenoss, Inc. 2020, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import docker


class Docker():
    """ Uses docker module to get list of docker images. """

    def __init__(self):
        self.client = docker.from_env()

    def getImageCount(self):
        return len(self.getImages())

    def getImages(self):
        """ Returns a list of docker image objects.
        """
        try:
            images = self.client.images.list()
        except Exception as ex:
            print("Docker Exception: %s" % ex)
            images = []

        return images
