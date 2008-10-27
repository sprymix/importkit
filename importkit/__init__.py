from semantix.readers.yaml.reader import YamlReader

__all__ = ['read']

class SemantixReaderError(Exception): pass

def read(filename, return_meta = False):
    if filename.endswith('.yml'):
        return YamlReader.read(filename, return_meta)

    raise SemantixReaderError('cannot read file:  %s' % filename)
