#!/usr/bin/env python
##############################################################################
#
# Copyright (C) Zenoss, Inc. 2020, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import base64
from datetime import datetime
import json
import os
import re
import subprocess
import shutil
from time import time
import urllib
import urllib2


class DockerImage():
    def __init__(self, d=None):
        self.containers = d['Containers']
        self.created_at = d['CreatedAt']
        self.digest = d['Digest']
        self.id = d['ID']
        self.repo = d['Repository']
        self.shared_size = d['SharedSize']
        self.size = d['Size']
        self.tag = d['Tag']
        self.unique_size = d['UniqueSize']
        self.virtual_size = d['VirtualSize']

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self.id)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.id)


class ElasticsearchDockerImage():
    def __init__(self, d=None):
        self.doc_id = d['_id']
        self.library = d['_source']['Library']
        self.repo = d['_source']['Repo']
        self.tag = d['_source']['Tag']
        self.uuid = d['_source']['UUID']

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self.doc_id)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.doc_id)


class Serviced():
    """ Defines the basic serviced class and attributes. """

    isvcs_dir = '/opt/serviced/var/isvcs'
    backup_dir = '/opt/serviced/var/backups'
    timestamp = datetime.fromtimestamp(time()).strftime(
        '%Y-%m-%d_%H:%M'
        )

    def command(self, cmd=None):
        """ Returns command results. """
        try:
            self.cmd = cmd
            request = subprocess.Popen(
                self.cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE)
            results = request.communicate()
        except Exception:
            raise
        return results

    def urlRequest(self, url=None, params=None):
        """ Connect to a URL via urllib2 and return results from query.

            Keyword arguments:
            url -- URL to send request(s) (default None)
            params -- the request parameters (default None)
        """
        url = url
        self.params = params
        try:
            
            if url and self.params:
                if self.params.has_key('get_method'):
                    if self.params.get('get_method') == 'DELETE':
                        opener = urllib2.build_opener(urllib2.HTTPHandler)
                        request = urllib2.Request(url)
                        request.get_method = lambda: 'DELETE'
                        response = opener.open(request)
                else:
                    opener = urllib2.build_opener(urllib2.HTTPHandler)
                    request = urllib2.Request("%s%s" % (
                        url,
                        urllib.urlencode(params)
                        ))
                    response = opener.open(request)
            elif url and not self.params:
                opener = urllib2.build_opener(urllib2.HTTPHandler)
                request = urllib2.Request(url)
                response = opener.open(request)
            else:
                print("Serviced.urlRequest: No url or params specified.")
        except Exception:
            raise

        if response:
            status = response.code
            if status == 200:
                results = response.readlines()[0]
                return results
            elif status != 200:
                print("Serviced.urlRequest Error: %s" % status)
        else:
            print("Serviced.urlRequest Error: Problem with request.")
            return None

    def getSnapshots(self):
        """ Returns list of snapshots.
            Returns None if there aren't any snapshots.
        """
        cmd = [
            "serviced",
            "snapshot",
            "list"
        ]

        results = self.command(cmd)

        if results:
            if results[0]:
                snapshots = results[0].split()
            else:
                if 'no snapshots found' in results[1]:
                    snapshots = []
                else:
                    print(results[1])
                    snapshots = None

        return snapshots


