##############################################################################
#
# Copyright (C) Zenoss, Inc. 2020, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from __future__ import absolute_import, print_function

import subprocess
import urllib
import urllib2

from datetime import datetime
from time import time


class Serviced(object):
    """Defines the basic serviced class and attributes."""

    isvcs_dir = "/opt/serviced/var/isvcs"
    backup_dir = "/opt/serviced/var/backups"
    timestamp = datetime.fromtimestamp(time()).strftime("%Y-%m-%d_%H:%M")

    def command(self, cmd=None):
        """ Returns command results. """
        try:
            self.cmd = cmd
            request = subprocess.Popen(
                self.cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )
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
                if "get_method" in self.params:
                    if self.params.get("get_method") == "DELETE":
                        opener = urllib2.build_opener(urllib2.HTTPHandler)
                        request = urllib2.Request(url)
                        request.get_method = lambda: "DELETE"
                        response = opener.open(request)
                else:
                    opener = urllib2.build_opener(urllib2.HTTPHandler)
                    request = urllib2.Request(
                        "%s%s" % (url, urllib.urlencode(params))
                    )
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
        cmd = ["serviced", "snapshot", "list"]

        results = self.command(cmd)

        if results:
            if results[0]:
                snapshots = results[0].split()
            else:
                if "no snapshots found" in results[1]:
                    snapshots = []
                else:
                    print(results[1])
                    snapshots = None

        return snapshots
