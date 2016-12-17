#!/usr/bin/env python3

"""Shared CLI."""

# pylint: disable=wildcard-import,unused-wildcard-import

import argparse
import os
import re
import subprocess

from zmwangx.colorout import *

import imgur.authenticate
import imgur.save
import imgur.upload

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

def cli(action):
    """Shared CLI interface for imgur.upload and imgur.save.

    Parameters
    ----------
    action : {"upload", "save"}

    """

    if action == "upload":
        description = """Upload images to your Imgur account, and get
        back links. You should put your client_id and client_secret in a
        configuration file $XDG_CONFIG_HOME/imgur/imgur.conf or
        $HOME/.config/imgur/imgur.conf, under the section "oauth". You
        may authorize this application by putting a known refresh_token
        in the same config file, running imgur-authorize, or directly
        running this script (in which case you will be prompted for
        authorization in the very first run, and your config file will
        be updated so that you don't need to re-authorize in the
        future).

        This script logs to $XDG_DATA_HOME/imgur/upload.log or
        $HOME/.local/share/imgur/upload.log.
        """
    else:
        description = """Save remote images to your Imgur account. This
        routine basically retrieves the remote images to local
        tempfiles, and then upload them in the same way as
        imgur-upload. See "imgur-upload -h" for more details."""

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-a', '--anonymous', action='store_true',
                        help='upload anonymously')
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
    if action == "upload":
        parser.add_argument('paths', nargs='+', metavar='PATH',
                            help='path to the image')
    else:
        parser.add_argument('source_urls', nargs='+', metavar='URL',
                            help='source urls of images')
    args = parser.parse_args()

    client = imgur.authenticate.gen_client(anonymous=args.anonymous)
    if client is None:
        cfatal_error("failed to create client")
        return 1
    log_file = get_log_file()
    with open(log_file, 'a', encoding='utf-8') as log_obj:
        date = subprocess.check_output('date').decode('utf-8').strip()
        log_obj.write('# %s\n' % date)

        if action == "upload":
            cprogress("uploading %d images..." % len(args.paths))
            uploaded_uris = imgur.upload.upload_images(
                client, args.paths, jobs=args.jobs)
        else:
            cprogress("saving %d images..." % len(args.source_urls))
            uploaded_uris = imgur.save.save_images(
                client, args.source_urls, jobs=args.jobs)

        success_count = 0
        failure_count = 0
        for uri in uploaded_uris:
            if uri is not None:
                if not args.no_https:
                    uri = re.sub(r'^http://', 'https://', uri)
                success_count += 1
                print(uri)
                log_obj.write('%s\n' % uri)
            else:
                failure_count += 1

    cprogress("successfully %s %d images, failed on %d images" %
              ("uploaded" if action == "upload" else "saved",
               success_count, failure_count))

    return 1 if failure_count > 0 else 0
