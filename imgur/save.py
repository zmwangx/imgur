#!/usr/bin/env python3

"""Save online images to Imgur account."""

# pylint: disable=wildcard-import,unused-wildcard-import

import multiprocessing
import os
import tempfile
import urllib.request

from zmwangx.colorout import *

import imgur.cli

class Saver(object):
    """Image saver.

    This is a function class used for multiprocessing.Pool.map. Upon
    calling, the function downloads an image from a remote URL and save
    it to Imgur.

    """
    # pylint: disable=too-few-public-methods,invalid-name
    def __init__(self, client, directory):
        """Init."""
        self.client = client
        self.directory = directory

    def __call__(self, source_url):
        """Download image from url and upload to Imgur."""
        fd, savepath = tempfile.mkstemp(dir=self.directory)
        os.close(fd)
        try:
            urllib.request.urlretrieve(source_url, filename=savepath)
        except OSError:
            cerror("failed to download '%s'" % source_url)
            os.remove(savepath)
            return None
        try:
            return self.client.upload_image(savepath).link
        # not sure what's waiting
        # pylint: disable=broad-except
        except Exception:
            cerror("failed to upload '%s' saved from '%s'" %
                   (savepath, source_url))
            return None

def save_images(client, source_urls, jobs=None):
    """Retrieve remote images and then upload to Imgur.

    Parameters
    ----------
    source_urls : list
        List of source image URLs.
    jobs : int
        Number of workers. If None, multiprocessing.cpu_count() * 2 is
        used. If 0, the number of paths is used (not recommended when
        paths is a large list). Default is None.

    Returns
    -------
    uploaded_urls : list
        List of uploaded image URLs; a None element means a failure.

    """
    pool_size = multiprocessing.cpu_count() * 2 if jobs is None else jobs
    if pool_size == 0:
        pool_size = len(source_urls)
    pool = multiprocessing.Pool(processes=pool_size)
    with tempfile.TemporaryDirectory(prefix="imgur-save-") as directory:
        return pool.map(Saver(client, directory), source_urls)

def main():
    """CLI interface."""
    imgur.cli.cli("save")

if __name__ == "__main__":
    main()
