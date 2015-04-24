importkit
=========

Importkit is a Python library for making anything importable as a Python module.

Importkit uses and extends ``importlib``, introduced in Python 3.1, to provide
a straightforward framework for creating importers, allowing non-Python code or
data to be ``import``-ed seamlessly.

Importkit includes an implementation of a generic, schema-based YAML DSL that
makes it easy to represent complex objects in a robust declarative format.

Importkit also implements module tagging and automatic translation, which makes
it possible to use general module dependency graph to perform cross-platform
builds from a single source.
