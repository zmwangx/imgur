#!/usr/bin/env python3

"""Authenticate with Imgur's OAuth API."""

# pylint: disable=wildcard-import,unused-wildcard-import

import configparser
import os
import sys

import pyimgur

from zmwangx.colorout import *

import imgur.authorize

def get_conf_file():
    """Get the path to imgur's config file.

    Also make sure the directory containing the config file exists.

    """

    if 'XDG_CONFIG_HOME' in os.environ:
        conf_file = os.path.join(os.environ['XDG_CONFIG_HOME'],
                                 'imgur/imgur.conf')
    else:
        conf_file = os.path.expanduser('~/.config/imgur/imgur.conf')
    if not os.path.exists(os.path.dirname(conf_file)):
        os.makedirs(os.path.dirname(conf_file), mode=0o700)
    return conf_file

def get_credentials():
    """Get credentials from conf file.

    Returns
    -------
    (client_id, client_secret, refresh_token) : tuple
        Unavailable values are marked as None.

    """

    config = configparser.ConfigParser()
    config.read(get_conf_file())
    client_id = config.get('oauth', 'client_id', fallback=None)
    client_secret = config.get('oauth', 'client_secret', fallback=None)
    refresh_token = config.get('oauth', 'refresh_token', fallback=None)
    return (client_id, client_secret, refresh_token)

def gen_client():
    """Generate an authenticated OAuth client with a fresh access_token.

    client_id, client_secret, and refresh_token are read from either
    $XDG_CONFIG_HOME/imgur/imgur.conf or $HOME/.config/imgur/imgur.conf,
    under the "oauth" section. If client_id or client_secret is not
    present, return None; if only refresh_token is missing, call
    imgur.authorize.authorize(client_id, client_secret) to authorize and
    generate the token. The credentials are then used to initialize the
    client.

    Returns
    -------
    client : pyimgur.Imgur
        On success. None if any step failed.

    """

    client_id, client_secret, refresh_token = get_credentials()
    if client_id is None or client_secret is None:
        cwarning("client_id or client_secret unavailable")
        return None

    if refresh_token is None:
        sys.stderr.write("No refresh_token found in config file.\n"
                         "Generate one with imgur.authorize?\n")
        while True:
            yesno = input("[Yn] ")
            if not yesno or yesno.startswith(('Y', 'y')):
                yesno = True
                break
            elif yesno.startswith(('N', 'n')):
                yesno = False
                break
            else:
                sys.stderr.write("Please answer yes or no.\n")

        if yesno:
            return imgur.authorize.authorize(client_id, client_secret)
        else:
            return None

    client = pyimgur.Imgur(client_id, client_secret,
                           refresh_token=refresh_token)
    client.refresh_access_token()
    return client
