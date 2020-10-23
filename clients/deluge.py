import argparse
from contextlib import redirect_stdout
from sys import stderr
from sys import stdin
from sys import stdout


def torrent_feed(args):
    for name, url in zip(*[iter(stdin)]*2):
        if args.just_print:
            print(f'{name}{url.strip()}', file=stdout, flush=True)


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

    with redirect_stdout(stderr):
        torrent_feed(args)


def main():
    try:
        exit(_main())
    except KeyboardInterrupt:
        raise SystemExit(130)


if __name__ == '__main__':
    main()
