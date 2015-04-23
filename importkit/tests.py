##
# Copyright (c) 2015 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import os.path
import unittest


if __name__ == '__main__':
    from importkit.import_ import install
    install()
    from importkit import languages

    start = os.path.dirname(os.path.dirname(__file__))
    suite = unittest.defaultTestLoader.discover(start)
    runner = unittest.TextTestRunner()
    runner.run(suite)
