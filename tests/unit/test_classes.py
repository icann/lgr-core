# -*- coding: utf-8 -*-
"""
test_classes.py - Unit testing of class module.
"""
from __future__ import unicode_literals

import unittest

from lgr.classes import (Class,
                         ComplementClass,
                         UnionClass,
                         IntersectionClass,
                         DifferenceClass,
                         SymmetricDifferenceClass)
from lgr.exceptions import LGRFormatException


class TestClass(unittest.TestCase):

    @unittest.skip("need mock of Unicode Database")
    def test_pattern_basic_class(self):
        basic_class = Class("test-class", codepoints=[0x0060, 0x0061])
        self.assertEqual(basic_class.get_pattern({}, {}, None),
                         "[\\x{60}\\x{61}]")

    @unittest.skip("need mock of Unicode Database")
    def test_pattern_complement(self):
        basic_class = Class("test-class", codepoints=[0x0060, 0x0061])
        compl_class = ComplementClass()
        compl_class.add_child(basic_class)
        self.assertEqual(compl_class.get_pattern({}, {}, None),
                         "[^\\x{60}\\x{61}]")

    @unittest.skip("need mock of Unicode Database")
    def test_pattern_union(self):
        base_class_1 = Class("test-class-1", codepoints=[0x0060, 0x0061])
        base_class_2 = Class("test-class-2", codepoints=[0x0065, 0x0066])
        compl_class = UnionClass()
        compl_class.add_child(base_class_1)
        compl_class.add_child(base_class_2)
        self.assertEqual(compl_class.get_pattern({}, {}, None),
                         "[\\x{60}\\x{61}][\\x{65}\\x{66}]")

    @unittest.skip("need mock of Unicode Database")
    def test_pattern_by_ref(self):
        basic_class = Class("test-class", codepoints=[0x0060, 0x0061])
        by_ref_class = Class(by_ref='test-class')
        classes_lookup = {
            'test-class': basic_class
        }
        self.assertEqual(by_ref_class.get_pattern({}, classes_lookup, None),
                         basic_class.get_pattern({}, {}, None))

    def test_complement_class(self):
        complement_class = ComplementClass()

        complement_class.add_child(Class(codepoints=[1, 2]))
        with self.assertRaises(LGRFormatException) as exc_cm:
            complement_class.add_child(Class(codepoints=[1, 2]))
        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

    def test_intersection_class(self):
        intersection_class = IntersectionClass()

        intersection_class.add_child(Class(codepoints=[1, 2]))
        intersection_class.add_child(Class(codepoints=[1, 2]))
        with self.assertRaises(LGRFormatException) as exc_cm:
            intersection_class.add_child(Class(codepoints=[1, 2]))
        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

    def test_difference_class(self):
        difference_class = DifferenceClass()

        difference_class.add_child(Class(codepoints=[1, 2]))
        difference_class.add_child(Class(codepoints=[1, 2]))
        with self.assertRaises(LGRFormatException) as exc_cm:
            difference_class.add_child(Class(codepoints=[1, 2]))
        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

    def test_symmetric_difference_class(self):
        difference_class = SymmetricDifferenceClass()

        difference_class.add_child(Class(codepoints=[1, 2]))
        difference_class.add_child(Class(codepoints=[1, 2]))
        with self.assertRaises(LGRFormatException) as exc_cm:
            difference_class.add_child(Class(codepoints=[1, 2]))
        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

    def test_by_ref(self):
        with self.assertRaises(LGRFormatException) as exc_cm:
            Class(by_ref='ref', name='name')
        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.BY_REF_AND_OTHER)

        with self.assertRaises(LGRFormatException) as exc_cm:
            Class(by_ref='ref', from_tag='tag')
        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.BY_REF_AND_OTHER)

        with self.assertRaises(LGRFormatException) as exc_cm:
            Class(by_ref='ref', unicode_property='prop')
        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.BY_REF_AND_OTHER)

        with self.assertRaises(LGRFormatException) as exc_cm:
            Class(by_ref='ref', ref=['1'])
        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.BY_REF_AND_OTHER)

    def test_validate_by_ref_class(self):
        cls = Class(by_ref='named-class')
        cls.validate([None], {}, {'named-class': None})

        with self.assertRaises(LGRFormatException) as exc_cm:
            cls.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_BY_REF)

    def test_validate_named_class(self):
        cls = Class(name='named-rule')
        cls.validate([], {}, {})

        with self.assertRaises(LGRFormatException) as exc_cm:
            cls.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_TOP_LEVEL_NAME)

    def test_validate_complement_class(self):
        cls = ComplementClass()

        with self.assertRaises(LGRFormatException) as exc_cm:
            cls.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        cls.add_child(Class(codepoints=[1, 2]))
        cls.validate([None], {}, {})

    def test_validate_union_class(self):
        cls = UnionClass()

        with self.assertRaises(LGRFormatException) as exc_cm:
            cls.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        cls.add_child(Class(codepoints=[1, 2]))
        with self.assertRaises(LGRFormatException) as exc_cm:
            cls.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        cls.add_child(Class(codepoints=[1,2]))
        cls.validate([None], {}, {})

    def test_validate_intersection_class(self):
        cls = IntersectionClass()

        with self.assertRaises(LGRFormatException) as exc_cm:
            cls.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        cls.add_child(Class(codepoints=[1, 2]))
        with self.assertRaises(LGRFormatException) as exc_cm:
            cls.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        cls.add_child(Class(codepoints=[1,2]))
        cls.validate([None], {}, {})

    def test_validate_difference_class(self):
        cls = DifferenceClass()

        with self.assertRaises(LGRFormatException) as exc_cm:
            cls.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        cls.add_child(Class(codepoints=[1, 2]))
        with self.assertRaises(LGRFormatException) as exc_cm:
            cls.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        cls.add_child(Class(codepoints=[1,2]))
        cls.validate([None], {}, {})

    def test_validate_symmetric_difference_class(self):
        cls = SymmetricDifferenceClass()

        with self.assertRaises(LGRFormatException) as exc_cm:
            cls.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        cls.add_child(Class(codepoints=[1, 2]))
        with self.assertRaises(LGRFormatException) as exc_cm:
            cls.validate([None], {}, {})

        the_exception = exc_cm.exception
        self.assertEqual(the_exception.reason,
                         LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        cls.add_child(Class(codepoints=[1,2]))
        cls.validate([None], {}, {})


if __name__ == '__main__':
    import logging
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
