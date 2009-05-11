import yaml

class YamlReaderError(Exception):
    pass

class YamlReader(object):
    @staticmethod
    def read(filename):
        with open(filename, 'r') as f:
            return yaml.load(f.read())
