#!/usr/bin/env python
##############################################################################
#
# Copyright (C) Zenoss, Inc. 2020, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import argparse
from Docker import Docker
from DockerRegistry import DockerRegistry
from ElasticsearchServiced import ElasticsearchServiced
from Serviced import Serviced
from Zookeeper import Zookeeper


docker = Docker()
dr = DockerRegistry()
es = ElasticsearchServiced()
serviced = Serviced()
zk = Zookeeper()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--imagecount",
        help="Displays Image (tag) counts",
        action="store_true"
        )
    parser.add_argument(
        "-c",
        "--cleanup",
        help="Removes unused elasticsearch-serviced image tags.",
        action="store_true"
    )
    args = parser.parse_args()
    return args


def cleanUp():
    print("Removing unused elasticsearch-serviced image tags.")
    getCounts()
    es.cleanUp()
    print("elasticsearch-serviced clean up completed.")


def getCounts():
    """ Prints the total count of image tags for:
          Docker
          DockerRegistry
          ElasticsearchServiced
          Serviced
          Zookeeper
    """
    docker_images = docker.getImageCount()
    dr_images = dr.getTagCount()
    es_images = es.getImageTagCount()
    serviced_snapshots = serviced.getSnapshots()
    zk_images = zk.getDockerTagCount()

    print("Docker Images: %d" % docker_images)
    print("Docker Registry Images: %d" % dr_images)
    print("Elasticsearch Serviced Images: %d" % es_images)
    print("Serviced Snapshots: %d" % len(serviced_snapshots))
    print("Zookeeper Images: %d" % zk_images)


if __name__ == '__main__':
    opts = get_args()
    if opts.imagecount:
        getCounts()
    if opts.cleanup:
        cleanUp()
