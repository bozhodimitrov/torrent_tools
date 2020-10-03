import argparse
import json
import re
from collections import OrderedDict
from functools import lru_cache
from time import sleep

import feedparser


CONFIG_FILE_PATH = 'config.json'
TITLE_PATTERN = re.compile(r'\[.*?\] (?P<title>.*?) \[SEEDERS.*\]')
TORRENT_URL_PATTERN = re.compile(
    r'^(?P<href>http://.*/download\.php\?id=[a-z0-9]{30,40}\&'
    r'f=[a-zA-Z0-9%.-]{1,600}\.torrent&rsspid=[a-z0-9]{30,40})$',
)


class LRU(OrderedDict):
    def __init__(self, maxsize=128, /, *args, **kwds):
        self.maxsize = maxsize
        super().__init__(*args, **kwds)

    def __contains__(self, key):
        found = super().__contains__(key)
        if found:
            self.move_to_end(key)
        else:
            self[key] = None
        return found

    def __getitem__(self, key):
        self.move_to_end(key)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if super().__contains__(key):
            self.move_to_end(key)
        else:
            super().__setitem__(key, value)
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]


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


def extract_title(title):
    title_match = TITLE_PATTERN.search(title)
    if title_match:
        return title_match.group('title').strip()
    else:
        print(f'Bad title {title}')


def extract_url(enclosures):
    if not enclosures or enclosures[0].type != 'application/x-bittorrent':
        print(f'Bad enclosures {enclosures}')
        return

    url_match = TORRENT_URL_PATTERN.search(enclosures[0].href)
    if url_match:
        return url_match.group('href')
    else:
        print(f'Bad URL {enclosures[0].href}')


def tracker():
    rss = feedparser.parse(**parser_config())
    if rss.status != 200 or rss.bozo != 0:
        print(f'Bad status {rss.status}, bozo {rss.bozo}')
        print(f'Bad {rss.bozo_exception}')
        return

    for entry in rss.entries:
        yield (
            entry.id,
            extract_title(entry.title),
            extract_url(entry.enclosures),
        )


def rss_feed(args):
    last_torrents = LRU(cache_limit(), [(tid, None) for tid, *_ in tracker()])

    while True:
        sleep(5)
        for tid, title, url in tracker():
            if tid in last_torrents or not title or not url:
                continue
            elif args.url:
                print(f'{title}\n{url}')
            else:
                print(title)


def main():
    parser = argparse.ArgumentParser(prog='xbtit_feed')
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s 0.0.1',
    )
    parser.add_argument('-u', '--url', action='store_true')
    args = parser.parse_args()
    rss_feed(args)


if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
