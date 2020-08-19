#!/usr/bin/env python

import os
import sys

if hasattr(os, 'link'):
    del os.link  # Hack workaround for http://bugs.python.org/issue8876

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

# https://stackoverflow.com/questions/62114945/attributeerror-parsedrequirement-object-has-no-attribute-req
install_reqs = parse_requirements('requirements.txt', session=False)
try:
    req_list = [str(ir.req) for ir in install_reqs]  # Pip version < 20
except AttributeError:
    req_list = [str(ir.req) for ir in install_reqs]  # Pip version >= 20


readme = open('README.rst').read()
# doclink = """
# Documentation
# -------------
#
# The full documentation is at http://frecency.rtfd.org."""
doclink = ''
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='frecency',
    version='0.1.0',
    description='An implementation of exponentially weighted frecency, with advanced structures and a Django Field.',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author="Michael J.T. O'Kelly",
    author_email='mokelly@gmail.com',
    url='https://github.com/mokelly/frecency',
    packages=find_packages(exclude=['test*']),
    package_dir={'frecency': 'frecency'},
    include_package_data=True,
    install_requires=req_list,
    license='MIT',
    keywords=('frecency', 'frequency', 'recency', 'django', 'statistics', 'counting', 'measurement', 'data science'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
