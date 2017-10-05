# -*- coding: utf-8 -*-
"""
classes.py - Definition of class structures.
"""
from __future__ import unicode_literals

import logging

from lgr.exceptions import (LGRFormatException, RuleError)

logger = logging.getLogger(__name__)

# Key used to store an internal tag-based class
# As tags are XML NMTOKEN, they can't start with an '#'
# So use this char to avoid any collision.
TAG_CLASSNAME_PREFIX = "#__internal_tag_"


def set_to_rvalue(cp_set, as_set):
    """
    Convert a set to a return value.

    If `cp_set` is empty and `as_set` is False, then the rvalue is a text
    pattern to be used in regex. As the set is empty, '[]' is not a valid
    regex, so take care of this case here.

    :param cp_set: Code point set.
    :param as_set: If True, rvalue is a set, unicode string otherwise.
    :return: Either a set or a unicode string.
    """
    if as_set:
        return cp_set
    else:
        if len(cp_set) == 0:
            # Empty set, we have to return empty string
            # because '[]' is an invalid REGEX
            return unicode('')
        else:
            return unicode(cp_set)


class Class(object):
    """
    Base class to represent Class.
    """
    def __init__(self, name=None,
                 comment=None,
                 ref=None,
                 from_tag=None,
                 unicode_property=None,
                 codepoints=None,
                 by_ref=None):
        """
        Create a class.

        :param name: Name of the class.
        :param comment: Optional comment associated to the class.
        :param ref: Optional list of references.
        :param from_tag: Define a tag-based class.
        :param unicode_property: Define a Unicode property-based class.
        :param codepoints: Initial sequence of code points.
        :param by_ref: Name of the referenced class.
        """
        self.name = name
        self.comment = comment
        self.ref = ref or []
        self.from_tag = from_tag
        self.unicode_property = unicode_property
        self.codepoints = set(codepoints or [])
        self.by_ref = by_ref

        if by_ref is not None:
            if name is not None:
                logger.error("Cannot create a class with "
                             "both a 'by-ref' and a 'name'")
                raise LGRFormatException(LGRFormatException.LGRFormatReason.BY_REF_AND_OTHER)
            elif from_tag is not None:
                logger.error("Cannot create a class with "
                             "both a 'by-ref' and a 'from-tag'")
                raise LGRFormatException(LGRFormatException.LGRFormatReason.BY_REF_AND_OTHER)
            elif unicode_property is not None:
                logger.error("Cannot create a class with "
                             "both a 'by-ref' and a 'property'")
                raise LGRFormatException(LGRFormatException.LGRFormatReason.BY_REF_AND_OTHER)
            elif ref is not None:
                logger.error("Cannot create a class with "
                             "both a 'by-ref' and a 'ref'")
                raise LGRFormatException(LGRFormatException.LGRFormatReason.BY_REF_AND_OTHER)

    def add_codepoint(self, cp):
        """
        Add (a) codepoint(s) to the set of codepoints.

        :param cp: Code point(s) to add. An integer or a sequence of code points.
        """
        if self.by_ref is not None:
            logger.error("Cannot add code point to a 'by-ref' class")
            raise LGRFormatException(LGRFormatException.LGRFormatReason.BY_REF_AND_OTHER)

        if isinstance(cp, int):
            cp = [cp]
        self.codepoints.update(cp)

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False, as_set=False):
        """
        Return a pattern describing the class which can be used in a regex.

        :param rules_lookup: Dictionary of defined rules in the LGR. Not used.
        :param classes_lookup: Dictionary of defined classes in the LGR to use
                               for by-ref classes.
        :param unicode_database: The Unicode Database.
        :param is_look_behind: True if class is used in a look-behind element.
        :param as_set: If True, return the set object instead of a string.
        :return: A text pattern that can be used as a regular expression,
                 or the set object related to this pattern.
        """
        if self.by_ref is not None:
            if self.by_ref not in classes_lookup:
                logger.error("Class cannot reference inexisting rule '%s'",
                             self.by_ref)
                raise RuleError(self,
                                "%s cannot reference "
                                "inexisting class '%s'" % (self, self.by_ref))
            cp_set = classes_lookup[self.by_ref].get_pattern(rules_lookup,
                                                             classes_lookup,
                                                             unicode_database,
                                                             is_look_behind,
                                                             as_set)
        elif self.from_tag is not None:
            tag_classname = TAG_CLASSNAME_PREFIX + self.from_tag
            if tag_classname not in classes_lookup:
                logger.warning("Undefined tag '%s' in current LGR",
                               self.from_tag)
                cp_set = unicode_database.get_set()
            else:
                cp_set = classes_lookup[tag_classname].get_pattern(rules_lookup,
                                                                   classes_lookup,
                                                                   unicode_database,
                                                                   is_look_behind,
                                                                   as_set)
        elif self.unicode_property is not None:
            (name, value) = self.unicode_property.split(':')
            cp_set = unicode_database.get_set(pattern='\p{%s=%s}' % (name, value))
        else:
            cp_set = unicode_database.get_set(self.codepoints)

        return set_to_rvalue(cp_set, as_set)

    def validate(self, parents, rules_lookup, classes_lookup):
        """
        Ensure a class has a valid definition.

        :param parents: List of parent objects of this instance.
        :param rules_lookup: Dictionary of defined rules in the LGR. Not used.
        :param classes_lookup: Dictionary of defined classes in the LGR to use
                               for by-ref classes.
        """
        logger.debug('Validate %s', self)
        if self.by_ref is not None:
            if self.by_ref not in classes_lookup:
                # From RFC7940, section 6.2.1. Declaring and Invoking Named Classes
                # It is an error to reference a named class for which the
                # definition has not been seen.
                logger.error("Class cannot reference inexisting class '%s'",
                             self.by_ref)
                raise LGRFormatException(LGRFormatException.LGRFormatReason.INVALID_BY_REF)

        is_top_level = len(parents) == 0
        if (is_top_level and self.name is None) or \
            (not is_top_level and self.name is not None):
            # From RFC7940, section 6.2.1. Declaring and Invoking Named Classes
            # The "name" attribute MUST be present if and only if the class
            # is a direct child element of the "rules" element.
            logger.error("'name' attribute MUST be present only and only if "
                         "class is a direct child of the 'rules' element")
            raise LGRFormatException(LGRFormatException.LGRFormatReason.INVALID_TOP_LEVEL_NAME)

        if self.from_tag is not None:
            tag_classname = TAG_CLASSNAME_PREFIX + self.from_tag
            if tag_classname not in classes_lookup:
                logger.warning("Undefined tag '%s' in current LGR",
                               self.from_tag)

    def __repr__(self):
        return '<Class %s>' % (self.name or self.from_tag or self.by_ref)


