class LanguageMeta(type):
    languages = []

    def __new__(cls, name, bases, dct):
        lang = super(LanguageMeta, cls).__new__(cls, name, bases, dct)
        if 'recognize_file' in dct:
            LanguageMeta.languages.append(lang)
        return lang

    @staticmethod
    def recognize_file(filename, try_append_extension=False):
        for lang in LanguageMeta.languages:
            myfile = lang.recognize_file(filename, try_append_extension)
            if myfile:
                return (lang, myfile)
        return None


class Language(object, metaclass=LanguageMeta):
    pass
