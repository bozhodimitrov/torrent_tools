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


@lru_cache(maxsize=1)
def timeout_interval(default=5):
    return load_config().get('parser').get('interval', default)


@lru_cache(maxsize=1)
def http_cookies():
    return load_config().get('parser').get('cookies', {})


@lru_cache(maxsize=1)
def download_path():
    dl_path = load_config().get('parser').get('dl_path')
    if dl_path:
        return dl_path
    else:
        raise SystemExit('Invalid or missing download path')


@lru_cache(maxsize=1)
def tracker_url():
    url = load_config().get('parser').get('url')
    if not url:
        raise SystemExit('Invalid or missing tracker url')
    else:
        return url
