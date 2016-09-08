# -*- coding: utf-8 -*-
"""
rebuild_lgr.py - Entirely rebuild an LGR structure.
"""
from __future__ import unicode_literals
import logging
import copy

from lgr.char import RangeChar
from lgr.utils import format_cp
from lgr.exceptions import LGRException

logger = logging.getLogger(__name__)


def rebuild_lgr(lgr, options):
    """
    Rebuild an LGR with given parameters.

    options argument can contain:
        * unicode_version: The target Unicode version to be used
          when rebuilding the LGR. If None is given, use the current one.
        * validating_repertoire: The validating repertoire used
          for checking code points.
        * unidb: Munidata's Unicode database. If None, skip Unicode checks.

    :param LGR lgr: The LGR to rebuild.
    :param dict options: Dictionary of options to the validation function.
    """
    # Local import to prevent import cycles
    from lgr.core import LGR

    # Redirect LGR-general log to lgr.validate logger
    # Since we are just rebuilding an LGR, the main point of the test
    # being to catch all errors/warning from regular code
    # when we insert codepoints/variants
    lgr_logger = logging.getLogger('lgr.core')
    lgr_logger_level = lgr_logger.getEffectiveLevel()
    log_handler = options.get('log_handler', None)
    if log_handler is not None:
        lgr_logger.setLevel('INFO')
        lgr_logger.addHandler(log_handler)

    unicode_version = options.get('unicode_version',
                                  lgr.metadata.unicode_version)
    validating_repertoire = options.get('validating_repertoire', None)

    logger.info("Rebuilding LGR '%s' with Unicode version %s "
                "and Validating Repertoire '%s'",
                lgr, unicode_version, validating_repertoire)

    unidb = options.get('unidb', None)
    if unidb is not None:
        unidb_version = unidb.get_unicode_version()
        if unidb_version != unicode_version:
            logger.warning("Target Unicode version %s differs "
                           "from UnicodeDatabase %s",
                           unicode_version, unidb_version)

    # For now, simply copy the metadata and references of the source LGR
    target_metadata = copy.deepcopy(lgr.metadata)
    target_metadata.unicode_version = unicode_version
    target_reference_manager = copy.deepcopy(lgr.reference_manager)

    target_lgr = LGR(name=lgr.name,
                     metadata=target_metadata,
                     reference_manager=target_reference_manager,
                     unicode_database=unidb)

    for char in lgr.repertoire:
        if isinstance(char, RangeChar):
            try:
                target_lgr.add_range(char.first_cp, char.last_cp,
                                     comment=char.comment,
                                     ref=char.references,
                                     tag=char.tags,
                                     when=char.when, not_when=char.not_when,
                                     validating_repertoire=validating_repertoire,
                                     override_repertoire=False)
            except LGRException:
                logger.error("Cannot add range '%s-%s'",
                             format_cp(char.first_cp),
                             format_cp(char.last_cp))
            continue

        # Insert code point
        try:
            target_lgr.add_cp(char.cp,
                              comment=char.comment,
                              ref=char.references,
                              tag=char.tags,
                              when=char.when, not_when=char.not_when,
                              validating_repertoire=validating_repertoire,
                              override_repertoire=False)
        except LGRException:
            logger.error("Cannot add code point '%s'",
                         format_cp(char.cp))

        # Create variants
        for var in char.get_variants():
            try:
                target_lgr.add_variant(char.cp,
                                       variant_cp=var.cp,
                                       variant_type=var.type,
                                       when=var.when, not_when=var.not_when,
                                       comment=var.comment, ref=var.references,
                                       validating_repertoire=validating_repertoire,
                                       override_repertoire=True)
            except LGRException:
                logger.error("Cannot add variant '%s' to code point '%s'",
                             format_cp(var.cp),
                             format_cp(char.cp))

    if log_handler is not None:
        lgr_logger.setLevel(lgr_logger_level)
        lgr_logger.removeHandler(log_handler)

    logger.info("Rebuilding LGR '%s done", lgr)

    return True
