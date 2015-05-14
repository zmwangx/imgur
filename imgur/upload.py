#!/usr/bin/env python3

"""Upload images to an Imgur account."""

import argparse
from contextlib import contextmanager
import multiprocessing
import os
import re
import subprocess
import sys

import imgur.authenticate

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

def get_log_file():
    """Get the path to upload's log file.

    Also make sure the directory containing the log file exists.

    """

    if 'XDG_DATA_HOME' in os.environ:
        log_file = os.path.join(os.environ['XDG_DATA_HOME'],
                                'imgur/upload.log')
    else:
        log_file = os.path.expanduser('~/.local/share/imgur/upload.log')
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file), mode=0o700)
    return log_file

def main():
    """CLI interface."""
    description = """Upload images to your Imgur account, and get back
    links. You should put your client_id and client_secret in a
    configuration file $XDG_CONFIG_HOME/imgur/imgur.conf or
    $HOME/.config/imgur/imgur.conf, under the section "oauth". You may
    authorize this application by putting a known refresh_token in the
    same config file, running imgur-authorize, or directly running this
    script (in which case you will be prompted for authorization in the
    very first run, and your config file will be updated so that you
    don't need to re-authorize in the future).

    This script logs to $XDG_DATA_HOME/imgur/upload.log or
    $HOME/.local/share/imgur/upload.log.
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-j', '--jobs', type=int,
                        help="""Maximum number of concurrent jobs. If 0,
                        do not limit the number of jobs (not recommended
                        when uploading a large list of imagesp). By
                        default, twice the number of (virtual) CPU cores
                        is used.""")
    parser.add_argument('--no-https', action='store_true',
                        help="""by default returned URIs use the HTTPS
                        protocol; this option turns HTTPS off and use
                        HTTP instead""")
    parser.add_argument('paths', nargs='+', metavar='PATH',
                        help='path to the image')
    args = parser.parse_args()

    client = imgur.authenticate.gen_client()
    if client is None:
        cfatal_error("failed to create client")
        exit(1)
    log_file = get_log_file()
    with open(log_file, 'a', encoding='utf-8') as log_obj:
        date = subprocess.check_output('date').decode('utf-8').strip()
        log_obj.write('# %s\n' % date)
        cprogress("uploading %d images..." % len(args.paths))
        uris = upload_images(client, args.paths, jobs=args.jobs)
        success_count = 0
        failure_count = 0
        for uri in uris:
            if uri is not None:
                if not args.no_https:
                    uri = re.sub(r'^http://', 'https://', uri)
                success_count += 1
                print(uri)
                log_obj.write('%s\n' % uri)
            else:
                failure_count += 1
    cprogress("successfully uploaded %d images, failed on %d images" %
              (success_count, failure_count))

    return 1 if failure_count > 0 else 0
