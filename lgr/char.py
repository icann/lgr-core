# -*- coding: utf-8 -*-
"""
char.py - Definition of base classes for character objects.
"""
from __future__ import unicode_literals
import logging

from lgr.exceptions import (CharAlreadyExists,
                            NotInLGR,
                            RangeAlreadyExists,
                            LGRFormatException,
                            VariantAlreadyExists)
from lgr.utils import cp_to_str, format_cp

logger = logging.getLogger(__name__)


def _to_index(i):
    """
    Convert input to something usable as an index.

    Index for character is first code point, ie. "code point" for single
    code point, and first code point of sequence for code point sequence.

    :param i: Input to be converted to an index.
    :return: Value suitable for index use.

    >>> _to_index(0x002D) == 0x002D
    True
    >>> _to_index([0x002D, 0x002E]) == 0x002D
    True
    >>> _to_index((0x002D, 0x002E)) == 0x002D
    True
    """
    if isinstance(i, int):
        index = i
    else:
        index = i[0]

    return index


class Variant(object):
    """
    Represent a variant of a code point.

    A variant is uniquely identified by a combination of its:
        - code point (or code point sequence)
        - when attribute
        - not-when attribute
    """
    # For now, structure is very simple, and is used to only store the variant
    # code point (or sequence). This seems very similar to what a CharBase is,
    # and maybe we should base the Variant class on it?

    def __init__(self, cp_or_sequence,
                 variant_type=None,
                 when=None, not_when=None,
                 comment=None, ref=None):
        self.cp = tuple(cp_or_sequence)
        self.type = variant_type
        self.when = when
        self.not_when = not_when
        self.comment = comment
        self.references = ref if ref is not None else []

    def __unicode__(self):
        return u''.join(unichr(c) for c in self.cp)

    def __repr__(self):
        return "<Variant: %s>" % ' '.join(cp_to_str(c) for c in self.cp)

    def __eq__(self, other):
        return ((self.cp == other.cp) and
                (self.when == other.when) and
                (self.not_when == other.not_when))

    def __hash__(self):
        # TODO: rework this to get an actual hash function
        return (hash(self.cp) +
                hash(self.when) +
                hash(self.not_when))


