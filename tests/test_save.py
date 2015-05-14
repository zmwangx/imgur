#!/usr/bin/env python3

import filecmp
import os
import sys
import urllib.request

from zmwangx.infrastructure import capture_stdout, capture_stderr, change_home

import imgur.save

import tests.test_upload

# inherit from tests.test_upload.TestUpload to reuse the same setup
class TestSave(tests.test_upload.TestUpload):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # static method write_config already defined

    def test_main(self):
        with capture_stdout():
            with capture_stderr():
                with change_home():
                    self.write_config()

                    source_url = "http://i.imgur.com/VXz0fRx.png"
                    sys.argv[1:] = ["--no-https", source_url]
                    try:
                        if imgur.save.main() == 1:
                            raise SystemExit(1)
                    except SystemExit:
                        raise SystemExit(sys.stderr.getvalue())

                    output = sys.stdout.getvalue()
                    uploaded_urls = output.strip().split("\n")
                    self.assertEqual(len(uploaded_urls), 1)
                    uploaded_url = uploaded_urls[0]
                    # download uploaded image and make sure it's
                    # identical to the original
                    image1_path, _ = urllib.request.urlretrieve(source_url)
                    image2_path, _ = urllib.request.urlretrieve(uploaded_url)
                    try:
                        self.assertTrue(filecmp.cmp(image1_path,
                                                    image2_path,
                                                    shallow=False))
                    finally:
                        os.remove(image1_path)
                        os.remove(image2_path)
