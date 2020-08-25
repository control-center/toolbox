##############################################################################
#
# Copyright (C) Zenoss, Inc. 2020, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################



import json
import os
import shutil

from .serviced import Serviced


class DockerRegistry(Serviced):
    """ Connects to docker-registry on localhost:5000 and returns
       all docker repos and tags. """

    def __init__(self):
        self.url = "http://localhost:5000/v2"

    def backup(self):
        """ Backup /opt/serviced/var/isvcs/docker-registry
            Creates /opt/serviced/var/isvcs/docker-registry_timestamp.bak
        """
        dr_path = "%s/docker-registry" % self.isvcs_dir
        backup_dr_path = "%s/docker-registry_%s.bak" % (
            self.isvcs_dir,
            self.timestamp,
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
        results = self.urlRequest("%s/%s" % (self.url, "_catalog"))
        if results:
            repos = json.loads(results)
        else:
            repos = None
        return repos

    def getTagCount(self):
        """ Returns the count of Docker Registry tags."""
        return len(self.getTags())

    def getTags(self):
        """ Connects to DockerRegistry and gets list of tags
            based on provided repos.

            Keyword arguments:
            repos -- the repositories to get tags from (default None)
        """
        repos = self.getRepos()
        image_tags = []
        for repo in repos["repositories"]:
            results = self.urlRequest("%s/%s/tags/list" % (self.url, repo))
            if results:
                tags = json.loads(results)
                for tag in tags["tags"]:
                    image_tag = "%s:%s" % (tags["name"], tag)
                    if image_tag:
                        image_tags.append(image_tag)
                image_tags.sort()
        return image_tags
