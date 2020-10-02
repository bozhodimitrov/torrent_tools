from collections import deque
import argparse
import re

import feedparser


DEQUE_LIMIT = 100
PARSER_CONFIG_FILENAME = 'config.json'
TITLE_PATTERN = re.compile(r'\[.*?\] (?P<title>.*?) \[SEEDERS.*\]')
TORRENT_URL_PATTERN = re.compile(
    r'^(?P<href>http://(.*)/download\.php\?id=[a-z0-9]{30,40}\&'
    r'f=[a-zA-Z0-9%.-]{1,600}\.torrent&rsspid=[a-z0-9]{30,40})$'
)


def extract_title(title):
    title = title.encode('utf-8')
    title_match = TITLE_PATTERN.search(title)
    if title_match:
        return title_match.group('title').strip()

    print('Bad title {}'.format(title))



def extract_url(enclosures):
    if not enclosures or enclosures[0].type != 'application/x-bittorrent':
        print('Bad enclosures {}'.format(enclosures))
        return

    url_match = TORRENT_URL_PATTERN.search(enclosures[0].href)
    if url_match:
        return url_match.group('href')

    print('Bad URL {}'.format(enclosures[0].href))


def tracker(parser_config):
    rss = feedparser.parse(**parser_config)
    if rss.status != 200 or rss.bozo != 0:
        print('Bad status {}, bozo {}'.format(rss.status, rss.bozo))
        print('Bad {}'.format(rss.bozo_exception))
        return

    for entry in rss.entries:
        yield (
            entry.id,
            extract_title(entry.title),
            extract_url(entry.enclosures)
        )


def rss_feed(args):
    last_torrents = deque((tid for tid, _, _ in extractor()), DEQUE_LIMIT)
    parser_config = load_json(PARSER_CONFIG_FILENAME)

    while True:
        sleep(5)
        for tid, title, url in tracker(parser_config):
            if tid in last_torrents:
                continue

            last_torrents.append(tid)
            if not title or not url:
                print('Bad \n{}\n{}\n{}\n'.format(tid, title, url))
                continue

            yield title, url


def load_json(filename):
    try:
        with open(filename) as json_config_file:
            return json.load(json_config_file)
    except Exception:
        print('Configuration file missing/error')
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(prog='xbtit_feed')
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s 0.0.1',
    )
    args = parser.parse_args()
    rss_feed(args)


if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
