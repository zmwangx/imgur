#!/usr/bin/env python3

"""Authorize with Imgur's OAuth API and generate refresh token."""

# pylint: disable=wildcard-import,unused-wildcard-import

import argparse
import configparser
import sys
import webbrowser

import pyimgur

import imgur.authenticate

from zmwangx.colorout import *

def authorize(client_id, client_secret):
    """Authorize with Imgur's OAuth API and get refresh token.

    The refresh token will be written to the config file.

    Parameters
    ----------
    client_id : str
    client_secret : str

    Returns
    -------
    client : pyimgur.Imgur
        An authorized and authenticated client with access token and
        refresh token, or None if any step fails.

    """

    if client_id is None or client_secret is None:
        cwarning("client_id or client_secret unavailable")
        cwarning("please make sure your config file exists "
                 "and is in valid format")
        return None

    client = pyimgur.Imgur(client_id, client_secret)
    auth_url = client.authorization_url('pin')
    webbrowser.open(auth_url)
    try:
        pin = input("Please enter the PIN shown on the Imgur website: ")
    except EOFError:
        sys.stderr.write("\n")
        cerror("no input")
        return None
    client.exchange_pin(pin)
    refresh_token = client.refresh_token
    cprogress("Refresh token generated.")

    # add credentials to config file
    conf_file = imgur.authenticate.get_conf_file()
    config = configparser.ConfigParser()
    config.read([conf_file])
    config['oauth'] = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
    }
    with open(conf_file, 'w') as conf_obj:
        config.write(conf_obj)
        cprogress("Written: %s" % conf_file)
    return client

def main():
    """CLI interface."""
    description = """Authorize with Imgur's OAuth API and generate
    refresh token. Before you run this script, you need to put your
    client_id and client_secret in a config file
    $XDG_CONFIG_HOME/imgur/imgur.conf (or
    $HOME/.config/imgur/imgur.conf), under the "oauth"
    section. Additional credentials will be written to this file
    afterwards."""
    parser = argparse.ArgumentParser(description=description)
    # no arguments
    parser.parse_args()

    client_id, client_secret, _ = imgur.authenticate.get_credentials()
    if authorize(client_id, client_secret) is None:
        cerror("authorization failed")
        return 1
