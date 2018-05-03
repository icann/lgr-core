# -*- coding: utf-8 -*-
"""
diff_collisions.py - Diff and collisions of labels
"""
from __future__ import unicode_literals

from copy import deepcopy

from collections import Counter

from lgr.utils import format_cp, cp_to_ulabel
from lgr.exceptions import InvalidSymmetry, NotInLGR

MD = "\n```\n"

LRI = '\u2066'
PDI = '\u2069'

PRIMARY = 'Primary'
VARIANT = 'Variant'


def _generate_indexes(lgr, labels, keep=False, quiet=False):
    """
    Generate indexes based on labels provided in the list

    :param lgr: The current LGR
    :param labels: The list of labels, as a list of U-Labels.
    :param keep: Do we keep labels without collision in the output
    :param quiet: If True, do not collect rule log.

    :return: (label_indexes, not_in_lgr), with:
              - label_indexes: the dictionary containing the primary labels
                               and their variants (with various information) for each index.
              - not_in_lgr: List of labels that do not pass preliminary eligibility testing.
  """

    label_indexes = {}
    not_in_lgr = []
    # Get the indexes and variants for all labels
    for label in labels:
        label_cp = tuple([ord(c) for c in label])
        try:
            label_index = lgr.generate_index_label(label_cp)
        except NotInLGR:
            not_in_lgr.append(label_cp)
            continue

        label_cp_out = format_cp(label_cp)
        if label_index not in label_indexes:
            label_indexes[label_index] = []
        label_indexes[label_index].append({'label': label,
                                           'bidi': "%s'%s'%s" % (LRI,
                                                                 label,
                                                                 PDI),
                                           'cat': PRIMARY,
                                           'cp': label_cp,
                                           'cp_out': label_cp_out,
                                           'disp': {label: '-'},
                                           'rules': {label: '-'},
                                           'action_idx': {label: '-'}
                                           })

    for (label_index, primaries) in deepcopy(label_indexes).items():
        # only get variants for collided labels (if not keep)
        if len(primaries) < 2 and not keep:
            del label_indexes[label_index]
            continue
        for primary in primaries:
            label_cp = primary['cp']
            label = primary['label']
            for (variant_cp,
                 variant_disp,
                 action_idx, _,
                 log) in lgr.compute_label_disposition(label_cp,
                                                       include_invalid=True,
                                                       collect_log=not quiet):
                variant = cp_to_ulabel(variant_cp)
                log = log.strip()
                if quiet:
                    log = ''
                variant_cp_out = format_cp(variant_cp)
                # search if variant is already in our dict, then add or
                # update it
                existing = [var for var in label_indexes[label_index]
                            if var['label'] == variant]
                if len(existing) < 1:
                    label_indexes[label_index].append({'label': variant,
                                                       'bidi': "%s'%s'%s" % (LRI,
                                                                             variant,
                                                                             PDI),
                                                       'cat': VARIANT,
                                                       'cp': variant_cp,
                                                       'cp_out': variant_cp_out,
                                                       'disp': {label: variant_disp},
                                                       'rules': {label: log},
                                                       'action_idx': {label: action_idx}
                                                       })
                else:
                    assert len(existing) == 1
                    existing[0]['disp'][label] = variant_disp
                    existing[0]['rules'][label] = log
                    existing[0]['action_idx'][label] = action_idx

    return label_indexes, not_in_lgr


