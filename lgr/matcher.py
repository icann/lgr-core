# -*- coding: utf-8 -*-
"""
matcher.py - Definition of matcher structures.
"""
from __future__ import unicode_literals

import logging

from lgr.exceptions import LGRFormatException
from lgr.utils import format_cp_collapsed
from lgr.core import PROTOCOL_LABEL_MAX_LENGTH

logger = logging.getLogger(__name__)


class Matcher(object):
    """
    Abstract parent class of Matcher objects.
    """

    def __init__(self, comment=None):
        """
        Create a base matcher.

        :param comment: Optional comment
        """
        self.comment = comment

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False):
        """
        Resolve a matcher operator to a regex pattern.

        :param rules_lookup: Dictionary of defined rules in the LGR to use
                             for by-ref rules.
        :param classes_lookup: Dictionary of defined classes in the LGR to use
                             for by-ref classes.
        :param unicode_database: The Unicode Database.
        :param is_look_behind: True if matcher is used in a look-behind element.
        :return: String to be compiled to a regex.
        """
        raise NotImplementedError()

    def validate(self, parents, rules_lookup, classes_lookup):
        """
        Ensure a matcher has a valid definition.

        :param parents: List of parent objects of this instance.
        :param rules_lookup: Dictionary of defined rules in the LGR. Not used.
        :param classes_lookup: Dictionary of defined classes in the LGR to use
                               for by-ref classes.
        """
        logger.debug('Validate %s', self)

    def iter_children(self):
        """
        Returns an iterator of any child element of this matcher, which could be none.
        """
        return iter([])

    def __repr__(self):
        return '<Matcher>'


class CompoundMatcher(Matcher):
    """
    Base class for matcher with children
    """

    MAX_CHILDREN = None

    def __init__(self, comment=None):
        super(CompoundMatcher, self).__init__(comment)
        self._children = []

    def add_child(self, child):
        if self.MAX_CHILDREN is not None and len(self._children) >= self.MAX_CHILDREN:
            logger.error("Cannot have more than %s children", self.MAX_CHILDREN)
            raise LGRFormatException(LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        self._children.append(child)

    def validate(self, parents, rules_lookup, classes_lookup):
        super(CompoundMatcher, self).validate(parents,
                                              rules_lookup, classes_lookup)
        for child in self._children:
            child.validate(parents + [self], rules_lookup, classes_lookup)

    def iter_children(self):
        """
        Returns an iterator of any child element of this matcher, which could be none.
        """
        return iter(self._children)

    def can_add_child(self):
        """
        Returns true of this element accept more children.
        """
        return self.MAX_CHILDREN and len(self._children) < self.MAX_CHILDREN


class StartMatcher(Matcher):
    """
    Represent the start of the label.

    Defined in
    5.3.8.  The start and end Elements
    """

    MAX_CHILDREN = 0

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False):
        return '^'

    def __str__(self):
        return '(start)'

    def __repr__(self):
        return '<StartMatcher>'


class EndMatcher(Matcher):
    """
    Represent the end of the label.

    Defined in
    5.3.8.  The start and end Elements
    """

    MAX_CHILDREN = 0

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False):
        return '$'

    def __str__(self):
        return '(end)'

    def __repr__(self):
        return '<EndMatcher>'


class AnchorMatcher(Matcher):
    """
    Represent the current code point in the label being evaluated.

    Defined in
    5.4.1.  The anchor Element
    """

    MAX_CHILDREN = 0

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False):
        # Note: anchor must be of the following format:
        # (\x{AAAA})+

        # TODO: Cannot use new-style string formatting here
        # because \x{AAAA} is used for CharMatcher
        return '%(anchor)s'

    def __str__(self):
        return '⚓'

    def __repr__(self):
        return '<AnchorMatcher>'


class LookAroundMatcher(CompoundMatcher):
    """
    Base class for look-around matchers.

    Defined in
    5.4.2.  The look-behind and look-ahead Elements
    """
    pass


