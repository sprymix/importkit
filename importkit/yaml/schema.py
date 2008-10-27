import subprocess
from semantix import validator

class YamlValidationError(Exception): pass
class Base(object):
    schema = None
    schema_file = ''

    @classmethod
    def validate(cls, meta, dct):
        if 'marshalled' in meta and meta['marshalled']:
            return

        print 'validating >> ' + meta['filename']

        return cls.schema.check(dct)

    @classmethod
    def validate_kwalify(cls, filename):
        kwalify = subprocess.Popen(['kwalify', '-lf', cls.schema_file, filename],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        (stdout, stderr) = kwalify.communicate()

        if stdout.find('INVALID') >= 0 or stderr.find('ERROR') >= 0:
            raise YamlValidationError('Failed to validate file: %s\n\nValidator output: \n%s' %
                                           (filename, stderr + stdout))

    @classmethod
    def _create_class(cls, meta, dct):
        return type(meta['class']['name'], (Base,), {'schema_file': meta['filename'], 'schema': validator.Schema(dct)})