class Docker(Serviced):
    """ Uses subprocess module to run commands
        and gather output from commands.
    """

    def getDiskUsage(self, images=None):
        """ Returns disk usage in GB required for saving docker images.

            Keyword arguments:
            images -- list of image objects (default None)
                example: images = [<DockerImage 0x7fe68fa4e5a8>]
        """
        if images:
            size = 0
            for img in images:
                if 'GB' in img.size:
                    size = size + float(img.size.split('GB')[0]) * 1024
                elif 'MB' in img.size:
                    size = size + float(img.size.split('MB')[0])
        else:
            size = 0

        return "%d GB" % (size / 1024)

    def getImageCount(self):
        return len(self.getImages())

    def getImages(self):
        """ Returns a list of docker image objects.
        """
        cmd = [
            "docker",
            "images",
            "--format",
            "'{{json .}}'"
            ]
        images = []
        results = self.command(cmd)
        for result in results[0].split('\n'):
            if result:
                try:
                    img = json.loads(result.strip('\''))
                    obj = DockerImage(img)
                    images.append(obj)
                except Exception as e:
                    print("%s" % e)

        return images

    def getImageString(self, image):
        imageString = "%s:%s" % (
            image.repo,
            image.tag
        )
        return imageString

    def prepareBackup(self):
        """ Returns a tuple with two items.
            The first item is the disk usage of docker images in GB.
            The second item is a list of docker images to save.
            (default base and latest images)
        """
        images = self.getImages()
        if images:
            parsed_images = []
            unparsed_images = []
            for img in images:
                if 'latest' in img.Tag:
                    unparsed_images.append(img)
                    parsed_images.append(self.getImageString(img))
                elif 'zenoss' in img.Repository:
                    unparsed_images.append(img)
                    parsed_images.append(self.getImageString(img))

        if unparsed_images:
            sizeOfImages = self.getDiskUsage(unparsed_images)
        else:
            sizeOfImages = None

        if parsed_images:
            parsed_images.sort()
        else:
            parsed_images = None
        return (sizeOfImages, parsed_images)

    def saveImages(self, images=None, path='/opt/serviced/var/backups/'):
        """ Runs docker save <image> -o <path>

            Keyword arguments:
            images -- the list of images to save (default None)
            path -- full path to save images (default /opt/serviced/var/backups)
        """
        if not os.path.exists(path) and not os.path.isdir(path):
            print("Docker.saveImages: unable to save images.")
            print("Docker.saveImages: Directory: %s doesn't exist." % path)
            return None

        if images:
            for img in images:
                img = str(img)
                save_image = img.replace('/', '-').replace(':', '_')
                save_image_path = "%s%s.img" % (path, save_image)
                try:
                    cmd = [
                        'docker',
                        'save',
                        img,
                        '-o',
                        save_image_path
                    ]
                    img_saved = self.command(cmd)[0]
                except Exception as e:
                    print(e)
            if img_saved:
                return img_saved
        else:
            print("Docker.saveImages: No images provided to save.")
            return None


class DockerRegistry(Serviced):
    """ Connects to docker-registry on localhost:5000 and returns
       all docker repos and tags. """
    def __init__(self):
        self.url = 'http://localhost:5000/v2'

    def backup(self):
        """ Backup /opt/serviced/var/isvcs/docker-registry
            Creates /opt/serviced/var/isvcs/docker-registry_timestamp.bak
        """
        dr_path = "%s/docker-registry" % self.isvcs_dir
        backup_dr_path = "%s/docker-registry_%s.bak" % (
            self.isvcs_dir,
            self.timestamp
            )

        # Create docker-registry backup directory and copy data.
        if os.path.exists(dr_path) and os.path.isdir(dr_path):
            if not os.path.exists(backup_dr_path):
                try:
                    shutil.copytree(dr_path, backup_dr_path)
                    return True
                except Exception as e:
                    print("Unable to backup docker-registry: %s" % e)
                    return False

    def getRepos(self):
        """ Connects to DockerRegistry, gets list of repositories
           and lists tags for each repository. """
        results = self.urlRequest("%s/%s" % (
            self.url,
            '_catalog'
        ))
        if results:
            repos = json.loads(results)
        else:
            repos = None
        return repos

    def getTagCount(self):
        """ Returns the count of Docker Registry tags."""
        return len(self.getTags(self.getRepos()))

    def getTags(self):
        """ Connects to DockerRegistry and gets list of tags
            based on provided repos.

            Keyword arguments:
            repos -- the repositories to get tags from (default None)
        """
        repos = self.getRepos()
        image_tags = []
        for repo in repos['repositories']:
            results = self.urlRequest("%s/%s/tags/list" % (
                self.url,
                repo
            ))
            if results:
                tags = json.loads(results)
                for tag in tags['tags']:
                    image_tag = "%s:%s" % (
                        tags['name'],
                        tag)
                    if image_tag:
                        image_tags.append(image_tag)
                image_tags.sort()
        return image_tags


