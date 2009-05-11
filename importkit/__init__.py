from semantix.readers.yaml.reader import YamlReader

class SemantixReaderError(Exception):
    pass

def read(filename):
    if filename.endswith('.yml'):
        return YamlReader.read(filename)

    raise SemantixReaderError('unable to read file:  %s' % filename)
