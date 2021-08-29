# YAMLiny - a tiny parser for a tiny subset of YAML

YAMLiny is a parser for a tiny subset of YAML syntax, although behavior
may differ slightly in certain scenarios.

## Install

YAMLiny is on PyPi, install with pip.

```bash
pip install yamliny
```

## Usage

YAMLiny currently only has parsing functionality.

```python
import yamliny

# this is pretty much the entirety of what you can do with YAMLiny syntax at the moment
yamliny_text = """
key: value
multivalue-key: # you can also use inline comments!
    array: [one, two, three]
    key: value
""".strip()

content = yamliny.loads(yamliny_text)
# content is a dict with:
# {'key': 'value',
#  'multivalue-key': {'array': ['one', 'two', 'three'], 'key': 'value'}}
```
