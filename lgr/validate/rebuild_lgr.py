# -*- coding: utf-8 -*-
"""
rebuild_lgr.py - Entirely rebuild an LGR structure.
"""
from __future__ import unicode_literals
import logging
import copy

from lgr.char import RangeChar
from lgr.utils import format_cp
from lgr.exceptions import LGRException, CharNotInScript, CharInvalidIdnaProperty

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

    unicode_version = options.get('unicode_version',
                                  lgr.metadata.unicode_version)
    validating_repertoire = options.get('validating_repertoire', None)

    description = "Rebuilding LGR with Unicode version {}".format(unicode_version)
    if validating_repertoire is not None:
        description += " and validating repertoire '{}'".format(validating_repertoire)
    result = {
        'description': description,
        'repertoire': {}  # XXX: Cannot use defaultdict because of django...
    }

    logger.info("Rebuilding LGR '%s' with Unicode version %s "
                "and Validating Repertoire '%s'",
                lgr, unicode_version, validating_repertoire)

    unidb = options.get('unidb', None)
    if unidb is not None:
        unidb_version = unidb.get_unicode_version()
        if unidb_version != unicode_version:
            result['generic'] = "Target Unicode version {} " \
                                "differs from UnicodeDatabase {}".format(unicode_version,
                                                                         unidb_version)
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
            range_ok = True
            for cp, status in target_lgr.check_range(char.first_cp, char.last_cp,
                                                     validating_repertoire):
                if status is not None:
                    result['repertoire'].setdefault(char, {}).setdefault('errors', []).append(status)
                    range_ok = False
                in_script, _ = lgr.cp_in_script([cp])
                if not in_script:
                    result['repertoire'].setdefault(char, {}).setdefault('warnings', []).append(CharNotInScript(cp))
                    range_ok = False

            if not range_ok:
                continue

            try:
                target_lgr.add_range(char.first_cp, char.last_cp,
                                     comment=char.comment,
                                     ref=char.references,
                                     tag=char.tags,
                                     when=char.when, not_when=char.not_when,
                                     validating_repertoire=validating_repertoire,
                                     override_repertoire=False)
            except LGRException as exc:
                result['repertoire'].setdefault(char, {}).setdefault('errors', []).append(exc)
                logger.error("Cannot add range '%s-%s'",
                             format_cp(char.first_cp),
                             format_cp(char.last_cp))
            continue

        in_script, _ = lgr.cp_in_script(char.cp)
        if not in_script:
            result['repertoire'].setdefault(char, {}).setdefault('warnings', []).append(CharNotInScript(char.cp))
        # Insert code point
        try:
            target_lgr.add_cp(char.cp,
                              comment=char.comment,
                              ref=char.references,
                              tag=char.tags,
                              when=char.when, not_when=char.not_when,
                              validating_repertoire=validating_repertoire,
                              override_repertoire=False)
        except LGRException as exc:
            result['repertoire'].setdefault(char, {}).setdefault('errors', []).append(exc)
            logger.error("Cannot add code point '%s'", format_cp(char.cp))
            if not isinstance(exc, CharInvalidIdnaProperty):  # Cannot include non-IDNA valid code points
                target_lgr.add_cp(char.cp,
                                  comment=char.comment,
                                  ref=char.references,
                                  tag=char.tags,
                                  when=char.when, not_when=char.not_when,
                                  force=True)

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
            except LGRException as exc:
                result['repertoire'].setdefault(char, {}).setdefault('variants', {}).setdefault(var, []).append(exc)
                logger.error("Cannot add variant '%s' to code point '%s'", format_cp(var.cp), format_cp(char.cp))
                if not isinstance(exc, CharInvalidIdnaProperty):  # Cannot include non-IDNA valid code points
                    target_lgr.add_variant(char.cp,
                                           variant_cp=var.cp,
                                           variant_type=var.type,
                                           when=var.when, not_when=var.not_when,
                                           comment=var.comment, ref=var.references,
                                           force=True)

    logger.info("Rebuilding LGR '%s done", lgr)

    return True, result
