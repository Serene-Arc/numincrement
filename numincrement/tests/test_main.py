#!/usr/bin/env python3

import pytest

import numincrement.__main__ as numincrement


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


@pytest.mark.parametrize(('test_value', 'test_format', 'expected'), ((1, (1, 0), '1'),
                                                                     (1, (2, 0), '01'),
                                                                     (1.5, (1, 1), '1.5'),
                                                                     (2.5, (2, 2), '02.50'),
                                                                     (1, (5, 0), '00001'),
                                                                     ))
def test_format_number_string(test_value: [int, float], test_format: tuple[int, int], expected: str):
    result = numincrement._format_number_to_string(test_format, test_value)
    assert result == expected