class CharBase(object):
    """
    Base class for char objects.
    """

    def __init__(self, cp_or_sequence,
                 comment=None, ref=None,
                 tag=None,
                 when=None, not_when=None):
        assert len(cp_or_sequence), "there should be at least one char"
        self.cp = tuple(cp_or_sequence)
        self.comment = comment
        self.references = ref if ref is not None else []
        self.tags = tag if tag is not None else []
        self.when = when
        self.not_when = not_when
        self._variants = {}

    def as_index(self):
        return _to_index(self.cp)

    def add_variant(self, cp_or_sequence,
                    variant_type=None,
                    when=None, not_when=None,
                    comment=None, ref=None):
        """
        Add a variant to a char.

        :param cp_or_sequence: Code point or code point sequence of the variant.
        :param variant_type: Type for the variant, if any.
        :param when: Condition to be satisfied for the variant to exist.
        :param not_when: Condition to must be not satisfied for the variant
                         to exist.
        :param comment: Optional comment for the variant.
        :param ref: List of references associated to the code point.
        :raises VariantAlreadyExists: If variant already exists for character.

        >>> c = CharBase.from_cp_or_sequence([1])
        >>> c.add_variant([10], 'BLOCKED')
        >>> (10, ) in c._variants
        True
        >>> c._variants[(10,)][0].type
        u'BLOCKED'
        """
        assert len(cp_or_sequence), "there should be at least one char"

        var = Variant(cp_or_sequence,
                      variant_type=variant_type,
                      when=when, not_when=not_when,
                      comment=comment, ref=ref)

        idx = tuple(cp_or_sequence)
        if idx in self._variants and var in set(self._variants[idx]):
            logger.error("%r: Variant '%s' already exists",
                         self,
                         format_cp(cp_or_sequence))
            raise VariantAlreadyExists(self.cp, var.cp)
        else:
            self._variants.setdefault(idx, []).append(var)

    def del_variant(self, cp_or_sequence, when=None, not_when=None):
        """
        Delete a variant from a char.

        :param cp_or_sequence: Code point or code point sequence of the variant.
        :param when: Condition to be satisfied for the variant to exist.
        :param not_when: Condition to must be not satisfied for the variant
                         to exist.
        :returns: True if deleted.

        >>> c = CharBase.from_cp_or_sequence([1])
        >>> c.add_variant([10], 'BLOCKED')
        >>> c.del_variant([10])
        True
        >>> len(c._variants) == 0
        True
        """
        assert len(cp_or_sequence), "there should be at least one char"

        var = Variant(cp_or_sequence, when=when, not_when=not_when)

        idx = tuple(cp_or_sequence)
        if idx in self._variants and var in set(self._variants[idx]):
            self._variants[idx].remove(var)
            if len(self._variants[idx]) == 0:
                # Variant was last variant with this code point
                del self._variants[idx]
            return True
        else:
            return False

    def __eq__(self, other):
        return self.cp == other.cp

    def __hash__(self):
        return hash(self.cp)

    def __unicode__(self):
        return u''.join(unichr(c) for c in self.cp)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__,
                             ' '.join(cp_to_str(c) for c in self.cp))

    def __len__(self):
        return len(self.cp)

    def has_variant(self):
        """
        Test if a char has any variants.

        :return: True if char has at least one variant.
        """
        return len(self._variants) > 0

    def is_prefix_of(self, cp_sequence):
        """
        Test if the current char is a prefix of input.

        :param cp_sequence: The input to test.
        :return: True if current char is prefix of cp_sequence, False otherwise.

        >>> CharBase([0x002A]).is_prefix_of([0x002A, 0x002B])
        True
        >>> CharBase([0x002A, 0x002B]).is_prefix_of([0x002A, 0x002B])
        True
        >>> CharBase([0x002A, 0x002B]).is_prefix_of([0x002A])
        False
        """
        # cp_sequence must be at least the same length as cp
        return len(cp_sequence) >= len(self.cp) \
            and list(self.cp) == list(cp_sequence[:len(self)])

    def get_variants(self):
        """
        Return a generator to iterate through the variants of a char.

        :returns: Generator of Variant objects of a char.
        """

        for variant_cp in sorted(self._variants):
            variants = self._variants[variant_cp]
            for var in variants:
                yield var

    def get_variant(self, var_cp):
        """
        Return a the variant marching the code point.

        :returns: The required variant
        """
        return self._variants.get(var_cp, None)

    def get_reflexive_variants(self):
        """
        Return the list of reflexive variants.

        :return: List of reflexive variants of the character.
        """
        return self._variants.get(self.cp, [])

    @staticmethod
    def from_cp_or_sequence(cp_or_sequence, *args, **kwargs):
        """
        Static method to construct the proper CharBase-derived object from a
        code point or a code point sequence.

        >>> isinstance(CharBase.from_cp_or_sequence(1), Char)
        True
        >>> isinstance(CharBase.from_cp_or_sequence([1]), Char)
        True
        >>> isinstance(CharBase.from_cp_or_sequence([1,2]), CharSequence)
        True
        """
        cls = Char
        cp_value = cp_or_sequence
        if not isinstance(cp_or_sequence, int):
            if len(cp_or_sequence) > 1:
                cls = CharSequence
            else:
                cp_value = cp_or_sequence[0]

        char = cls(cp_value, *args, **kwargs)
        return char


class Char(CharBase):
    """
    A single char object.

    Represent a <char cp="XXXX"> element in the XML file.
    """

    def __init__(self, cp, *args, **kwargs):
        # Convert single code point to tuple
        super(Char, self).__init__((cp,), *args, **kwargs)


