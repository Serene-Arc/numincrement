#!/usr/bin/env python3

import argparse
import re
from decimal import Decimal
from pathlib import Path

import pytest

import numincrement.__main__ as numincrement


@pytest.fixture()
def args():
    args = argparse.Namespace
    args.expression = r'(\d)'
    args.files = []
    args.increment = 1
    args.decrement = None
    args.no_act = False
    args.verbose = 0

    return args


@pytest.mark.parametrize(('test_string', 'expected'), (
    ('1', (1, 0)),
    ('10', (2, 0)),
    ('1.1', (1, 1)),
    ('01', (2, 0)),
    ('001', (3, 0)),
    ('001.10', (3, 2)),
    ('.100', (0, 3)),
))
def test_get_number_format(test_string: str, expected: tuple[int, int]):
    result = numincrement._get_number_format(test_string)
    assert result == expected


@pytest.mark.parametrize(('test_value', 'test_format', 'expected'), ((Decimal('1'), (1, 0), '1'),
                                                                     (Decimal('1'), (2, 0), '01'),
                                                                     (Decimal('1.5'), (1, 1), '1.5'),
                                                                     (Decimal('2.5'), (2, 2), '02.50'),
                                                                     (Decimal('1'), (5, 0), '00001'),
                                                                     (Decimal('1.5'), (0, 1), '1.5'),
                                                                     (Decimal('1.5'), (1, 0), '1.5'),
                                                                     ))
def test_format_number_string(test_value: Decimal, test_format: tuple[int, int], expected: str):
    result = numincrement._format_number_to_string(test_format, test_value)
    assert result == expected


@pytest.mark.parametrize(('test_expression', 'test_path', 'change', 'expected'), (
    (r'(\d)', Path('1.txt'), Decimal('1'), Path('2.txt')),
    (r'(\d)', Path('1.txt'), Decimal('-1'), Path('0.txt')),
    (r'(\d)', Path('1_2.txt'), Decimal('1'), Path('2_2.txt')),
    (r'_(\d)', Path('1_2.txt'), Decimal('1'), Path('1_3.txt')),
    (r'_(\d)', Path('1_20.txt'), Decimal('1'), Path('1_30.txt')),
    (r'_(\d+)', Path('3_21.txt'), Decimal('1'), Path('3_22.txt')),
    (r'(\d)_(\d)', Path('1_2.txt'), Decimal('1'), Path('2_3.txt')),
    (r'(\d)_\d', Path('1_2.txt'), Decimal('1'), Path('2_2.txt')),
    (r'_\d(\d+)', Path('3_21.txt'), Decimal('-3'), Path('3_2-2.txt')),
    (r'_\d(\d+)', Path('3_21.txt'), Decimal('10'), Path('3_211.txt')),
))
def test_path_generation_integers(test_expression: str, test_path: Path, change: Decimal, expected: Path):
    catches = re.search(test_expression, test_path.name)
    result = test_path
    result = numincrement.change_path_name(catches, change, result)
    assert result == expected


@pytest.mark.parametrize(('test_expression', 'test_path', 'change', 'expected'), (
    (r'(\d)', Path('1_2.txt'), Decimal('0.1'), Path('1.1_2.txt')),
    (r'([\d.]+)', Path('1.00_2.txt'), Decimal('0.1'), Path('1.10_2.txt')),
    (r'([\d.]+)', Path('1.00000_2.txt'), Decimal('0.1'), Path('1.10000_2.txt')),
    (r'(\d)', Path('1_2.txt'), Decimal('0.01'), Path('1.01_2.txt')),
    (r'\d_(\d)', Path('1_2.txt'), Decimal('0.5'), Path('1_2.5.txt')),
))
def test_path_generation_decimal(test_expression: str, test_path: Path, change: Decimal, expected: Path):
    catches = re.search(test_expression, test_path.name)
    result = test_path
    result = numincrement.change_path_name(catches, change, result)
    assert result == expected


@pytest.mark.parametrize(('test_paths', 'test_expression', 'change', 'expected_files'), (
    (('1.txt', '2.txt'), r'^(\d)', Decimal('1'), {'2.txt', '3.txt'}),
    (('1.txt', '1_2.txt'), r'^(\d)', Decimal('1'), {'2.txt', '2_2.txt'}),
    (('1_1.txt', '2.txt', '3_1.txt'), r'_(\d)', Decimal('1'), {'1_2.txt', '2.txt', '3_2.txt'}),
))
def test_integration(
        args: argparse.Namespace,
        test_paths: list[str],
        test_expression: str,
        change: int,
        expected_files: set[str],
        tmp_path: Path):
    args.increment = change
    args.expression = test_expression
    args.files = [Path(tmp_path / test_string) for test_string in test_paths]
    for file in args.files:
        file.touch()
    numincrement.main(args)
    results = set(sorted([file.name for file in tmp_path.iterdir() if file.is_file()]))
    assert results == expected_files
