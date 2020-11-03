import argparse
from asyncio import get_event_loop
from asyncio import get_running_loop
from asyncio import sleep as asleep
from asyncio import TimeoutError
from errno import ECONNRESET
from functools import lru_cache
from signal import SIGINT
from signal import signal
from urllib.parse import urljoin

from aioconsole.stream import aprint
from aiohttp import ClientOSError
from aiohttp import ClientPayloadError
from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import InvalidURL
from aiohttp import TCPConnector
from lxml.etree import ParserError
from lxml.etree import XMLSyntaxError
from lxml.html import fromstring
from lxml.html import HTMLParser

from utils.cache import LRU
from utils.config import cache_limit
from utils.config import parser_config


CONTENT_PATH = "descendant-or-self::tr[contains(@class, 'hl-tr')]"

NAME_PATH = "string(descendant::td[contains(@class, 'tLeft')]/"\
    "descendant::a[contains(@class, 'tLink')])"

LINK_PATH = "string(descendant::td[contains(@class, 'small')]/"\
    "a[@title='Download' or contains(@class, 'tr-dl')]/@href)"

HTTP_EXCEPTIONS = (
    ClientOSError,
    ClientPayloadError,
    InvalidURL,
    OSError,
    TimeoutError,
)


@lru_cache(maxsize=1)
def parser():
    return HTMLParser(collect_ids=False)


def extractor(html):
    try:
        root = fromstring(html, parser=parser())
    except (ParserError, XMLSyntaxError):
        return

    for tag in reversed(root.xpath(CONTENT_PATH)):
        name, link = tag.xpath(NAME_PATH), tag.xpath(LINK_PATH)
        if name and link:
            yield name.strip(), urljoin(tracker_url(), link.strip())


@lru_cache(maxsize=1)
def tracker_url():
    url = parser_config().get('url')
    if not url:
        raise SystemExit('Invalid tracker url')
    else:
        return url


async def tracker(session):
    try:
        resp = await session.get(tracker_url(), allow_redirects=False)
    except HTTP_EXCEPTIONS as e:
        if isinstance(e, OSError) and e.errno != ECONNRESET:
            await aprint(f'Connection error: {str(e)}', use_stderr=True)
        return

    async with resp:
        if resp.status != 200:
            return

        try:
            html = await resp.text()
        except TimeoutError:
            return

        for torrent_info in extractor(html):
            yield torrent_info


async def http_feed(args):
    get_running_loop().create_task(_wakeup())

    config = parser_config()
    options = dict(
        cookies=config['cookies'],
        connector=TCPConnector(
            keepalive_timeout=299,
            enable_cleanup_closed=True,
        ),
        timeout=ClientTimeout(total=config['interval']),
    )

    async with ClientSession(**options) as session:
        seen_urls = LRU(
            cache_limit(), [(url, None) async for _, url in tracker(session)],
        )

        if not seen_urls:
            raise SystemExit('Expired credentials')
            return

        while True:
            async for torrent, url in tracker(session):
                if url not in seen_urls:
                    await aprint(f'{torrent}\n{url}', flush=True)

            await asleep(config['interval'])


async def _wakeup():
    while True:
        await asleep(1)


async def _main():
    parser = argparse.ArgumentParser(prog='torrentpier_feed')
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s 0.0.1',
    )
    parser.add_argument('-u', '--url', action='store_true')
    args = parser.parse_args()

    await http_feed(args)


def _shutdown_handler(signal, frame):
    raise KeyboardInterrupt


def main():
    signal(SIGINT, _shutdown_handler)
    loop = get_event_loop()
    try:
        exit(loop.run_until_complete(_main()))
    except KeyboardInterrupt:
        raise SystemExit(130)


if __name__ == '__main__':
    main()
