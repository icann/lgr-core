# -*- coding: utf-8 -*-
"""
parser.py - Base class for LGR parser.
"""
import logging
import os
import io

from lgr.core import LGR

logger = logging.getLogger(__name__)


class LGRParser(object):
    """
    This class is intended to define a base class to be inherited by actual parser classses.
    """

    def __init__(self, source, filename=None):
        self.source = source

        if not filename and isinstance(self.source, str):
            self.filename = os.path.basename(self.source)
        else:
            self.filename = filename

        self._unicode_database = None
        self._lgr = None

    @property
    def unicode_database(self):
        return self._unicode_database

    @unicode_database.setter
    def unicode_database(self, unidb):
        """
        Set the Unicode Database.

        :param unidb: The Unicode database to use
        """
        self._unicode_database = unidb
        if self._lgr is not None:
            self._lgr.unicode_database = unidb

    def unicode_version(self):
        """
        Get the Unicode version of the LGR document.

        :return: A string containing the Unicode version.
        """
        raise NotImplementedError()

    def validate_document(self, schema=None):
        """
        Validate the document source.

        Ensure the input file as a correct format
        and can be parsed into an LGR data structure.

        :param schema: Optional external validation file.
        :return: None if validation is correct,
                 an implementation-specific object otherwise.
        """
        raise NotImplementedError()

    def parse_document(self, force=False):
        """
        Actual parsing of the LGR document specified in constructor.

        :return: The LGR structure.
        """
        self._lgr = LGR(name=self.filename)

        logger.debug('Start parsing of file: %s', self.filename)

        if hasattr(self.source, "read"):
            self._parse_doc(self.source, force=force)
        else:
            with io.open(self.source, 'r', encoding='utf-8') as rule_file:
                self._parse_doc(rule_file, force=force)

        return self._lgr

    def _parse_doc(self, rule_file, force=False):
        raise NotImplementedError()
