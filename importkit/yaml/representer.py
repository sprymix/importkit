##
# Copyright (c) 2014 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import decimal

from yaml import representer


class FrozensetRepresenter(representer.SafeRepresenter):
    def represent_frozenset(self, data):
        value = {k: None for k in data}
        return self.represent_mapping(
            'tag:importkit.magic.io,2009/importkit/frozenset', value)


representer.SafeRepresenter.add_representer(frozenset,
    FrozensetRepresenter.represent_frozenset)


class DecimalRepresenter(representer.SafeRepresenter):
    def represent_decimal(self, data):
        value = str(data)
        return self.represent_scalar(
            'tag:importkit.magic.io,2009/importkit/decimal', value)


representer.SafeRepresenter.add_representer(decimal.Decimal,
    DecimalRepresenter.represent_decimal)
