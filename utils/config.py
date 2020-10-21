import json
from functools import lru_cache


CONFIG_FILE_PATH = 'config.json'


@lru_cache(maxsize=1)
def load_config(filename=CONFIG_FILE_PATH):
    try:
        with open(filename) as json_config_file:
            return json.load(json_config_file)
    except FileNotFoundError:
        print('Configuration file missing')
        raise SystemExit(1)
    except json.decoder.JSONDecodeError:
        print('Configuration file decoding error')
        raise SystemExit(1)


def cache_limit():
    return load_config().get('cache_limit')


def parser_config():
    return load_config().get('parser')
