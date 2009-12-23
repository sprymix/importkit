import yaml
import semantix.lang.yaml.loader


class SemantixLangLoaderError(Exception):
    pass


def load(filename):
    if filename.endswith('.yml'):
        with open(filename) as f:
            result = semantix.lang.yaml.loader.Loader.load(f)
            for d in result:
                yield d

        return

    raise SemantixLangLoaderError('unable to load file:  %s' % filename)
