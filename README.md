# YAMLite - parser for a tiny subset of YAML

YAMLite is a parser for a tiny subset of YAML syntax, although behavior
may differ slightly in certain scenarios.

## Install

YAMLite is on PyPi, install with pip.

```bash
pip install yamlite
```

## Usage

YAMLite currently only has parsing functionality.

```python
import yamlite

# this is pretty much the entirety of what you can do with YAMLite syntax at the moment
yamlite_text = """
key: value
multivalue-key: # you can also use inline comments!
    array: [one, two, three]
    key: value
""".strip()

content = yamlite.loads(yamlite_text)
# content is a dict with:
# {'key': 'value',
#  'multivalue-key': {'array': ['one', 'two', 'three'], 'key': 'value'}}
```
