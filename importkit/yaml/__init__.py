import yaml
import re
import os

import semantix.helper as helper

class YamlReaderError(Exception): pass
class YamlValidationError(Exception): pass
class YamlReader(object):
    @staticmethod
    def read(filename):
        buffer = file(filename).readlines()

        schema = ''
        result = {}

        for line in buffer:
            if line.startswith('#') or line.startswith('%'):
                if line.startswith('#!SCHEMA'):
                    match = re.match(r"""
                                        \#\!SCHEMA
                                            \s '(?P<filename>.*)'
                                      """, line, re.X)

                    schema = match.group('filename')

                if line.startswith('#!INCLUDE'):
                    match = re.match(r"""
                                        \#\!INCLUDE
                                            \s '(?P<filename>.*)'
                                            \s \(
                                                (?P<sections>.*)
                                               \)
                                      """, line, re.X)

                    if match:
                        chunks = {}
                        fn = YamlReader._get_path(filename, match.group('filename'))

                        parts = YamlReader.read(fn)

                        for section in match.group('sections').split(','):
                            section = section.strip()

                            if section in parts:
                                chunks[section] = parts[section]
                            else:
                                raise YamlReaderError('cannot find section "%s" in file: %s' % (section, fn))

                        result = helper.merge_dicts(result, chunks)

            else:
                break

        if schema:
            schema = YamlReader._get_path(filename, schema)
            output = os.popen('kwalify -lf ' + schema + ' ' + os.path.abspath(filename)).read()

            if output.find('INVALID') >= 0:
                raise YamlValidationError('Failed to validate file: %s\n\nValidator output: \n%s' %
                                               (os.path.abspath(filename), output))

        return helper.merge_dicts(result, yaml.load(''.join(buffer)))

    @staticmethod
    def _get_path(base_filename, rel_filename):
        if rel_filename.startswith('/'):
            return path
        else:
            return os.path.abspath(os.path.dirname(base_filename) + '/' + rel_filename)
