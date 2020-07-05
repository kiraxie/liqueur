import os
import json
import yaml


class Config(dict):
    def __init__(self, defaults=None):
        dict.__init__(self, defaults or {})

    @classmethod
    def from_json(cls, filename):
        d = {}
        with open(filename, 'r') as json_file:
            d = json.loads(json_file.read())
        return cls(d)

    @classmethod
    def from_yaml(cls, filename):
        d = {}
        with open(filename, 'r') as yaml_file:
            d = yaml.load(yaml_file, Loader=yaml.Loader)
        return cls(d)

    def from_mapping(self, *mapping, **kwargs):
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], "items"):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError(
                "expected at most 1 positional argument, got %d" % len(mapping)
            )
        mappings.append(kwargs.items())
        for mapping in mappings:
            for (key, value) in mapping:
                self[key] = value
        return
