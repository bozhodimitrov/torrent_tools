import argparse


def main():
    parser = argparse.ArgumentParser(prog='xbtit_feed')
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s 0.0.1',
    )
    args = parser.parse_args()


if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
