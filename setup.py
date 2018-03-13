#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='atlasbroker',
    version='1.1.3',
    python_requires='>=3.5',
    packages=find_packages(),
    install_requires=['flask', 'openbrokerapi==1.0.0', 'pymongo', 'pwgen', 'atlasapi'],

    # Metadata
    author="Yellow Pages Inc.",
    author_email="cloud@yp.ca",
    license="Apache License 2.0",
    description="Kubernetes Broker for MongoDB Atlas Cloud provider",
    long_description=open('README.rst').read(),
    url="https://github.com/mickybart/python-atlasbroker",
    keywords=["atlas", "mongo", "mongodb", "cloud", "kubernetes", "broker"],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        'Operating System :: OS Independent',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    extras_require={}

)
