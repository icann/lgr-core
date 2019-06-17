# -*- coding: utf-8 -*-
"""
metadata.py - Check metadata rfc7940 compliance
"""

import logging
import datetime
import mimetypes
import re

logger = logging.getLogger(__name__)

VALID_SCOPE_TYPES = set([
    None,
    "domain",
])

def check_metadata(lgr, options):
    """
    Check the meta element for RFC7940 compliance.

    :param LGR lgr: The LGR to check.
    :param options: Dictionary of options to the validation function - unused.
    :return True if compliant, False otherwise.
    """
    success = True
    logger.info("Testing metadata")
    result = {
        'description': 'Testing metadata',
        'repertoire': []
    }

    # validity_start, validity_end
    vstart = lgr.metadata.validity_start
    vend = lgr.metadata.validity_end

    today = datetime.date.today().strftime("%Y-%m-%d")

    if vend is not None and today > vend:
        logging.error("validity_end has expired")
        lgr.notify_error('validity_end_expiry')
        success = False
    lgr.notify_tested('validity_end_expiry')

    if vstart is not None and vend is not None and vstart > vend:
        logging.error("validity_start is later than validity_end")
        lgr.notify_error('validity_start_end')
        success = False
    lgr.notify_tested('validity_start_end')

    if vstart is not None and vstart > today:
        logging.error("validity_start is in the future")
        lgr.notify_error('validity_started')
        success = False
    lgr.notify_tested('validity_started')

    # description
    if lgr.metadata.description is not None:
        t = lgr.metadata.description.description_type
        if t is not None:
            if t not in mimetypes.types_map.values():
                logging.error("description has invalid mime type '%s'", t)
                lgr.notify_error('metadata_description_type')
                success = False
    lgr.notify_tested('metadata_description_type')

    # scope
    for s in lgr.metadata.scopes:
        if s.scope_type not in VALID_SCOPE_TYPES:
            logging.error("invalid scope type '%s'", s.scope_type)
            lgr.notify_error('metadata_scope_type')
            success = False
    lgr.notify_tested('metadata_scope_type')

    # Version
    if lgr.metadata.version is not None:
        if not re.match(r'[1-9]\d*$', lgr.metadata.version.value):
            lgr.notify_error('metadata_version_integer')
            success = False
    lgr.notify_tested('metadata_version_integer')
    logger.info("Metadata test done")

    return success, result
