import unittest
try:
    from unittest.mock import MagicMock
except Exception:
    from mock import MagicMock
from ..zookeeper import Zookeeper


class TestZookeeper(unittest.TestCase, Zookeeper):

    def setUp(self):
        self.zk = Zookeeper()
        self.zk_connected = MagicMock(return_value=True)
        self.zk.getDockerTagCount = MagicMock(return_value={"count": 20})
        self.zk.getDockerTags = MagicMock(return_value={
            "zk_tags": [
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-062825.636',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-100554.863',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-110125.481',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-120218.924',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-130152.284',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-140113.828',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-150154.294',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-160217.009',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-170049.260',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-180151.165',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-190217.615',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-200205.883',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-210121.526',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-220210.675',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190628-230147.711',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190629-000158.009',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190629-010055.199',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190629-020156.248',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190629-030128.395',
                b'cmn7pwgr105nkvlfospy45o1a/resmgr_6.3:20190629-040102.330'
                ]})

    def tearDown(self):
        self.zk.disconnect()

    def test_init(self):
        self.assertIsInstance(self.zk, Zookeeper)
        self.assertTrue(self.zk_connected)

    def test_getDockerTagCount(self):
        self.tag_count = self.zk.getDockerTagCount()
        self.assertIsInstance(self.tag_count['count'], int)

    def test_getDockerTags(self):
        self.tags = self.zk.getDockerTags()
        self.assertIsInstance(self.tags['zk_tags'], list)
        self.assertGreaterEqual(len(self.tags['zk_tags']), 0)
