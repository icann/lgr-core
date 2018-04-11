# -*- coding: utf-8 -*-
"""
xml_validity.py - Check that the resulting LGR serialized to XML is valid.
"""
from __future__ import unicode_literals

import logging
from io import BytesIO

logger = logging.getLogger(__name__)


def check_xml_validity(lgr, options):
    """
    Serialize the LGR to XML, and validate the XML against the RNG.

    `options` argument can contain:
        * rng_filepath: Filepath of the RNG schema used to validate.
          when rebuilding the LGR. If None is given, use the current one.

    :param LGR lgr: The LGR to check.
    :param options: Dictionary of options to the validation function.
    """
    # Local import to prevent import cycles.
    from lgr.parser.xml_serializer import serialize_lgr_xml
    from lgr.parser.xml_parser import XMLParser

    logger.info("Testing XML validity")

    if 'rng_filepath' not in options:
        logger.warning("rng_filepath not in 'options' arguments, skipping")
        return True, {}

    xml = BytesIO(serialize_lgr_xml(lgr))
    parser = XMLParser(xml)

    result = {
        'description': "Testing XML validity using RNG"
    }

    validation_result = parser.validate_document(options['rng_filepath'])
    if validation_result is not None:
        logger.warning('RNG validation failed: XML error is')
        logger.warning(validation_result)
        result['validation_result'] = validation_result
    else:
        logger.info('RNG validation OK')
    result['rng_result'] = validation_result is None

    logger.info("Testing XML validity done")

    return validation_result is None, result
