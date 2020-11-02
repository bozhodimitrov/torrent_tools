import argparse
from asyncio import get_event_loop

from aioconsole.stream import aprint
from aioconsole.stream import get_standard_streams


async def torrent_feed(args):
    reader, writer = await get_standard_streams()
    while True:
        try:
            name, url = await reader.__anext__(), await reader.__anext__()
        except StopAsyncIteration:
            break

        if args.just_print:
            await aprint(
                f'{name.decode()}{url.decode()}',
                streams=(reader, writer),
                end='',
            )


def _main():
    parser = argparse.ArgumentParser(prog='deluge-dl')
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s 0.0.1',
    )
    parser.add_argument('--just-print', action='store_true')
    args = parser.parse_args()

    loop = get_event_loop()
    try:
        loop.run_until_complete(torrent_feed(args))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


def main():
    try:
        exit(_main())
    except KeyboardInterrupt:
        raise SystemExit(130)


if __name__ == '__main__':
    main()