def _compare(labels, label1_indexes, label2_indexes):
    for label in labels:
        label_cp_out = format_cp(tuple([ord(c) for c in label]))
        (index1, index2) = labels[label]
        yield "\n## Comparison on label " \
              "{label} [{cp}]\n".format(label="%s'%s'%s" % (LRI, label, PDI),
                                        cp=label_cp_out)
        yield "\n### Test dispositions: ###\n"
        labels2 = label2_indexes[index2]
        labels1 = label1_indexes[index1]
        # change in disposition
        ret = True
        for label2 in labels2:
            label2_cp = label2['cp']
            for label1 in labels1:
                label1_cp = label1['cp']
                if label1_cp == label2_cp:
                    (res, out) = _compare_labels(label, label1, label2)
                    ret &= res
                    if out:
                        yield MD
                        yield out
                        yield MD
        if ret:
            yield MD
            yield 'No changes in disposition.'
            yield MD

        # change in number of variants
        yield "\n### Test number of variants: ###\n"
        added = _get_new_variants(labels2, labels1)
        removed = _get_new_variants(labels1, labels2)
        for add in added:
            yield MD
            yield "New {cat} in LGR2:\n" \
                  "{label} [{cp}]\n".format(cat=add['cat'],
                                            label=add['bidi'],
                                            cp=add['cp_out'])
            try:
                yield "\nRules for LGR2:\n{}".format(add['rules'][label])
            except KeyError:
                raise InvalidSymmetry()
            yield MD
        for remove in removed:
            yield MD
            yield "Removed {cat} in LGR2:\n" \
                  "{label} [{cp}]\n".format(cat=remove['cat'],
                                            label=remove['bidi'],
                                            cp=remove['cp_out'])
            try:
                yield "\nRules for LGR1:\n{}".format(remove['rules'][label])
            except KeyError:
                raise InvalidSymmetry()
            yield MD

        if len(added) == 0 and len(removed) == 0:
            yield MD
            yield 'No changes in number of variants.'
            yield MD


def _compare_labels(primary, label1, label2):
    """
    Compare two labels disposition
    :param primary: the primary label
    :param label1: the first label
    :param label2: the second label

    :return A tuple containing True if there is no difference False otherwise
            and the output text
    """
    output = ""
    try:
        l1_disp = label1['disp'][primary]
        l2_disp = label2['disp'][primary]
    except KeyError:
        raise InvalidSymmetry()
    if l1_disp != l2_disp:
        output += "Change in disposition for {cat} {label} [{cp}] (2->1):" \
                  " {l2disp} => {l1disp}\n".format(cat=label2['cat'],
                                                   label=label2['bidi'],
                                                   cp=label2['cp_out'],
                                                   l2disp=l2_disp,
                                                   l1disp=l1_disp)
        if label2['cat'] == 'Primary':
            return False, output

        try:
            output += "\nRules for LGR2:\n{}\n".format(label2['rules'][primary])
            output += "\nRules for LGR1:\n{}".format(label1['rules'][primary])
        except KeyError:
            raise InvalidSymmetry()

        return False, output

    return True, output


def _get_new_variants(new_labels, old_labels):
    """
    Get a list of new variants for a label between two LGR
    :param new_labels: The label and its variants under the new LGR
    :param old_labels: The label and its variants under the old LGR

    :return a list of new variants
    """
    new_list = []
    for new in new_labels:
        new_cp = new['cp']
        found = False
        for old in old_labels:
            old_cp = old['cp']
            if old_cp == new_cp:
                found = True
                break
        if not found:
            new_list.append(new)
    return new_list