class ElasticsearchServiced(Serviced):
    """Connects to elasticsearch-serviced on localhost and returns
       all elasticsearch documents matching specified params. """

    def __init__(self, params=None):
        """ Init method for ElasticsearchServiced class.

            Keyword arguments:
            params -- dictionary of urlRequest parameters (default None)
        """
        self.url = 'http://localhost:9200/controlplane/imageregistry/_search?'
        self.params = params

    def backup(self):
        """ Backup /opt/serviced/var/isvcs/elasticsearch-serviced
            Creates /opt/serviced/var/isvcs/elasticsearch-serviced_timestamp.bak
        """
        es_path = "%s/elasticsearch-serviced" % self.isvcs_dir
        backup_es_path = "%s/elasticsearch-serviced_%s.bak" % (
            self.isvcs_dir,
            self.timestamp
        )

        # Create elasticsearch-serviced backup directory and copy data
        if os.path.exists(es_path) and os.path.isdir(es_path):
            if not os.path.exists(backup_es_path):
                try:
                    shutil.copytree(es_path, backup_es_path)
                    return True
                except Exception as e:
                    print("Unable to bacup elasticsearch-serviced: %s" % e)
                    return False

    def cleanUp(self):
        ir_url = 'http://localhost:9200/controlplane/imageregistry/'
        params = {'get_method': 'DELETE'}
        images = self.getImages()
        if images:
            serviced = Serviced()
            for img in images:
                if 'latest' not in img.tag:
                    url = "%s%s" % (ir_url, img.doc_id)
                    results = serviced.urlRequest(url, params)
                    print("Successfully removed: %s" % json.loads(results))

    def getImageTagCount(self):
        self.params = {"size": 1}
        try:
            results = self.urlRequest(self.url, self.params)
            elastic_documents = json.loads(results)
            total = elastic_documents['hits']['total']
            return total
        except Exception as e:
            print("Exception getting total count: %s" % e)
            return None

    def getTagDocs(self):
        """Returns a generator of all elasticsearch-serviced
           document objects. """
        # Run a query with a size of 1 and gather the total count

        total = self.getImageTagCount()
        try:
            if total:
                if total < 10000:
                    self.params = {"size": total}
                    results = self.urlRequest(self.url, self.params)
                    yield results
                else:
                    start = 0
                    size = 100
                    gathered = 0
                    while gathered < total:
                        self.params = {"from": start, "size": size}
                        results = self.urlRequest(self.url, self.params)
                        yield results
                        gathered = start + size
                        start = start + size
        except Exception as e:
            print("Elastic.getAllTagDocs Exception: %s" % e)

    def getImages(self):
        """ Returns a list of all elasticsearch-serviced images. """
        elasticImages = []
        for result in self.getTagDocs():
            data = json.loads(result)
            if data:
                try:
                    for doc in data['hits']['hits']:
                        if doc:
                            doc = ElasticsearchDockerImage(doc)
                            elasticImages.append(doc)
                except Exception as e:
                    print("Exception encountered: %s" % e)
        return elasticImages

    def parseElasticImages(self, docs=None):
        parsed_docs = []
        if docs:
            try:
                for doc in docs:
                    parsed_docs.append("%s/%s:%s" % (
                        doc.library,
                        doc.repo,
                        doc.tag))
            except Exception as e:
                print("Exception parsing docs: %s" % e)
            parsed_docs.sort()
        return parsed_docs


class Zookeeper(Serviced):
    """ Uses Serviced.command to connect to isvcs-zookeeper and list tags. """

    def __init__(self):
        self.connected = False

    def getDockerTagCount(self):
        """ Gets numberChildren from /docker/registry/tags node. """
        cmd = [
            "docker",
            "exec",
            "-it",
            "serviced-isvcs_zookeeper",
            "/bin/bash",
            "-c",
            "$ZK_PATH/bin/zkCli.sh stat /docker/registry/tags"]

        zk_output = self.command(cmd)[0]

        for line in zk_output.split('\n'):
            if 'numChildren =' in line:
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
            "$ZK_PATH/bin/zkCli.sh ls /docker/registry/tags"]

        zk_output = self.command(cmd)[0]

        for line in zk_output.split('\n'):
            if 'Session establishment complete' in line:
                self.connected = True
            elif line.startswith('['):
                zk_data_string = line

        if self.connected:
            encoded_zk_docker_tags = zk_data_string.translate(
                None,
                "[]\r,").split()

        if encoded_zk_docker_tags:
            for line in encoded_zk_docker_tags:
                zk_tags.append(base64.decodestring(line))

            if zk_tags:
                zk_tags.sort()

        return zk_tags
