##############################################################################
#
# Copyright (C) Zenoss, Inc. 2020, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from __future__ import absolute_import, print_function

import argparse

from .docker import Docker
from .dockerregistry import DockerRegistry
from .elasticsearchserviced import ElasticsearchServiced
from .serviced import Serviced
from .zookeeper import Zookeeper


docker = Docker()
dr = DockerRegistry()
es = ElasticsearchServiced()
serviced = Serviced()
zk = Zookeeper()


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


def process_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    tags = subparsers.add_parser("tags", help="Manage image tags")
    tags_subparsers = tags.add_subparsers()

    tags_count = tags_subparsers.add_parser(
        "count", help="Displays image tag count",
    )
    tags_count.set_defaults(func=getCounts)

    tags_clean = tags_subparsers.add_parser(
        "clean", help="Remove unused image tags",
    )
    tags_clean.set_defaults(func=cleanUp)

    args = parser.parse_args()
    args.func()


def main():
    process_args()
