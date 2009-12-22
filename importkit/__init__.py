import yaml
import semantix.lang.yaml.reader

class SemantixReaderError(Exception):
    pass


def read(filename):
    if filename.endswith('.yml'):
        return semantix.lang.yaml.reader.YamlReader.read(filename)

    raise SemantixReaderError('unable to read file:  %s' % filename)