def _write_complete_output(label_indexes):
    """
    Output le collisions information between labels
    :param label_indexes: the dictionary containing the primary labels and
                          their variants (with various information) for each index.
    """
    output_labels = ("\n## Collision ##\n" + MD +
                     "Label:       \t{label:{len}} | {variant}\n"
                     "Code points: \t{label_cp:{len}} | {variant_cp}\n"
                     "Category:    \t{label_cat:{len}} | {variant_cat}" +
                     MD)
    output_dr = ("{cat} {label} [{label_cp}]:\n"
                 "\tDisposition: {label_disp}\n"
                 "\tRules:\n{label_rules}")
    collided = False
    for collisions in label_indexes.values():
        # do not output anything if there is not at least 2 primaries colliding
        if len(collisions) < 2 or \
                        len([lbl for lbl in collisions if lbl['cat'] == PRIMARY]) < 2:
            continue
        idx = 0
        collided = True
        primaries = [label for label in collisions if label['cat'] == PRIMARY]
        for label in collisions:
            idx += 1
            for variant in collisions[idx:]:
                yield output_labels.format(label="%s" % label['bidi'],
                                           variant="%s" % variant['bidi'],
                                           label_cp="[%s]" % label['cp_out'],
                                           variant_cp="[%s]" % variant['cp_out'],
                                           label_cat=label['cat'],
                                           variant_cat=variant['cat'],
                                           len=max(len(label['label']),
                                                   len(label['cat']),
                                                   len(label['cp_out'])) + 2)

                # do not output disposition and rules if both labels are
                # primaries
                if label['cat'] == PRIMARY and variant['cat'] == PRIMARY:
                    continue

                # output the disposition and rules for each primary
                for primary in primaries:
                    prim = primary['label']
                    cp_out = primary['cp_out']
                    try:
                        ldisp = label['disp'][prim]
                        lrules = label['rules'][prim]
                        vdisp = variant['disp'][prim]
                        vrules = variant['rules'][prim]
                    except KeyError:
                        raise InvalidSymmetry()

                    yield "\n### Details for label" \
                          " {label} [{cp}] ###\n".format(label=primary['bidi'],
                                                         cp=cp_out)
                    if label['label'] != prim and label['cat'] != PRIMARY:
                        yield MD
                        yield output_dr.format(cat=label['cat'],
                                               label="%s" % label['bidi'],
                                               label_cp=label['cp_out'],
                                               label_disp=ldisp,
                                               label_rules=lrules)
                        yield MD
                    if variant['label'] != prim and variant['cat'] != PRIMARY:
                        yield MD
                        yield output_dr.format(cat=variant['cat'],
                                               label="%s" % variant['bidi'],
                                               label_cp=variant['cp_out'],
                                               label_disp=vdisp,
                                               label_rules=vrules)
                        yield MD
    if not collided:
        yield MD
        yield "No collision in the list of labels"
        yield MD


def _full_dump(label_indexes):
    """
    Write a dump containing a summary of all labels variants
    :param label_indexes: the dictionary containing the primary labels and
                          their variants (with various information) for each index.
    """
    for labels in label_indexes.values():
        primaries = [label for label in labels if label['cat'] == PRIMARY]
        for primary in primaries:
            prim = primary['label']
            cp_out = primary['cp_out']
            yield "\n## Dump for label " \
                  "{label} [{cp}]: ##\n\n".format(label=primary['bidi'],
                                                  cp=cp_out)
            yield MD
            for variant in labels:
                if variant['label'] == prim:
                    continue
                yield "{cat} Label: " \
                      "{label} [{cp}]\n".format(cat=variant['cat'],
                                                label=variant['bidi'],
                                                cp=variant['cp_out'])
                try:
                    yield "\tDisposition {}\n".format(variant['disp'][prim])
                except KeyError:
                    raise InvalidSymmetry()

            yield "\nDisposition count:"
            try:
                for (disp, count) in Counter(disp for disp in [l['disp'][prim].lower() for l in labels]).most_common():
                    yield "\n - {}: {}".format(disp, count)
            except KeyError:
                raise InvalidSymmetry()
            yield MD


