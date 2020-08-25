import unittest
try:
    from unittest.mock import MagicMock
except Exception:
    from mock import MagicMock
from ..dockerimages import Docker


class TestDocker(unittest.TestCase, Docker):

    def setUp(self):
        self.docker = Docker()

    def test_getImages(self):
        images = self.docker.getImages()
        self.assertIsInstance(images, list)
        self.assertGreaterEqual(images, 0)


suite = unittest.TestLoader().loadTestsFromTestCase(TestDocker)
