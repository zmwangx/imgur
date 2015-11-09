imgur
=====

|Build Status|

This Python package is a CLI wrapper around `pyimgur
<https://github.com/Damgaard/PyImgur>`_ specialized in uploading
images (with multiprocessing support). It always does authenticated
uploads, i.e., uploads to your account, so that you have full control
over the uploaded images later.

Installation
------------

Clone the repository, then in the root of the repository, do ::

  pip install .

or ::

  ./setup.py install

Note that some older versions of ``setuptools`` might not work; in
that case, run ``pip install --upgrade pip`` first.

Usage
-----

This package installs two console scripts, ``imgur-authorize`` and
``imgur-upload``. The invocations are::

  imgur-authorize [-h]

and::

  imgur-upload [-h] [-j JOBS] [--no-https] PATH [PATH ...]

Run the scripts with the ``-h`` flag for detailed explanations of the
options. The use of ``imgur-authorize`` is also explained in the
"Authorization" section.

Credentials and configuration file
----------------------------------

You should put your credentials (client id and client secret) in a
configuration file located at ``$XDG_CONFIG_HOME/imgur/imgur.conf``, or
if the environment variable ``XDG_CONFIG_HOME`` is not defined,
``~/.config/imgur/imgur.conf``. The standard INI format is used, and
``client_id`` and ``client_secret`` should be placed under the
``oauth`` section, so an example configuration file would be

.. code:: ini

   # you should register your application at
   # http://api.imgur.com/oauth2/addclient
   [oauth]
   client_id = XXXXXXXXXXXXXXX
   client_secret = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

If there is a known refresh token, you can also put ``refresh_token``
in the ``oauth`` section and avoid the authorization process. If not,
see the "Authorization" section on how to generate one automatically.

Authorization
-------------

You can authorize your application and generate a refresh token
automatically using ``imgur-authorize``. Just run::

  imgur-authorize

An authorization URI will be opened in your default browser, and you
will be asked to sign in to Imgur (if you are not already signed
in). Afterwards, you will get a PIN from Imgur, which you can enter in
to the CLI prompt. The program will take care of the rest
automatically. The refresh token will be added to your config file for
future use, so you only need to authorize once.

Alternatively, if you don't call ``imgur-authorize`` explicitly, then
you will be given the option to authorize upon first use of
``imgur-upload``.

.. |Build Status| image:: https://travis-ci.org/zmwangx/imgur.svg?branch=master
   :target: https://travis-ci.org/zmwangx/imgur
