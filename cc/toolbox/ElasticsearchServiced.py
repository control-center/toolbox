#!/usr/bin/env python
##############################################################################
#
# Copyright (C) Zenoss, Inc. 2020, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import json
from Serviced import Serviced
import shutil

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
                    print("Unable to backup elasticsearch-serviced: %s" % e)
                    return False

    def cleanUp(self):
        ir_url = 'http://localhost:9200/controlplane/imageregistry/'
        params = {'get_method': 'DELETE'}
        images = self.getImages()
        if images:
            try:
                serviced = Serviced()
                for img in images:
                    if 'latest' not in img.tag:
                        url = "%s%s" % (ir_url, img.doc_id)
                        results = serviced.urlRequest(url, params)
                        print("Successfully removed: %s" % json.loads(results))
            except Exception:
                raise

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
