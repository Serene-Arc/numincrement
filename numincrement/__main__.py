#!/usr/bin/env python3

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Union

logger = logging.getLogger()
parser = argparse.ArgumentParser()


def _add_options():
    parser.add_argument('expression', type=str)
    parser.add_argument('files', nargs='+')
    parser.add_argument('-n', '--no-act', action='store_true')
    parser.add_argument('-l', '--lazy', action='store_true')

    change_options = parser.add_mutually_exclusive_group()
    change_options.add_argument('-i', '--increment', type=int, default=None, nargs='?', const=1)
    change_options.add_argument('-d', '--decrement', type=int, default=None, nargs='?', const=1)

    parser.add_argument('-v', '--verbose', action='count', default=0)


def _setup_logging(verbosity: int):
    logger.setLevel(1)
    stream = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    if verbosity <= 0:
        stream.setLevel(logging.INFO)
    else:
        stream.setLevel(logging.DEBUG)


def _get_number_format(in_string: str) -> tuple[int, int]:
    match = re.match(r'(?a)(\d*)?\.?(\d*)?', in_string)
    return len(match[1]), len(match[2])


def _format_number_to_string(format_vals: tuple[int, int], val: Union[int, float]) -> str:
    end = str(val - int(val)) if (val - int(val)) else ''
    if end:
        end = end.split('.')[-1].ljust(format_vals[1], '0')
        end = '.' + end
    result = str(int(val)).zfill(format_vals[0]) + end
    result = result.format(val)
    return result


def main(args):
    _setup_logging(args.verbose)

    if args.increment:
        change = args.increment
    elif args.decrement:
        change = abs(args.decrement) * -1
    else:
        logger.warning('No increment or decrement value provided')
        change = 0

    pattern = re.compile(args.expression)
    files = reversed(sorted([Path(file) for file in args.files]))
    for file in files:
        if catches := re.search(pattern, file.name):
            catches = catches.groups()
        else:
            logger.error('No match found in file name {} with regex string {}'.format(file.name, pattern))
            continue
        for catch in catches:
            if not re.match(r'[.\d]+', catch):
                logger.warning(f'Could not change capture {catch}')
                continue
            number_format = _get_number_format(catch)
            number = float(catch)
            number += change
            replacement = _format_number_to_string(number_format, number)
            new_path = file.with_name(file.name.replace(catch, replacement))
            if args.no_act:
                logger.info('Rename: {} -> {}'.format(file, new_path))
            else:
                logger.info('Renaming file {} to {}'.format(file, new_path))
                try:
                    file.rename(new_path)
                except OSError:
                    logger.error('{} already exists'.format(new_path))


if __name__ == '__main__':
    _add_options()
    args = parser.parse_args()
    main(args)