class RangeChar(Char):
    """
    A specific char from a range.

    Represent a code point in a <range first-cp="XXXX" last-cp="YYYY"/>
    in the XML file.

    This object acts exactly like a Char, and is used to store the range the
    character belongs to.
    """

    def __init__(self, cp, first_cp, last_cp, *args, **kwargs):
        # Convert single code point to tuple
        super(RangeChar, self).__init__(cp, *args, **kwargs)
        self.first_cp = first_cp
        self.last_cp = last_cp

    def add_variant(self, *args, **kwargs):
        # From RFC7940, section 5. Code Points and Variants
        # A "range" element has no child elements.
        logger.error("%r: Range has no variant", self)
        raise LGRFormatException(LGRFormatException.
                                 LGRFormatReason.RANGE_NO_CHILD)

    def del_variant(self, *args, **kwargs):
        # From RFC7940, section 5. Code Points and Variants
        # A "range" element has no child elements.
        logger.error("%r: Range has no variant", self)
        raise LGRFormatException(LGRFormatException.
                                 LGRFormatReason.RANGE_NO_CHILD)

    def __repr__(self):
        return '<RangeChar: %s (%s - %s)>' % (' '.join(cp_to_str(c) for c in
                                                       self.cp),
                                              cp_to_str(self.first_cp),
                                              cp_to_str(self.last_cp))


class CharSequence(CharBase):
    """
    A char sequence object.

    Represent a <char cp="XXXX YYYY..."> element in the XML file.
    """
    pass


