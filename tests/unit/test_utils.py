# -*- coding: utf-8 -*-
"""
test_utils.py - Unit testing of LGR utils module.
"""
from __future__ import unicode_literals

import unittest

from lgr.utils import collapse_codepoints


class TestUtils(unittest.TestCase):

    def test_collapse(self):
        ranges = collapse_codepoints([c for c in range(0x0061, 0x007A + 1)] +
                                     [0x0107] + [0x0137, 0x0138])

        expected_output = [(0x0061, 0x007A),
                           (0x0107, 0x0107),
                           (0x0137, 0x0138)]
        self.assertEqual(ranges, expected_output)

if __name__ == '__main__':
    unittest.main()
