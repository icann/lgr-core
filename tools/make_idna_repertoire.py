#!/bin/env python
# -*- coding: utf-8 -*-
"""
make_idna_repertoire.py - Parse IDNA2008 table to create a repertoire.

Parse the IDNA 2008 tables from IANA website and create an LGR XML file
with all codepoints with PVALID or CONTEXTO/J property.
"""
from lxml import etree
import sys
import argparse
import logging

IDNATABLES_URL = "http://www.iana.org/assignments/idna-tables-{version}/idna-tables-{version}.xml"
IDNATABLES_NS = "http://www.iana.org/assignments"

CODEPOINT_TAG = "{%s}codepoint" % IDNATABLES_NS
PROPERTY_TAG = "{%s}property" % IDNATABLES_NS

logger = logging.getLogger(__name__)


def make_idna_repertoire(version):
    """
    Make a repertoire from IDNA tables.
    Parse IDNA table registry, convert it to an LGR XML format,
    and output it on stdout.

    Input:
        * version: The unicode version to use.
    """
    from lgr.core import LGR
    from lgr.parser.xml_serializer import serialize_lgr_xml

    lgr = LGR('idna2008-%s' % version)

    idna_url = IDNATABLES_URL.format(version=version)
    logger.debug("Fetching and parsing '%s'", idna_url)
    registry = etree.parse(idna_url)

    # To keep '{}' when string-formatting
    namespace = "{{{0}}}".format(IDNATABLES_NS)
    record_xpath = '{0}registry[@id="idna-tables-properties"]/{0}record'.format(namespace)

    for record in registry.findall(record_xpath):
        codepoint = record.find(CODEPOINT_TAG).text
        prop = record.find(PROPERTY_TAG).text

        if prop not in ['PVALID', 'CONTEXTO', 'CONTEXTJ']:
            continue

        if codepoint.find('-') > 0:
            # Codepoint is a range
            (first_cp, last_cp) = [int(c, 16) for c in codepoint.split('-')]
            lgr.add_range(first_cp, last_cp)
        else:
            # Single codepoint
            lgr.add_cp(int(codepoint, 16))

    lgr_root = serialize_lgr_xml(lgr, pretty_print=True, encoding='unicode', xml_declaration=False)
    print(lgr_root)


def main():

    parser = argparse.ArgumentParser(description='Parse and make a repertoire '
                                                 'from IDNA2008 registry')
    parser.add_argument('-v', '--verbose', action='store_true', help='be verbose')
    parser.add_argument('unicode', metavar='Unicode Version')

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG if args.verbose else logging.INFO)

    make_idna_repertoire(args.unicode)


if __name__ == '__main__':
    main()
