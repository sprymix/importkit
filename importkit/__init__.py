from semantix.lib.readers.yaml import YamlReader

__all__ = ['read']

class SemantixReaderError(Exception): pass

def read(filename):
    if filename.endswith('.yml'):
        return YamlReader.read(filename)

    raise SemantixReaderError('cannot read file:  %s' % filename)