def diff(lgr_1, lgr_2, labels_input, show_collision=True,
         show_dump=False, quiet=False):
    """
    Show diff for a list of labels between 2 LGR

    :param lgr_1: The first LGR info object.
    :param lgr_2: The second LGR info object.
    :param labels_input: The file containing the labels
    :param show_collision: Output collisions
    :param show_dump: Generate a full dump
    :param quiet: Do not print rules
    """
    from lgr.tools.utils import read_labels
    labels = set()
    for label, valid, error in read_labels(labels_input, lgr_1.unicode_database):
        if valid:
            labels.add(label)
        else:
            yield "Label {}: {}\n".format(label, error)

    # get diff between labels and variants for the two LGR
    # keep label without collision as we need to compare
    label1_indexes, not_in_lgr_1 = _generate_indexes(lgr_1,
                                                     labels,
                                                     keep=True,
                                                     quiet=quiet)
    label2_indexes, not_in_lgr_2 = _generate_indexes(lgr_2,
                                                     labels,
                                                     keep=True,
                                                     quiet=quiet)

    if not_in_lgr_1 or not_in_lgr_2:
        for index, not_in_lgr in enumerate([not_in_lgr_1, not_in_lgr_2], 1):
            yield "# Labels not in LGR {} #\n\n".format(index)
            for label_cp in not_in_lgr:
                yield "Label {}\n".format(cp_to_ulabel(label_cp))
            yield '\n'

    # generate a dictionary of indexes per label
    labels_dic = {}
    yield "\n# LGR comparison #\n"
    for label in labels:
        label_cp = tuple([ord(c) for c in label])
        try:
            index1 = lgr_1.generate_index_label(label_cp)
        except NotInLGR:
            yield "Label {} not in LGR {}\n".format(label, lgr_1)
            continue
        try:
            index2 = lgr_2.generate_index_label(label_cp)
        except NotInLGR:
            yield "Label {} not in LGR {}\n".format(label, lgr_2)
            continue
        labels_dic[label] = (index1, index2)

    for output in _compare(labels_dic, label1_indexes, label2_indexes):
        yield output
    # output collisions
    if show_collision:
        yield "\n\n# Collisions for LGR1 #\n"
        for output in _write_complete_output(label1_indexes):
            yield output
        if show_dump:
            yield "\n# Summary for LGR1 #\n"
            for output in _full_dump(label1_indexes):
                yield output
        yield "\n\n# Collisions for LGR2 #\n"
        for output in _write_complete_output(label2_indexes):
            yield output
        if show_dump:
            yield "\n# Summary for LGR2 #\n\n"
            for output in _full_dump(label2_indexes):
                yield output


def collision(lgr, labels_input, show_dump=False, quiet=False):
    """
    Show collisions in a list of labels for a given LGR

    :param lgr: The LGR object.
    :param labels_input: The file containing the labels
    :param show_dump: Generate a full dump
    :param quiet: Do not print rules
    """
    from lgr.tools.utils import read_labels
    labels = set()
    for label, valid, error in read_labels(labels_input, lgr.unicode_database):
        if valid:
            labels.add(label)
        else:
            yield "Label {}: {}\n".format(label, error)

    # get diff between labels and variants for the two LGR
    # only keep label without collision for a full dump
    label_indexes, not_in_lgr = _generate_indexes(lgr, labels, keep=show_dump,
                                                  quiet=quiet)

    if not_in_lgr:
        yield "\n# Labels not in LGR #\n\n"
        for label_cp in not_in_lgr:
            yield "Label {}\n".format(cp_to_ulabel(label_cp))

    # output collisions
    yield "\n# Collisions #\n\n"
    for output in _write_complete_output(label_indexes):
        yield output
    if show_dump:
        yield "\n# Summary #\n\n"
        for output in _full_dump(label_indexes):
            yield output


def get_collisions(lgr, labels_input, quiet=True):
    """
    Get collisions index in a list of labels for a given LGR

    :param lgr: The LGR object
    :param labels_input: The file containing the labels
    :param quiet: Do not get rules
    :return: The indexes for collisions
    """
    from lgr.tools.utils import read_labels
    labels = set()
    for label, valid, error in read_labels(labels_input, lgr.unicode_database):
        if valid:
            labels.add(label)
    label_indexes, _ = _generate_indexes(lgr, labels, keep=False, quiet=quiet)
    return label_indexes


def is_collision(lgr, labels_input):
    """
    Check if there is a collision in a list of labels for a given LGR

    :param lgr: The LGR object
    :param labels_input: The file containing the labels
    :return: Whether there is a collision or not
    """
    return len(get_collisions(lgr, labels_input)) > 0


