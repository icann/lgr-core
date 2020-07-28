# -*- coding: utf-8 -*-
"""
rule.py - Definition of rule structures.
"""
from __future__ import unicode_literals

import re
import logging

from picu.exceptions import PICUException

from lgr.utils import format_cp, cp_to_ulabel
from lgr.exceptions import LGRFormatException, RuleError

logger = logging.getLogger(__name__)
rule_logger = logging.getLogger('lgr-rule-logger')


class Rule(object):
    """
    A rule object.

    Defined in
    5.3.1.  The rule Element
    """
    def __init__(self, name=None, comment=None, ref=None, by_ref=None):
        """
        Create a new rule.

        :param name: Name of the rule.
        :param comment: Optional comment.
        :param ref: Optional list of references.
        :param by_ref: Name of the referenced rule.
        :raises LGRFormatException: If the rule has conflictual parameters.
        """
        self.name = name
        self.comment = comment
        self.references = ref or []
        self.by_ref = by_ref
        self.children = []

        if name is not None and by_ref is not None:
            logger.error("Cannot create a rule with both a 'name' and a 'by-ref'")
            raise LGRFormatException(LGRFormatException.LGRFormatReason.BY_REF_AND_OTHER)

    def iter_children(self):
        """
        Returns an iterator of any child element of this matcher, which could be none.
        """
        return iter(self.children)

    def can_add_child(self):
        # we don't (and in fact can't) validate the logic of the rule
        return True

    def add_child(self, child):
        if self.by_ref is not None:
            logger.error("Cannot add child to a 'by-ref' rule")
            raise LGRFormatException(LGRFormatException.LGRFormatReason.BY_REF_AND_OTHER)
        self.children.append(child)

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False):
        """
        Resolve a rule to a regex pattern.

        :param rules_lookup: Dictionary of defined rules in the LGR to use
                             for by-ref rules.
        :param classes_lookup: Dictionary of defined classes in the LGR to use
                             for by-ref classes.
        :param unicode_database: The Unicode Database.
        :param is_look_behind: True if rule is used in a look-behind element.
        :return: String to be compiled to a regex.
        """
        if self.by_ref is not None:
            if self.by_ref not in rules_lookup:
                logger.error("Rule cannot reference inexisting rule '%s'",
                             self.by_ref)
                raise RuleError(self,
                                "%s cannot reference inexisting"
                                " rule '%s'" % (self, self.by_ref))

            return rules_lookup[self.by_ref].get_pattern(rules_lookup,
                                                         classes_lookup,
                                                         unicode_database,
                                                         is_look_behind)

        return ''.join([m.get_pattern(rules_lookup,
                                      classes_lookup,
                                      unicode_database,
                                      is_look_behind) for m in self.children])

    def matches(self, label,
                rules_lookup,
                classes_lookup,
                unicode_database,
                anchor=None,
                index=0):
        """
        Test if a rule matches a label.

        :param label: Label to test, as a sequence of code points.
        :param rules_lookup: Dictionary of defined rules in the LGR to use
                             for by-ref rules.
        :param classes_lookup: Dictionary of defined classes in the LGR to use
                               for by-ref classes.
        :param unicode_database: The Unicode Database.
        :param anchor: Optional anchor to use for look-around rules.
        :param index: If anchor is used, its index (0-based).
        :return: True if label is matched by the rule, False otherwise.
        """
        rule_logger.debug("Test match on %s for label '%s' with anchor '%s' (%d)",
                          self,
                          format_cp(label),
                          format_cp(anchor) if anchor else anchor,
                          index)
        try:
            pattern = self.get_pattern(rules_lookup,
                                       classes_lookup,
                                       unicode_database)
        except (re.error, PICUException) as re_exc:
            rule_logger.error('Cannot get pattern for rule %s: %s',
                              self, re_exc)
            raise RuleError(self.name, re_exc)

        if len(pattern) == 0:
            # Pattern is empty, nothing will match
            rule_logger.debug('Empty pattern')
            return False

        if anchor is not None:
            if '%(anchor)s' not in pattern:
                rule_logger.debug('Not a parameterized context rule')
                # Pattern is not a parameterized context-rule, so set index to 0
                index = 0
                anchor = None
            else:
                # Format anchor - Can be a sequence.
                # Use old-style formatting, see note in matcher.AnchorMatcher
                pattern = pattern % {'anchor': ''.join(map(lambda c: '\\x{{{:X}}}'.format(c),
                                                           anchor))}
        rule_logger.debug("Pattern for rule %s: '%s'", self, pattern)
        try:
            regex = unicode_database.compile_regex(pattern)
        except (re.error, PICUException) as re_exc:
            rule_logger.error('Cannot compile regex: %s', re_exc)
            raise RuleError(self.name, re_exc)

        rule_logger.debug("Index: %d", index)

        # Convert label to U-format to be used in regex
        label_u = cp_to_ulabel(label)

        # Look for match. It is important to use "search" and not "match"
        # here, since a rule may not match at the beginning of a label.
        result = regex.search(label_u, index=index)
        rule_logger.debug("Result of match: %s", result)
        if result is None:
            return False

        if anchor is not None:
            match_index = result.start()
            rule_logger.debug('Match index: %d - Index: %d', match_index, index)
            if match_index > index:
                rule_logger.debug('Match found after index, invalid')
                return False
        return True

    def validate(self, parents, rules_lookup, classes_lookup):
        """
        Ensure a rule has a valid definition.

        :param parents: List of parent objects of this instance.
        :param rules_lookup: Dictionary of defined rules in the LGR. Not used.
        :param classes_lookup: Dictionary of defined classes in the LGR to use
                               for by-ref classes.
        """
        logger.debug('Validate %s', self)
        if self.by_ref is not None:
            if self.by_ref not in rules_lookup:
                # From RFC7940, section 6.3.4. The "name" and "by-ref" Attributes
                # It is an error to reference a rule or class for which
                # the definition has not been seen.
                logger.error("Rule cannot reference inexisting rule '%s'",
                             self.by_ref)
                raise LGRFormatException(LGRFormatException.LGRFormatReason.INVALID_BY_REF)

        is_top_level = len(parents) == 0
        if (is_top_level and self.name is None) or \
            (not is_top_level and self.name is not None):
            # From RFC7940, section section 6.3.4. The name and by-ref Attributes
            # rules declared as immediate child elements of the "rules" element
            # MUST be named using a unique "name" attribute,
            # and all other instances MUST NOT be named.
            logger.error("'name' attribute MUST be present only and only if "
                         "rule is a direct child of the 'rules' element")
            raise LGRFormatException(LGRFormatException.LGRFormatReason.INVALID_TOP_LEVEL_NAME)

        logger.debug('Validate %s children', self)
        for child in self.children:
            child.validate(parents + [self], rules_lookup, classes_lookup)

        logger.debug('%s is valid', self)

    def __repr__(self):
        if self.name is None:
            return '<Anonymous rule>'
        else:
            return '<Rule: %s>' % self.name

    def __str__(self):
        if self.by_ref is not None:
            return '(:rule-ref-{}:)'.format(self.by_ref)

        return ' '.join('{}'.format(m) for m in self.children)
