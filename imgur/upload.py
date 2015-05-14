#!/usr/bin/env python3

"""Upload images to an Imgur account."""

# pylint: disable=wildcard-import,unused-wildcard-import

import multiprocessing
import os

import imgur.authenticate
import imgur.cli

from zmwangx.colorout import *

def upload_image(client, path):
    """Upload a single image.

    Parameters
    ----------
    client : pyimgur.Imgur
    path : str
        Path to the image.

    Returns
    -------
    uri : str
        URI of the successfully uploaded image (HTTP), or None if
        failed.

    """

    title = os.path.basename(path)
    try:
        return client.upload_image(path, title=title).link
    # pylint: disable=broad-except
    except Exception:  # no sure what kind of exception will occur
        cerror("failed to upload %s" % path)
        return None

# define a one-parameter version of upload_image for
# multiprocessing.Pool.map()
# equivalent to (lambda path: upload_image(client, path))
class Uploader(object):
    """lambda path: upload_image(client, path)"""
    # pylint: disable=too-few-public-methods
    def __init__(self, client):
        """Init with a client."""
        self.client = client

    def __call__(self, path):
        """Call upload_image."""
        return upload_image(self.client, path)

def upload_images(client, paths, jobs=None):
    """Upload images using a pool of workers.

    Parameters
    ----------
    client : pyimgur.Imgur
    paths : list
        List of image paths.
    jobs : int
        Number of workers. If None, multiprocessing.cpu_count() * 2 is
        used. If 0, the number of paths is used (not recommended when
        paths is a large list). Default is None.

    Returns
    -------
    uris :
        A list of URIs of uploaded images (HTTP); a None element means a
        failed upload.

    """

    pool_size = multiprocessing.cpu_count() * 2 if jobs is None else jobs
    if pool_size == 0:
        pool_size = len(paths)
    pool = multiprocessing.Pool(processes=pool_size)
    return pool.map(Uploader(client), paths)

def main():
    """CLI interface."""
    imgur.cli.cli("upload")

if __name__ == "__main__":
    main()
