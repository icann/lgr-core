# -*- coding: utf-8 -*-
"""
action.py - Definition of action structures.
"""
from __future__ import unicode_literals

import logging

from lgr.utils import format_cp
from lgr.exceptions import LGRFormatException

logger = logging.getLogger(__name__)
rule_logger = logging.getLogger('lgr-rule-logger')


class Action(object):
    """
    Represent an action element.

    Defined in 6. The action Element
    """
    def __init__(self, disp,
                 comment=None,
                 ref=None,
                 match=None,
                 not_match=None,
                 any_variant=None,
                 all_variants=None,
                 only_variants=None):
        """
        Create the action element.

        :param disp: Disposition of the action.
        :param comment: Optional comment.
        :param ref: Optional list of references.
        :param match: Name of a rule that must be matched.
        :param not_match: Name of a rule that must not be matched.
        :param any_variant: Sequence of disposition to match to trigger action.
        :param all_variants: Sequence of disposition to match to trigger action.
        :param only_variants: Sequence of disposition to match to trigger action.
        """
        self.disp = disp
        self.comment = comment
        self.references = ref or []
        self.match = match
        self.not_match = not_match
        self.any_variant = frozenset(any_variant) if any_variant else None
        self.all_variants = frozenset(all_variants) if all_variants else None
        self.only_variants = frozenset(only_variants) if only_variants else None

        if match is not None and not_match is not None:
            # From RFC7940, section 7.1. The "match" and "not-match" Attributes
            # An action MUST NOT contain both a "match" and a "not-match" attribute
            logger.error("Action contains both 'match' and 'not-match' "
                         "attributes")
            raise LGRFormatException(LGRFormatException.LGRFormatReason.MATCH_NOT_MATCH)

    def apply(self, label, disp_set, only_variants,
              rules_lookup, classes_lookup,
              unicode_database):
        """
        Apply an action to a label.

        :param label: The label to process, as a sequence of code points.
        :param disp_set: Set of dispositions used to generate the label.
        :param only_variants: True if label only contains code point
                              from variant mapping.
        :param rules_lookup: Dictionary of defined rules in the LGR.
        :param classes_lookup: Dictionary of defined classes in the LGR.
        :param unicode_database: The Unicode Database used to process rules.
        :return: The final label disposition,
                 None is no action applies to the label.
        :raises RuleError: If rule is invalid.
        """

        # RFC7940, section 8.3.  Determining a Disposition for a Label or Variant Label
        # Step 2
        rule_logger.debug("Applying action %s on label '%s' "
                          "with disposition set '%s'",
                          self, format_cp(label), disp_set)

        # First bullet
        rule_matched = True
        if self.match is not None:
            rule = rules_lookup[self.match]
            rule_matched = rule.matches(label,
                                        rules_lookup, classes_lookup,
                                        unicode_database)
            rule_logger.info('Action %s: when rule matched: %s',
                             self, rule_matched)
        # Second bullet
        elif self.not_match is not None:
            rule = rules_lookup[self.not_match]
            rule_matched = not rule.matches(label,
                                            rules_lookup, classes_lookup,
                                            unicode_database)
            rule_logger.info('Action %s: not-when rule matched: %s',
                             self, rule_matched)

        # Third bullet
        variant_matched = True
        if self.any_variant is not None:
            # Any single match may trigger an action that contains
            # an "any-variant" attribute
            variant_matched = len(self.any_variant & disp_set) > 0
            rule_logger.info('Action %s: any-variant matched: %s',
                             self, variant_matched)
        # Fourth bullet
        elif self.all_variants is not None:
            # For an "all-variants" attribute,
            # the variant type for all variant code points must match one or
            # several of the types values specified in to trigger the action.
            variant_matched = (len(disp_set) > 0
                               and disp_set.issubset(self.all_variants))
            rule_logger.info('Action %s: all-variants matched: %s',
                             self, variant_matched)
        # Fifth bullet
        elif self.only_variants is not None:
            # For an "only-variants" attribute,
            # the variant type for all variant code points must match one or
            # several of the types values specified in to trigger the action.
            # An "only-variants" attribute will trigger the action
            # only if all code points of the variant label have variant mappings
            # from the original code points.
            # => Label only contains code points generated from variant mappings
            # (including reflexive mappings)
            variant_matched = (only_variants
                               and len(disp_set) > 0
                               and disp_set.issubset(self.only_variants))
            rule_logger.info('Action %s: only-variants matched: %s',
                             self, variant_matched)

        # Last bullet: rule_matched and variant_matched are initialised to True
        if rule_matched and variant_matched:
            rule_logger.info('Action %s triggered, disposition: %s',
                             self, self.disp)
            return self.disp

        rule_logger.info('Action %s not triggered', self)
        return None

    def __repr__(self):
        return '<Action: {}>'.format(self.comment or 'anon')

    def __eq__(self, other):
        return (self.disp == other.disp)\
               and (self.match == other.match)\
               and (self.not_match == other.not_match)\
               and (self.any_variant == other.any_variant)\
               and (self.all_variants == other.all_variants)\
               and (self.only_variants == other.only_variants)

    def __hash__(self):
        return hash((self.disp,
                     self.match, self.not_match,
                     self.any_variant, self.all_variants, self.only_variants))
