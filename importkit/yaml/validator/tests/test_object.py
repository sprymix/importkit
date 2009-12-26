import yaml

from semantix.lang.meta import Object, ObjectError
from semantix.lang.yaml.validator.tests.base import SchemaTest, result, raises


class A(Object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __eq__(self, other):
        return isinstance(other, A) and other.name == self.name and other.description == self.description

    @classmethod
    def construct(cls, data, context):
        return cls(name=data['name'], description=data['description'])


class Bad(object):
    pass


class CustomValidator(Object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @classmethod
    def construct(cls, data, context):
        name = data['name']
        description = data['description']

        if name != description:
            raise ObjectError('name must be equal to description')

        return cls(name=name, description=description)


class TestObject(SchemaTest):
    @staticmethod
    def setup_class(cls):
        cls.schema = cls.get_schema('ymls/object.yml')

    @result(key='test1', value=A(name='testname', description='testdescription'))
    def test_validator_object(self):
        """
        test1:
            name: testname
            description: testdescription
        """

    @raises(yaml.constructor.ConstructorError, "while constructing a Python object")
    def test_validator_object_fail(self):
        """
        fail:
            name: fail
        """

    @raises(ObjectError, "name must be equal to description")
    def test_validator_object_custom_validation(self):
        """
        customvalidation:
            name: custom
            description: validation
        """
