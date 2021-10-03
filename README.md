# YAMLiny - a tiny parser for a tiny subset of YAML

YAMLiny is a parser for a tiny subset of YAML syntax, although behavior
may differ slightly in certain scenarios.

## Install

YAMLiny is on PyPi, install with pip.

```bash
pip install yamliny
```

## Usage

YAMLiny currently offers parsing of text to a dictionary with `yamliny.loads`
and dumping a dictionary to YAMLiny text with `yamliny.dumps`.

```python
import yamliny

# this is pretty much the entirety of what you can do with YAMLiny syntax at the moment
yamliny_text = """
key: value
multivalue-key: # you can also use inline comments!
    array: [one, two, three]
    key: value
""".strip()

# You can turn YAMLiny into a dictionary with `loads`
content = yamliny.loads(yamliny_text)
# content is a dict with:
# {'key': 'value',
#  'multivalue-key': {'array': ['one', 'two', 'three'], 'key': 'value'}}

# And go back to YAMLiny with `dumps`
yamliny_text_again = yamliny.dumps(content)
```
