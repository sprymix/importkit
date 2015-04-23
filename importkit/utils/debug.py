##
# Copyright (c) 2015 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


try:
    from metamagic.utils.debug import debug
except ImportError:
    def debug(func):
        return func
