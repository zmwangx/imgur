#!/usr/bin/env python3

import os
import setuptools

here = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(here, 'README.rst')) as readme:
    long_description = readme.read()

setuptools.setup(
    name='imgur',
    version='0.1',
    description='wrapper around pyimgur',
    long_description=long_description,
    url='https://github.com/zmwangx',
    author='Zhiming Wang',
    author_email='zmwangx@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Graphics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='image imgur upload',
    packages=['imgur'],
    install_requires=[
        'pyimgur>=0.5.2',
        'zmwangx>=0.1.31+g932db22',
    ],
    dependency_links = [
        'git+https://github.com/zmwangx/pyzmwangx.git@master#egg=zmwangx-0.1.31',
    ],
    entry_points={
        'console_scripts': [
            'imgur-authorize=imgur.authorize:main',
            'imgur-save=imgur.save:main',
            'imgur-upload=imgur.upload:main',
        ]
    },
    test_suite='tests',
)
