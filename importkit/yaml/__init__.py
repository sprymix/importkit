import yaml
import re
import os
import subprocess

from ... import merge

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
                if line.startswith('#!'):
                    if line.startswith('#!SCHEMA'):
                        match = re.match(r"""
                                            \#\!SCHEMA
                                                \s '(?P<filename>.*)'
                                          """, line, re.X)

                        if match:
                            schema = match.group('filename')
                        else:
                            raise YamlReaderError('cannot parse #!SCHEMA directive, line: "%s"' % line)


                    elif line.startswith('#!INCLUDE'):
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

                            sections = match.group('sections').split(',')
                            for section in sections:
                                section = section.strip()

                                if section == '*':
                                    if len(sections) == 1:
                                        chunks = parts
                                        break
                                    else:
                                        raise YamlReaderError('invalid "*" use, line: %s' % line)

                                if section in parts:
                                    chunks[section] = parts[section]
                                else:
                                    raise YamlReaderError('cannot find section "%s" in file: %s' % (section, fn))

                            result = merge.merge_dicts(result, chunks)
                        else:
                            raise YamlReaderError('cannot parse #!INCLUDE directive, line: "%s"' % line)

                    else:
                        raise YamlReaderError('unknown compiler directive, line: "%s"' % line)

            else:
                break

        if schema:
            schema = YamlReader._get_path(filename, schema)
            kwalify = subprocess.Popen(['kwalify', '-lf', schema, os.path.abspath(filename)],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            (stdout, stderr) = kwalify.communicate()

            if stdout.find('INVALID') >= 0 or stderr.find('ERROR') >= 0:
                raise YamlValidationError('Failed to validate file: %s\n\nValidator output: \n%s' %
                                               (os.path.abspath(filename), stderr + stdout))

        return merge.merge_dicts(result, yaml.load(''.join(buffer)))

    @staticmethod
    def _get_path(base_filename, rel_filename):
        if rel_filename.startswith('/'):
            return path
        else:
            return os.path.abspath(os.path.dirname(base_filename) + '/' + rel_filename)