class Repertoire(object):
    """
    A structure used to store various code points types.
    """

    def __init__(self):
        # List of (first-cp, last-cp) tuples for ranges.
        # This list MUST be kept in order!
        # Should this really be here?
        self.ranges = []
        # Code point objects are indexed by their first code point, as an int.
        # So the key for a <char cp="1234"/> object is 1234,
        # and the key for a  <char cp="1234 5678"/> also is 1234.
        # The value stored is a list of CharBase objects.
        self._chardict = dict()

    # Note for the following methods:
    # People may want to easily access the repertoire without having to wonder
    # about the internal format used.
    # So handle multiple input:
    # * CharBase objects:
    # >>> c = Char(123)
    # >>> c in cd
    # * Single code point:
    # >>> 0x0020 in cd
    # * list/tuple, used for code point sequences:
    # >>> [1,2,3] in cd

    def __contains__(self, k):
        """
        >>> cd = Repertoire()
        >>> _ = cd.add_char([0x002A, 0x002B])
        >>> _ = cd.add_char([0x002A])
        >>> 0x002A in cd
        True
        >>> [0x002A] in cd
        True
        >>> [0x002A, 0x002B] in cd
        True
        >>> Char(0x002A) in cd
        True
        """
        if isinstance(k, CharBase):
            cp = k.cp
            k = k.as_index()
        elif isinstance(k, int):
            cp = (k, )
            k = _to_index(k)
        else:
            cp = tuple(k)
            k = _to_index(k)
        if k not in self._chardict:
            return False
        return cp in [c.cp for c in set(self._chardict[k])]

    def __getitem__(self, k):
        """
        >>> cd = Repertoire()
        >>> seq = cd.add_char([0x002A, 0x002B])
        >>> char = cd.add_char([0x002A])
        >>> seq == cd[0x002A, 0x002B]
        True
        >>> char == cd[0x002A]
        True
        """
        if isinstance(k, CharBase):
            k = k.cp
        elif isinstance(k, int):
            k = (k,)
        return self.get_char(k)

    def __iter__(self):
        """
        Iterate through the list of defined code points.

        Sort code points by increasing code point value.
        Only return the first element of a range, since all information is
        available from it.

        >>> cd = Repertoire()
        >>> seq = cd.add_char([0x002A, 0x002B])
        >>> char = cd.add_char([0x002A])
        >>> [char, seq] == list(cd)
        True
        """
        last_cp = None
        for index in sorted(self._chardict.keys()):
            char_list = self._chardict[index]

            # Reset last_cp once we have exhausted the range
            if last_cp < index:
                last_cp = None

            for char in sorted(char_list, key=lambda c: len(c.cp)):

                if isinstance(char, RangeChar):
                    if last_cp is not None:
                        # Skip all RangeChar of a range
                        continue
                    else:
                        last_cp = char.last_cp

                yield char

    def all_repertoire(self, include_sequences=True, include_ranges=True):
        """
        Return the whole content of the repertoire, unsorted.

        :param include_sequences: If False CharSequence are excluded from output.
        :param include_ranges: If False RangeChar are excluded from output.
        :return: A generator that contains all Char elements of the repertoire.

        >>> cd = Repertoire()
        >>> char1 = cd.add_char([0x002B])
        >>> char2 = cd.add_char([0x002A])
        >>> seq = cd.add_char([0x002A, 0x002B])
        >>> {char1, char2, seq} == set(cd.all_repertoire())
        True
        """
        for char_list in self._chardict.values():
            for char in char_list:
                if isinstance(char, CharSequence) and not include_sequences:
                    continue
                if isinstance(char, RangeChar) and not include_ranges:
                    continue
                yield char

    def __len__(self):
        """
        Return the number of elements in the repertoire.

        >>> cd = Repertoire()
        >>> len(cd)
        0
        >>> _ = cd.add_char([0x002A])
        >>> len(cd)
        1
        >>> _ = cd.add_char([0x002B])
        >>> len(cd)
        2
        >>> _ = cd.add_char([0x002A, 0x002B])
        >>> len(cd)
        3
        """
        return sum(len(c) for c in self._chardict.values())

    def add_char(self, cp_or_sequence,
                 comment=None, ref=None,
                 tag=None,
                 when=None, not_when=None):
        """
        Add a character to the LGR.

        :param cp_or_sequence: Code point or sequence to add to the LGR.
        :param comment: Comment associated to the code point.
        :param ref: List of references associated to the code point.
        :param tag: List of tags associated to the code point.
        :param when: Condition to be satisfied by the code point.
        :param not_when: Condition to not be satisfied by the codepoint.
        :returns: Corresponding Char object created.
        :raises CharAlreadyExists: If input already exists in dictionary.

        >>> cd = Repertoire()
        >>> c = cd.add_char([0x002A])
        >>> c in cd
        True
        >>> cd[0x002A] is c
        True
        >>> cd.add_char([0x002A]) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        CharAlreadyExists
        """
        # Entries are keyed to the first code point of the `cp_or_sequence`
        # with values appended to a list.
        # For a single code point, a Char instance is created
        # For a sequence of code points, a CharSequence instance is created
        assert len(cp_or_sequence), "there should be at least one char"

        char = CharBase.from_cp_or_sequence(cp_or_sequence,
                                            comment, ref, tag,
                                            when, not_when)
        self._add_char(char)
        return char

    def del_char(self, cp_or_sequence):
        """
        Delete a character from the LGR.

        :param cp_or_sequence: code point or code point sequence to delete.
        :raises NotInLGR: If the code point does not exist.

        >>> cd = Repertoire()
        >>> _ = cd.add_char([0x002A])
        >>> 0x002A in cd
        True
        >>> cd.del_char([0x002A])
        >>> 0x002A in cd
        False
        >>> cd.del_char([0x002B]) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        NotInLGR
        """
        assert len(cp_or_sequence), "there should be at least one char"

        char = CharBase.from_cp_or_sequence(cp_or_sequence)
        if not self._del_char(char):
            logger.error("Code point '%s' does not exist",
                         format_cp(cp_or_sequence))
            raise NotInLGR(cp_or_sequence)

    def add_range(self, first_cp, last_cp,
                  comment=None, ref=None,
                  tag=None,
                  when=None, not_when=None,
                  skip_check=False):
        """
        Add a range of characters to the LGR.

        :param first_cp: First code point of the range.
        :param last_cp: Last code point of the range.
        :param comment: Comment associated to the range.
        :param ref: List of references associated to the range.
        :param tag: List of tags associated to the range.
        :param when: Condition to be satisfied by the code point.
        :param not_when: Condition to not be satisfied by the codepoint.
        :param skip_check: If True, skips checking for overlapping ranges.
                           Invalid use of this parameter may leave
                           the dictionary in an inconsistent state!
        :raises RangeAlreadyExists: If input already exists in dictionary.

        >>> cd = Repertoire()
        >>> cd.add_range(0x002A, 0x0030)
        >>> 0x02A in cd
        True
        >>> c = cd[0x002A]
        >>> isinstance(c, RangeChar)
        True
        >>> c.first_cp == 0x002A and c.last_cp == 0x0030
        True
        >>> cd.add_range(0x002A, 0x0030) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        RangeAlreadyExists
        """
        assert first_cp < last_cp, "range must be defined in order"

        if not skip_check and self._check_range_overlap(first_cp, last_cp):
            logger.error("Range '%s - %s' already exists",
                         format_cp(first_cp), format_cp(last_cp))
            raise RangeAlreadyExists(first_cp, last_cp)

        for cp in range(first_cp, last_cp + 1):
            char = RangeChar(cp, first_cp, last_cp,
                             comment=comment, ref=ref, tag=tag,
                             when=when, not_when=not_when)
            # TODO: clean-up range on error.
            self._add_char(char)

        # Insert by first cp
        self.ranges.append((first_cp, last_cp))

    def del_range(self, first_cp, last_cp):
        """
        Delete a range of characters from the LGR.

        Note: This MUST be the exact same range that was added,
        meaning you cannot delete partial sub-ranges!

        :param first_cp: First code point of the range.
        :param last_cp: Last code point of the range.
        :raises NotInLGR: If the range does not exist.

        >>> cd = Repertoire()
        >>> cd.add_range(0x002A, 0x0030)
        >>> cd.del_range(0x002A, 0x0030)
        >>> 0x002A in cd
        False
        >>> cd.del_range(0x002A, 0x0030) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        NotInLGR
        """
        assert first_cp < last_cp, "range must be defined in order"

        if (first_cp, last_cp) not in self.ranges:
            logger.error("Range '%s - %s' does not exist",
                         format_cp(first_cp), format_cp(last_cp))
            raise NotInLGR(first_cp)

        for cp in range(first_cp, last_cp + 1):
            char = RangeChar(cp, first_cp, last_cp)
            if not self._del_char(char):
                # TODO: clean-up range on error
                # This should only happen if range insertion failed
                # -> inconsistent state for now
                logger.critical("Range '%s - %s' is missing code point %s",
                                format_cp(first_cp), format_cp(last_cp),
                                format_cp(cp))
                raise NotInLGR(cp)

        # Remove and sort by first cp
        self.ranges.remove((first_cp, last_cp))

    def get_char(self, cp_or_sequence):
        """
        Get the char object of a code point.

        :param cp_or_sequence: Code point or sequence of the character
                              to get.
        :raises NotInLGR: If the code point does not exist.

        >>> cd = Repertoire()
        >>> char = cd.add_char([0x002A])
        >>> c = cd.get_char([0x002A])
        >>> c is char
        True
        """
        assert len(cp_or_sequence), "there should be at least one char"

        origin = CharBase.from_cp_or_sequence(cp_or_sequence)

        idx = origin.as_index()
        if idx not in self._chardict:
            raise NotInLGR(cp_or_sequence)

        chars = self._chardict[idx]
        try:
            list_idx = chars.index(origin)
        except ValueError:
            logger.error("Code point '%s' does not exist",
                         format_cp(cp_or_sequence))
            raise NotInLGR(cp_or_sequence)

        char = chars[list_idx]
        return char

    def add_variant(self, cp_or_sequence,
                    variant_cp_or_sequence, variant_type=None,
                    when=None, not_when=None,
                    comment=None, ref=None):
        """
        Add a variant to a code point.

        :param cp_or_sequence: Code point or code point sequence of the character
                               to add the variant to.
        :param variant_cp_or_sequence: The code point or code point sequence
                                       of the variant.
        :param variant_type: The type for the variant, if any.
        :param when: Condition to be satisfied for the variant to exist.
        :param not_when: Condition to must be not satisfied for the variant
                         to exist.
        :param comment: Optional comment.
        :param ref: List of references associated to the code point.
        :raises NotInLGR: If the code point does not exist.

        >>> cd = Repertoire()
        >>> _ = cd.add_char([0x002A])
        >>> cd.add_variant([0x002A], [0x003A], 'BLOCK')
        >>> len(cd[0x002A]._variants) == 1
        True
        >>> cd[0x002A]._variants[(0x003A,)][0].type == 'BLOCK'
        True
        """
        char = self.get_char(cp_or_sequence)
        char.add_variant(variant_cp_or_sequence,
                         variant_type=variant_type,
                         when=when, not_when=not_when,
                         comment=comment,
                         ref=ref)

    def del_variant(self, cp_or_sequence,
                    variant_cp_or_sequence,
                    when=None, not_when=None):
        """
        Delete a variant from a character.

        :param cp_or_sequence: Code point or code point sequence of the character
                               to remove the variant from.
        :param variant_cp_or_sequence: The code point or code point sequence
                                       of the variant.
        :param when: Condition to be satisfied for the variant to exist.
        :param not_when: Condition to must be not satisfied for the variant
                         to exist.
        :returns: True if deleted.
        :raises NotInRepertoire: If the code point does not exist.

        >>> cd = Repertoire()
        >>> _ = cd.add_char([0x002A])
        >>> cd.add_variant([0x002A], [0x003A], 'BLOCK')
        >>> cd.del_variant([0x002A], [0x003A])
        True
        >>> len(cd[0x002A]._variants) == 0
        True
        """
        char = self.get_char(cp_or_sequence)
        return char.del_variant(variant_cp_or_sequence, when, not_when)

    def get_variants(self, cp_or_sequence):
        """
        Get the variants of a code point.

        :param cp_or_sequence: Code point or code point sequence of the character
                               to list the variant of.
        :returns: Generator of Variants objects of a char.
        :raises NotInRepertoire: If the code point does not exist.

        >>> cd = Repertoire()
        >>> _ = cd.add_char([0x002A])
        >>> cd.add_variant([0x002A], [0x003A], 'BLOCK')
        >>> list(cd.get_variants([0x002A])) == [Variant((0x003A,), 'BLOCK')]
        True
        """
        char = self.get_char(cp_or_sequence)
        return char.get_variants()

    def get_variant(self, cp_or_sequence, var_cp):
        """
        Get a specific variant of a code point.

        :param cp_or_sequence: Code point or code point sequence of the character
                               to list the variant of.
        :param var_cp: Variant code point to retrieve
        :returns: Generator of Variants objects of a char.
        :raises NotInRepertoire: If the code point does not exist.

        >>> cd = Repertoire()
        >>> _ = cd.add_char([0x002A])
        >>> cd.add_variant([0x002A], [0x003A], 'BLOCK')
        >>> cd.get_variant([0x002A], (0x003A, )) == [Variant((0x003A,), 'BLOCK')]
        True
        """
        char = self.get_char(cp_or_sequence)
        return char.get_variant(var_cp)

    def get_variant_sets(self):
        """
        Return the list of variants set contained in the repertoire.

        This function assumes the repertoire is symmetric and transitive.

        Note: This function is very stupid and NOT optimised in complexity
        nor memory consumption.

        :returns: List of variant set, with a variant set being
                  a list of code points included in the set.
        """
        def dfs(char, visited=None):
            """ Utility function to iterate in a char/variants (Depth-First Search)."""
            if visited is None:
                visited = set()
            visited.add(char.cp)
            for variant in char.get_variants():
                if variant.cp in visited:
                    continue
                try:
                    reverse_char = self.get_char(variant.cp)
                except NotInLGR:
                    # Ignore invalid LGR
                    continue
                dfs(reverse_char, visited)
            return visited

        variant_sets = set()
        for index in sorted(self._chardict.keys()):
            for char in self._chardict[index]:
                # XXX: Convert to tuple here so it is hashable
                variant_set = tuple(sorted(dfs(char)))
                if len(variant_set) > 1:
                    lowest = min(variant_set)
                    variant_sets.add((lowest, variant_set))

        return [variants for _, variants in sorted(variant_sets)]

    def del_reference(self, ref_id):
        """
        Iterate through the repertoire to remove the reference ref_id
        rom the list of code point/variant references.

        :param ref_id: The reference to remove.
        """
        for cp_list in self._chardict.itervalues():
            for char in cp_list:
                if ref_id in char.references:
                    char.references.remove(ref_id)
                for variant in char.get_variants():
                    if ref_id in variant.references:
                        variant.references.remove(ref_id)

    def get_chars_from_prefix(self, cp, only_variants=False):
        """
        Return the list of characters starting with cp.

        :param cp: The first codepoint of the characters.
        :return: List of characters, ordered by decreasing length.
        :param only_variants: Only return chars with variants.
        :raises NotInLGR: If the code point does not exist.
        """
        if cp not in self._chardict:
            raise NotInLGR(cp)
        if not only_variants:
            iterable = self._chardict[cp]
        else:
            iterable = [v for v in self._chardict[cp] if v.has_variant()]
        return sorted(iterable, key=lambda x: len(x), reverse=True)

    def _check_range_overlap(self, first_cp, last_cp):
        """
        Check that a range is not already inserted in this repertoire.

        >>> cd = Repertoire()
        >>> cd.ranges = [(5, 10), (20, 30)]
        >>> cd._check_range_overlap(1, 2)
        False
        >>> cd._check_range_overlap(1, 5)
        True
        """
        # Sort self.ranges by first_cp
        self.ranges.sort()
        for (range_first, range_last) in self.ranges:
            if first_cp > range_last or last_cp < range_first:
                continue
            # From now on:
            #    * first_cp <= range_last
            #    * last_cp >= range_first
            if first_cp >= range_first or last_cp <= range_last:
                return True
        return False

    def _add_char(self, char):
        """
        Generic function to add a char into the dictionary.

        :param char: Char object (a subclass of CharBase).
        :raises CharAlreadyExists: If char is already in dictionary.

        >>> cd = Repertoire()
        >>> cd._add_char(Char(0x002A))
        >>> 0x002A in cd
        True
        >>> cd._add_char(CharSequence(tuple([0x002A, 0x002B])))
        >>> [0x002A, 0x002B] in cd
        True
        >>> cd._add_char(Char(0x002A)) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        CharAlreadyExists
        """
        idx = char.as_index()
        if idx in self._chardict and char in set(self._chardict[idx]):
            logger.error("Char '%s' already exists", char)
            raise CharAlreadyExists(char.cp)
        else:
            self._chardict.setdefault(idx, []).append(char)

    def _del_char(self, char):
        """
        Generic function to delete a character from the dictionary.

        :param char: Char object (a subclass of CharBase).
        :returns: True if character was present, False otherwise.
        :raises KeyError: If char is not in dictionary.

        >>> cd = Repertoire()
        >>> cd._add_char(Char(0x002A))
        >>> cd._del_char(Char(0x002A))
        True
        >>> 0x002A in cd
        False
        >>> cd._del_char(Char(0x002B))
        False
        """
        idx = char.as_index()
        if idx in self._chardict and char in set(self._chardict[idx]):
            self._chardict[idx].remove(char)
            if len(self._chardict[idx]) == 0:
                # CP was only one (no sequence starting with this CP)
                del self._chardict[idx]
            return True
        else:
            return False


if __name__ == "__main__":
    import doctest

    logger.addHandler(logging.NullHandler())
    doctest.testmod()
