from semantix.lang.meta import LanguageMeta
from semantix.lang.meta import DocumentContext
from semantix.lang.import_ import ImportContext

# Import languages to register them
import semantix.lang.yaml


class SemantixLangLoaderError(Exception):
    pass


def load(filename):
    (lang, filename) = LanguageMeta.recognize_file(filename)
    if lang:
        with open(filename) as f:
            result = lang.load(f)
            for d in result:
                yield d
        return

    raise SemantixLangLoaderError('unable to load file:  %s' % filename)