class LookAheadMatcher(LookAroundMatcher):
    """
    Test if label at current input matches the defined expression
    without consuming input.

    Defined in
    5.4.2.  The look-behind and look-ahead Elements
    """
    def validate(self, parents, rules_lookup, classes_lookup):
        super(LookAheadMatcher, self).validate(parents,
                                               rules_lookup, classes_lookup)
        # TODO: Implement complete validation

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False):
        sub_regex = ''.join([m.get_pattern(rules_lookup,
                                           classes_lookup,
                                           unicode_database)
                             for m in self._children])
        return '(?=%s)' % sub_regex

    def __str__(self):
        return '→({})'.format(''.join('{}'.format(m) for m in self._children))

    def __repr__(self):
        return '<LookAheadMatcher>'


class LookBehindMatcher(LookAroundMatcher):
    """
    Test if label preceding current input matches the defined expression
    without consuming input.

    Defined in
    5.4.2.  The look-behind and look-ahead Elements
    """
    def validate(self, parents, rules_lookup, classes_lookup):
        super(LookBehindMatcher, self).validate(parents,
                                                rules_lookup, classes_lookup)
        # TODO: Implement complete validation

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False):
        sub_regex = ''.join([m.get_pattern(rules_lookup,
                                           classes_lookup,
                                           unicode_database,
                                           True)
                             for m in self._children])
        return '(?<=%s)' % sub_regex

    def __str__(self):
        return '({})←'.format(''.join('{}'.format(m) for m in self._children))

    def __repr__(self):
        return '<LookBehindMatcher>'


class CountMatcher(Matcher):
    """
    Implement the count attribute.

    Defined in
    5.3.3.  The count Attribute
    """
    def __init__(self, comment=None, count=None):
        super(CountMatcher, self).__init__(comment)
        self.count = count

    def get_pattern(self, rules_lookup=None, classes_lookup=None,
                    unicode_database=None,
                    is_look_behind=False):
        if not self.count:
            return ''

        if ':' in self.count:
            min, max = self.count.split(':')
            return '{%s,%s}' % (min, max)
        elif self.count.endswith('+'):
            if is_look_behind:
# Note: Most regex libraries only support fixed-length look-behind : (:?<=a{42}).
# For those which support variable-length look-behind (like ICU),
# it's possible that they do not support "infinite look-behind",
# ie. look-behind that contains '+' or '*': (:?<=a+).
# There is one trick we can apply here: since we are validating protocol labels
# according to RFC1035 we can limit the length of the matched input to the
# maximal label length
                return '{%s,%s}' % (self.count[:-1], PROTOCOL_LABEL_MAX_LENGTH)
            else:
                return '{%s,}' % self.count[:-1]

        return '{%s}' % self.count


class ChoiceMatcher(CountMatcher, CompoundMatcher):
    """
    Represent a list of alternative matchers.

    Defined in
    5.3.5.  The choice Element
    """
    def __init__(self, comment=None, count=None):
        super(ChoiceMatcher, self).__init__(comment, count)

    def validate(self, parents, rules_lookup, classes_lookup):
        CompoundMatcher.validate(self, parents, rules_lookup, classes_lookup)

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False):
        count = CountMatcher.get_pattern(self, is_look_behind=is_look_behind)
        choice = '(?:' + \
                 '(?:' + \
                 ')|(?:'.join([m.get_pattern(rules_lookup,
                                             classes_lookup,
                                             unicode_database,
                                             is_look_behind)
                               for m in self._children]) + \
                 ')' + \
                 ')'
        if len(count) > 0:
            return '%s%s' % (choice, count)
        else:
            return choice

    def __str__(self):
        count = CountMatcher.get_pattern(self)
        return '({}){}'.format('|'.join('{}'.format(m) for m in self._children), count)

    def __repr__(self):
        count = super(ChoiceMatcher, self).get_pattern()
        return '<ChoiceMatcher %s>' % count


class AnyMatcher(CountMatcher):
    """
    Match of any code point.

    Defined in
    5.3.7.  The any Element
    """

    MAX_CHILDREN = 0

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False):
        count = super(AnyMatcher, self).get_pattern(is_look_behind=is_look_behind)
        return '.%s' % count

    def __str__(self):
        count = CountMatcher.get_pattern(self)
        return '(any){}'.format(count)

    def __repr__(self):
        count = super(AnyMatcher, self).get_pattern()
        return '<AnyMatcher: %s>' % count


