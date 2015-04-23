##
# Copyright (c) 2012 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import unittest

from importkit.python import utils


class TestUtilsLangPythonUtils(unittest.TestCase):
    def test_utils_lang_python_utils_get_top_level_imports(self):
        code = '''
from ... import a, b
from ...b.c import a as e
from a.b import c
import test.test.a as s
try:
  import foo
except:
  import bar as foo

def f():
   import abc
   print()

class A:
   import xyz
   print('aaaaaaaa')'''


        code = compile(code, '', 'exec')
        imports = utils.get_top_level_imports(code)

        self.assertEqual(
          imports, [('...', ('a', 'b')), ('...b.c', ('a',)),
                            ('a.b', ('c',)), ('test.test.a', None),
                            ('foo', None), ('bar', None)])
