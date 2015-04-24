##
# Copyright (c) 2008-2015 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import os

from setuptools import setup


readme = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()


def find_packages(*roots):
    result = set()
    for root in roots:
        for dirpath, _, _ in os.walk(root):
            package = dirpath.replace(os.path.sep, '.')
            if '__pycache__' not in package:
                result.add(package)
    return result


setup_args = {
    'name':             'importkit',
    'version':          '0.5.0',
    'description':      ('Importkit is a Python library for making anything '
                         'importable as a Python module.'),
    'long_description': readme,
    'maintainer':       'Sprymix Inc.',
    'maintainer_email': 'into@sprymix.com',
    'url':              'https://github.com/sprymix/importkit',
    'platforms':        ['any'],
    'ext_modules':      [],

    'packages':         find_packages('importkit'),
    'include_package_data': True,
    'exclude_package_data': {
        '': ['.gitignore']
    },

    'install_requires': [
        'PyYAML>=3.11'
    ],

    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4'
    ]
}


setup(**setup_args)
