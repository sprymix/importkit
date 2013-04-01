##
# Copyright (c) 2011 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import dis
import types


def get_top_level_imports(code):
    assert isinstance(code, types.CodeType)

    imports = []

    ops = iter(dis.Bytecode(code))

    try:
        c1 = next(ops)
        c2 = next(ops)
    except StopIteration:
        return imports

    while True:
        try:
            c3 = next(ops)
        except StopIteration:
            return imports

        if c3.opname == 'IMPORT_NAME':
            assert c1.opname == 'LOAD_CONST'
            assert c2.opname == 'LOAD_CONST'

            imports.append((c1.argval * '.' + c3.argval, c2.argval))

        c1 = c2
        c2 = c3
