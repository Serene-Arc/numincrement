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


def _fix_midway_files(midway_files: list[Path]):
    for midway_file in midway_files:
        fixed_name = midway_file.with_name(midway_file.name.strip('.mid'))
        midway_file.rename(fixed_name)
        logger.debug('Fixed midway name for {}'.format(fixed_name))


def change_path_name(catch: re.Match, change: int, file: Path) -> Path:
    new_path = file
    for m, match in enumerate(catch.groups(), start=1):
        number_format = _get_number_format(match)
        try:
            number = float(match)
        except ValueError:
            logger.error('{} is not a string which can be incremented/decremented'.format(match))
            continue
        number += change
        replacement = _format_number_to_string(number_format, number)
        new_name = new_path.name[:catch.start(m)] + replacement + new_path.name[catch.end(m):]
        new_path = new_path.with_name(new_name)
    return new_path


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
    files = [Path(file) for file in args.files]
    midway_files = []

    for file in files:
        if not (match_hits := re.search(pattern, file.name)):
            logger.error('No match found in file name {} with regex string {}'.format(file.name, pattern))
            continue
        new_path = change_path_name(match_hits, change, file)
        if args.no_act:
            print('Rename: {} -> {}'.format(file, new_path))
        else:
            logger.info('Renaming file {} to {}'.format(file, new_path))
            midway_name = new_path.with_name(new_path.name + '.mid')
            midway_files.append(midway_name)
            try:
                file.rename(midway_name)
            except OSError:
                logger.error('{} already exists'.format(new_path))

    _fix_midway_files(midway_files)


def cmd_entry():
    _add_options()
    args = parser.parse_args()
    main(args)


if __name__ == '__main__':
    cmd_entry()