class CharMatcher(CountMatcher):
    """
    Match of literal code point and sequences.

    Defined in
    5.3.6.  Literal Code Point Sequences
    """

    MAX_CHILDREN = 0

    def __init__(self, cp_or_sequence, comment=None, count=None, ref=None):
        """
        Create a character matcher.

        :param cp_or_sequence: Codepoint or sequence to match, as a list.
        :param comment: Optional Comment associated to the code point.
        :param count: Optional count number.
        :param ref: List of references associated to the code point.
        """
        super(CharMatcher, self).__init__(comment, count)
        self.cp_or_sequence = cp_or_sequence
        self.comment = comment
        self.references = ref

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False):
        count = super(CharMatcher, self).get_pattern(is_look_behind=is_look_behind)
        regex = ''.join('\\x{%X}' % x for x in self.cp_or_sequence)

        if len(count) > 0:
            return '(%s)%s' % (regex, count)
        else:
            return regex

    def __str__(self):
        count = CountMatcher.get_pattern(self)
        if len(count) > 1:
            return '({}){}'.format(format_cp_collapsed(self.cp_or_sequence), count)

        return format_cp_collapsed(self.cp_or_sequence)

    def __repr__(self):
        count = super(CharMatcher, self).get_pattern()
        return '<CharMatcher: %s%s>' % (self.cp_or_sequence, count)


class RuleMatcher(CountMatcher):
    """
    Match of a rule (anonymous or by-ref).
    """
    def __init__(self, rule, comment=None, count=None):
        """
        Create a rule matcher.

        :param rule: The rule object of the matcher.
        :param comment: Optional comment.
        :param count: Optional count number.
        """
        super(RuleMatcher, self).__init__(comment, count)
        self._rule = rule

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False):
        count = super(RuleMatcher, self).get_pattern(is_look_behind=is_look_behind)
        regex = self._rule.get_pattern(rules_lookup, classes_lookup,
                                       unicode_database, is_look_behind)
        if len(count) > 0:
            return '(%s)%s' % (regex, count)
        else:
            return regex

    def validate(self, parents, rules_lookup, classes_lookup):
        super(RuleMatcher, self).validate(parents,
                                          rules_lookup, classes_lookup)
        self._rule.validate(parents + [self], rules_lookup, classes_lookup)

    def __str__(self):
        count = CountMatcher.get_pattern(self)
        if len(count) > 1:
            return '({}){}'.format(self._rule, count)

        return '{}'.format(self._rule)

    def __repr__(self):
        count = super(RuleMatcher, self).get_pattern()
        return '<RuleMatcher: %s%s>' % (self._rule, count)

    def iter_children(self):
        """
        Returns an iterator of any child element of this matcher, which could be none.
        """
        return self._rule.iter_children()

    def can_add_child(self):
        return self._rule.can_add_child()

    @property
    def by_ref(self):
        return self._rule.by_ref


class ClassMatcher(CountMatcher):
    """
    Match of a class (anonymous or by-ref).
    """
    def __init__(self, cls, comment=None, count=None):
        """
        Create a class matcher.

        :param cls: The class object of the matcher.
        :param comment: Optional comment.
        :param count: Optional count number.
        """
        super(ClassMatcher, self).__init__(comment, count)
        self._cls = cls

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False):
        count = super(ClassMatcher, self).get_pattern(is_look_behind=is_look_behind)
        regex = self._cls.get_pattern(rules_lookup, classes_lookup,
                                      unicode_database, is_look_behind)
        if len(count) > 0:
            return '(%s)%s' % (regex, count)
        else:
            return regex

    def validate(self, parents, rules_lookup, classes_lookup):
        super(ClassMatcher, self).validate(parents,
                                           rules_lookup, classes_lookup)
        self._cls.validate(parents + [self], rules_lookup, classes_lookup)

    def __str__(self):
        count = CountMatcher.get_pattern(self)
        if len(count) > 1:
            return '({}){}'.format(self._cls, count)

        return '{}'.format(self._cls)

    def __repr__(self):
        count = super(ClassMatcher, self).get_pattern()
        return '<ClassMatcher: %s%s>' % (self._cls, count)
