import argparse
from asyncio import get_event_loop
from base64 import b64encode

from aioconsole.stream import aprint
from aioconsole.stream import get_standard_streams
from deluge_client import LocalDelugeRPCClient

from utils.config import download_path


def load_torrent(filename, torrent_content, dl_path=download_path()):
    metadata = (
        filename, b64encode(torrent_content), {'download_location': dl_path},
    )

    for _ in range(3):
        try:
            with LocalDelugeRPCClient() as deluge:
                deluge.core.add_torrent_file(*metadata)
                break
        except OSError:
            pass
    else:
        return f'Failed to download: {filename}'


async def torrent_download(name, url):
    # TODO: implement download
    loop = get_event_loop()
    error = await loop.run_in_executor(None, load_torrent, name, url)
    if error:
        await aprint(error, use_stderr=True)


async def torrent_feed(args, encoding='utf-8'):
    reader, _ = await get_standard_streams()
    while True:
        try:
            name, url = await reader.__anext__(), await reader.__anext__()
        except StopAsyncIteration:
            break

        name, url = name.decode(encoding), url.decode(encoding)
        await aprint(f'{name}{url}', end='')

        if not args.just_print:
            await torrent_download(name, url)


async def _main():
    parser = argparse.ArgumentParser(prog='deluge-dl')
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s 0.0.1',
    )
    parser.add_argument('--just-print', action='store_true')
    args = parser.parse_args()

    await torrent_feed(args)


def main():
    loop = get_event_loop()
    try:
        loop.run_until_complete(_main())
    except KeyboardInterrupt:
        raise SystemExit(130)


if __name__ == '__main__':
    exit(main())
