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

from .serviced import Serviced


class DockerImage(object):
    def __init__(self, d=None):
        self.containers = d["Containers"]
        self.created_at = d["CreatedAt"]
        self.digest = d["Digest"]
        self.id = d["ID"]
        self.repo = d["Repository"]
        self.shared_size = d["SharedSize"]
        self.size = d["Size"]
        self.tag = d["Tag"]
        self.unique_size = d["UniqueSize"]
        self.virtual_size = d["VirtualSize"]

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self.id)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.id)


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
                if "GB" in img.size:
                    size = size + float(img.size.split("GB")[0]) * 1024
                elif "MB" in img.size:
                    size = size + float(img.size.split("MB")[0])
        else:
            size = 0

        return "%d GB" % (size / 1024)

    def getImageCount(self):
        return len(self.getImages())

    def getImages(self):
        """ Returns a list of docker image objects.
        """
        cmd = ["docker", "images", "--format", "'{{json .}}'"]
        images = []
        results = self.command(cmd)
        for result in results[0].split("\n"):
            if result:
                try:
                    img = json.loads(result.strip("'"))
                    obj = DockerImage(img)
                    images.append(obj)
                except Exception as e:
                    print("%s" % e)

        return images

    def getImageString(self, image):
        imageString = "%s:%s" % (image.repo, image.tag)
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
                if "latest" in img.Tag:
                    unparsed_images.append(img)
                    parsed_images.append(self.getImageString(img))
                elif "zenoss" in img.Repository:
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

    def saveImages(self, images=None, path="/opt/serviced/var/backups/"):
        """ Runs docker save <image> -o <path>

            Keyword arguments:
            images -- the list of images to save (default None)
            path -- full path to save images
                (default /opt/serviced/var/backups)
        """
        if not os.path.exists(path) and not os.path.isdir(path):
            print("Docker.saveImages: unable to save images.")
            print("Docker.saveImages: Directory: %s doesn't exist." % path)
            return None

        if images:
            for img in images:
                img = str(img)
                save_image = img.replace("/", "-").replace(":", "_")
                save_image_path = "%s%s.img" % (path, save_image)
                try:
                    cmd = ["docker", "save", img, "-o", save_image_path]
                    img_saved = self.command(cmd)[0]
                except Exception as e:
                    print(e)
            if img_saved:
                return img_saved
        else:
            print("Docker.saveImages: No images provided to save.")
            return None
