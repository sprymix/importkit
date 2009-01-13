import yaml
import re
import os
import subprocess

from semantix.utils import merge

class YamlReaderError(Exception): pass
class YamlReader(object):
    @staticmethod
    def read(filename, return_meta=False):
        buffer = file(filename).readlines()

        result = {}
        meta = {}

        meta['filename'] = filename

        for line in buffer:
            if line.startswith('#') or line.startswith('%'):
                if line.startswith('#!'):
                    if line.startswith('#!SCHEMA'):
                        match = re.match(r"""
                                            \#\!SCHEMA
                                                \s+
                                                    (?P<module>
                                                        (?P<schema_module>[a-zA-Z0-9_\.]+)\.
                                                        (?P<schema_class>[a-zA-Z0-9_]+)
                                                    )
                                          """, line, re.X)

                        if match:
                            meta['schema'] = {
                                                'module': match.group('module'),
                                                'schema_module': match.group('schema_module'),
                                                'schema_class': match.group('schema_class')
                                              }
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

                    elif line.startswith('#!CLASS'):
                        match = re.match(r"""
                                            \#\!CLASS
                                                \s+ (?P<name>\w+)
                                                \s+ \( \s*
                                                    (?P<module>
                                                        (?P<parent_module>[a-zA-Z0-9_\.]+)\.
                                                        (?P<parent_class>[a-zA-Z0-9_]+)
                                                    )
                                                \s* \)
                                          """, line, re.X)

                        if match:
                            meta['class'] = {
                                                'name': match.group('name'),
                                                'module': match.group('module'),
                                                'parent_module': match.group('parent_module'),
                                                'parent_class': match.group('parent_class')
                                            }
                        else:
                            raise YamlReaderError('cannot parse #!CLASS directive, line: "%s"' % line)

                    elif line.startswith('#!INSTANCE'):
                        match = re.match(r"""
                                            \#\!INSTANCE
                                                \s+ (?P<name>\w+)
                                                \s+ \( \s*
                                                    (?P<module>
                                                        (?P<class_module>[a-zA-Z0-9_\.]+)\.
                                                        (?P<class_name>[a-zA-Z0-9_]+)
                                                    )
                                                \s* \)
                                          """, line, re.X)

                        if match:
                            meta['instance'] = {
                                                'name': match.group('name'),
                                                'module': match.group('module'),
                                                'class_module': match.group('class_module'),
                                                'class_name': match.group('class_name')
                                            }
                        else:
                            raise YamlReaderError('cannot parse #!CLASS directive, line: "%s"' % line)

                    else:
                        raise YamlReaderError('unknown compiler directive, line: "%s"' % line)

            else:
                break

        result = merge.merge_dicts(result, yaml.load(''.join(buffer)))

        if return_meta:
            return meta, result
        return result


    @staticmethod
    def _get_path(base_filename, rel_filename):
        if rel_filename.startswith('/'):
            return path
        else:
            return os.path.abspath(os.path.dirname(base_filename) + '/' + rel_filename)
