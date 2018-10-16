import inspect
import json

excluded_classes = [BaseException, Exception, object]


def get_mro(cls):
    return filter(lambda x: x not in excluded_classes, inspect.getmro(cls))


def load_config():
    with open("config.json") as f:
        return json.load(f)
