#!/usr/bin/env python3

import configparser
import filecmp
import os
import sys
import tempfile
import unittest

import PIL.Image
import urllib.request
from zmwangx.infrastructure import capture_stdout, capture_stderr, change_home

import imgur.upload

class TestUpload(unittest.TestCase):

    def setUp(self):
        image = PIL.Image.new("RGB", (100, 100))
        fd, self.imagepath = tempfile.mkstemp(suffix=".png",
                                              prefix="imgur-test-")
        os.close(fd)
        image.save(self.imagepath)
        image.close()

    def tearDown(self):
        os.remove(self.imagepath)

    @staticmethod
    def write_config():
        config = configparser.ConfigParser()
        # I registered a dummy account for automated testing only
        # please do not abuse this account
        config["oauth"] = {
            "client_id": "4ec5d769d0104a9",
            "client_secret": "07e4898b8a21a049fb1590c271085ef93b58330b",
            "refresh_token": "88608c131302b8b712e6382ef4ca56dc7bc27f95",
        }
        configfilepath = os.path.expanduser("~/.config/imgur/imgur.conf")
        os.makedirs(os.path.dirname(configfilepath))
        with open(configfilepath, "w") as configfileobj:
            config.write(configfileobj)

    def test_main(self):
        with capture_stdout():
            with capture_stderr():
                with change_home():
                    sys.argv[1:] = ["--no-https", self.imagepath]
                    imgur.upload.main()
                    sys.stderr.write("getvalue: %s\n" % str(type(sys.stdout)))
                    output = sys.stdout.getvalue()
                    imageurls = output.strip().split("\n")
                    self.assertEqual(len(imageurls), 1)
                    imageurl = imageurls[0]
                    sys.stderr.write(str(type(sys.stdout)))
                    sys.stderr.write(str(type(sys.stderr)))
                    # download uploaded image and make sure it's
                    # identical to the original
                    downloaded_imagepath, _ = urllib.request.urlretrieve(imageurl)
                    try:
                        self.assertTrue(filecmp.cmp(self.imagepath,
                                                    downloaded_imagepath,
                                                    shallow=False))
                    finally:
                        os.remove(downloaded_imagepath)

if __name__ == "__main__":
    unittest.main()