class CombinatorClass(Class):
    """
    Base class for combinator operations.
    """

    MAX_CHILDREN = 0

    def __init__(self, name=None, comment=None):
        super(CombinatorClass, self).__init__(name=name, comment=comment)
        self._children = []

    def add_child(self, cls):
        if self.MAX_CHILDREN > 0 and len(self._children) >= self.MAX_CHILDREN:
            logger.error("Cannot have more than %s children", self.MAX_CHILDREN)
            raise LGRFormatException(LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        self._children.append(cls)

    def validate(self, parents, rules_lookup, classes_lookup):
        super(CombinatorClass, self).validate(parents,
                                              rules_lookup, classes_lookup)
        for child in self._children:
            child.validate(parents + [self], rules_lookup, classes_lookup)
        logger.debug('%s is valid', self)

    def __repr__(self):
        return '<Combinator>'


class ComplementClass(CombinatorClass):
    """
    Define the complement of a given class.
    """

    MAX_CHILDREN = 1

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False, as_set=False):
        # TODO: test existence of child
        child = self._children[0]
        cp_set = unicode_database.get_set(child.get_pattern(rules_lookup,
                                                            classes_lookup,
                                                            unicode_database,
                                                            is_look_behind,
                                                            as_set=True))
        cp_set.complement()
        return set_to_rvalue(cp_set, as_set)

    def validate(self, parents, rules_lookup, classes_lookup):
        super(ComplementClass, self).validate(parents,
                                              rules_lookup, classes_lookup)
        if len(self._children) != 1:
            logger.error("'Complement' class MUST contain one element")
            raise LGRFormatException(LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        logger.debug('%s is valid', self)

    def __repr__(self):
        return '<ComplementClass %s: %s>' % (self.name, self._children)


class UnionClass(CombinatorClass):
    """
    Define the union of multiple classes.
    """

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False, as_set=False):
        cp_set = unicode_database.get_set()
        for child in self._children:
            cp_set.update(child.get_pattern(rules_lookup, classes_lookup,
                                            unicode_database,
                                            is_look_behind,
                                            as_set=True))

        return set_to_rvalue(cp_set, as_set)

    def validate(self, parents, rules_lookup, classes_lookup):
        super(UnionClass, self).validate(parents,
                                         rules_lookup, classes_lookup)
        if len(self._children) < 2:
            logger.error("'Union' class MUST contain two or more element")
            raise LGRFormatException(LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        logger.debug('%s is valid', self)

    def __repr__(self):
        return '<UnionClass %s: %s>' % (self.name, self._children)


class IntersectionClass(CombinatorClass):
    """
    Define the intersection of multiple classes.
    """

    MAX_CHILDREN = 2

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False, as_set=False):

        set_1 = self._children[0].get_pattern(rules_lookup, classes_lookup,
                                              unicode_database,
                                              is_look_behind, as_set=True)
        set_2 = self._children[1].get_pattern(rules_lookup, classes_lookup,
                                              unicode_database,
                                              is_look_behind, as_set=True)

        # __and__ does make a copy of the set
        cp_set = set_1 & set_2

        return set_to_rvalue(cp_set, as_set)

    def validate(self, parents, rules_lookup, classes_lookup):
        super(IntersectionClass, self).validate(parents,
                                                rules_lookup, classes_lookup)
        if len(self._children) != 2:
            logger.error("'Intersection' class MUST contain two elements")
            raise LGRFormatException(LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        logger.debug('%s is valid', self)

    def __repr__(self):
        return '<IntersectionClass %s: %s>' % (self.name, self._children)


class DifferenceClass(CombinatorClass):
    """
    Define the difference of multiple classes.
    """

    MAX_CHILDREN = 2

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False, as_set=False):
        set_1 = self._children[0].get_pattern(rules_lookup, classes_lookup,
                                              unicode_database,
                                              is_look_behind, as_set=True)
        set_2 = self._children[1].get_pattern(rules_lookup, classes_lookup,
                                              unicode_database,
                                              is_look_behind, as_set=True)

        # __sub__ does make a copy of the set
        cp_set = set_1 - set_2

        return set_to_rvalue(cp_set, as_set)

    def validate(self, parents, rules_lookup, classes_lookup):
        super(DifferenceClass, self).validate(parents,
                                              rules_lookup, classes_lookup)
        if len(self._children) != 2:
            logger.error("'Difference' class MUST contain two elements")
            raise LGRFormatException(LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        logger.debug('%s is valid', self)

    def __repr__(self):
        return '<DifferenceClass %s: %s>' % (self.name, self._children)


class SymmetricDifferenceClass(CombinatorClass):
    """
    Define the symmetric difference of multiple classes.
    """

    MAX_CHILDREN = 2

    def get_pattern(self, rules_lookup, classes_lookup, unicode_database,
                    is_look_behind=False, as_set=False):

        set_1 = self._children[0].get_pattern(rules_lookup, classes_lookup,
                                              unicode_database,
                                              is_look_behind, as_set=True)
        set_2 = self._children[1].get_pattern(rules_lookup, classes_lookup,
                                              unicode_database,
                                              is_look_behind, as_set=True)

        # __and__ and __or__ do make a copy of the set
        cp_set = (set_1 | set_2) - (set_1 & set_2)

        return set_to_rvalue(cp_set, as_set)

    def validate(self, parents, rules_lookup, classes_lookup):
        super(SymmetricDifferenceClass, self).validate(parents,
                                                       rules_lookup,
                                                       classes_lookup)
        if len(self._children) != 2:
            logger.error("'Symmetric Difference' class MUST contain two elements")
            raise LGRFormatException(LGRFormatException.LGRFormatReason.INVALID_CHILDREN_NUMBER)

        logger.debug('%s is valid', self)

    def __repr__(self):
        return '<SymmetricDifferenceClass %s: %s>' % (self.name, self._children)
