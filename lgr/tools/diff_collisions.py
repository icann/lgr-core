# -*- coding: utf-8 -*-
"""
diff_collisions.py - Diff and collisions of labels
"""
from __future__ import unicode_literals

from collections import Counter
from copy import deepcopy
from typing import List

from lgr.exceptions import InvalidSymmetry, NotInLGR
from lgr.utils import format_cp, cp_to_ulabel

MD = "\n```\n"

LRI = '\u2066'
PDI = '\u2069'

PRIMARY = 'Primary'
VARIANT = 'Variant'
TLD = 'TLD'


def _compute_indexes(lgr, label_list, is_tld=False):
    for label in label_list:
        label_cp = tuple([ord(c) for c in label])
        try:
            label_index = lgr.generate_index_label(label_cp)
        except NotInLGR:
            if is_tld:
                continue
            yield label, label_cp, 'NotInLGR'
            continue

        yield label, label_cp, label_index


def _get_cached_indexes(index_list):
    for label, label_index in index_list.items():
        label_cp = tuple([ord(c) for c in label])
        yield label, label_cp, label_index


def _generate_indexes(lgr, labels: List, tlds=None, keep=False, quiet=False, cached_indexes=None):
    """
    Generate indexes based on labels provided in the list

    :param lgr: The current LGR
    :param labels: The list of labels, as a list of U-Labels.
    :param tlds: The list of TLDs
    :param keep: Do we keep labels without collision in the output
    :param quiet: If True, do not collect rule log.
    :param cached_indexes: The list of indexes already computed

    :return: (label_indexes, not_in_lgr), with:
              - label_indexes: the dictionary containing the primary labels
                               and their variants (with various information) for each index.
              - not_in_lgr: List of labels that do not pass preliminary eligibility testing.
  """

    label_indexes = {}
    not_in_lgr = []

    # Get the indexes and variants for all labels
    def _get_indexes(label_list, is_tld=False, is_cache=False):
        generator = _get_cached_indexes
        generator_args = [label_list]
        if not is_cache:
            generator = _compute_indexes
            generator_args = [lgr, label_list, is_tld]

        for l, l_cp, l_idx in generator(*generator_args):
            if isinstance(l_idx, str):
                if l_idx == 'NotInLGR':
                    not_in_lgr.append(l)
                continue

            label_cp_out = format_cp(l_cp)
            if l_idx not in label_indexes:
                label_indexes[l_idx] = []
            label_indexes[l_idx].append({'label': l,
                                         'bidi': "%s'%s'%s" % (LRI, l, PDI),
                                         'cat': PRIMARY if not is_tld else TLD,
                                         'cp': l_cp,
                                         'cp_out': label_cp_out,
                                         'disp': {l: '-'},
                                         'rules': {l: '-'},
                                         'action_idx': {l: '-'},
                                         'index': l_idx
                                         })

    _get_indexes(labels)
    if cached_indexes:
        _get_indexes(cached_indexes, is_cache=True)
    if tlds:
        # remove labels from tlds as we do not want duplicated in label_indexes lists
        _get_indexes(tlds - set(labels), is_tld=True)

    for (label_index, primaries) in deepcopy(label_indexes).items():
        # only get variants for collided labels (if not keep)
        if len(primaries) < 2 and not keep:
            del label_indexes[label_index]
            continue
        if not keep and quiet:
            continue
        for primary in primaries:
            label_cp = primary['cp']
            label = primary['label']
            for (variant_cp,
                 variant_disp,
                 variant_invalid_parts,
                 action_idx, _,
                 log) in lgr.compute_label_disposition(label_cp,
                                                       include_invalid=True,
                                                       collect_log=not quiet,
                                                       with_labels=[l['cp'] for l in primaries] if not keep else None):
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


def dump_collisions(colliding1, cb, colliding2=None, **kwargs):
    idx = 0
    list2 = colliding2
    for l1 in colliding1:
        idx += 1
        if list2 is None:
            # do not display the same collision permuted
            list2 = colliding1[idx:]
        for l2 in list2:
            if l1 != l2:
                yield cb(l1, l2, **kwargs)


def _write_complete_output(labels, label_indexes, tlds=None):
    """
    Output the collisions information between labels
    :param label_indexes: the dictionary containing the primary labels and
                          their variants (with various information) for each index.
    """
    output_labels = ("\n### Collision within the {col} ###\n" + MD +
                     "Label:       \t{label:{len}}   | {variant}\n"
                     "Code points: \t{label_cp:{len}} | {variant_cp}\n"
                     "Category:    \t{label_cat:{len}} | {variant_cat}" +
                     MD)

    def print_collision(label, variant):
        return output_labels.format(col='existing TLDs' if TLD in [label['cat'], variant['cat']] else 'input file',
                                    label="%s" % label['bidi'],
                                    variant="%s" % variant['bidi'],
                                    label_cp="[%s]" % label['cp_out'],
                                    variant_cp="[%s]" % variant['cp_out'],
                                    label_cat=label['cat'],
                                    variant_cat=variant['cat'],
                                    len=max(len(label['label']),
                                            len(label['cat']),
                                            len(label['cp_out'])) + 2)

    collided = False
    tlds = tlds or set()
    for idx, collisions in label_indexes.items():
        yield f"\n## Index '{cp_to_ulabel(idx)}' ##\n"
        colliding_labels = [l for l in collisions if l['label'] in labels]
        colliding_tlds = [l for l in collisions if l['label'] in tlds]

        # do not output anything if there is not at least 2 primaries colliding
        if len(colliding_labels) > 1:
            collided = True
            for col in dump_collisions(colliding_labels, print_collision):
                yield col

        if colliding_tlds:
            for col in dump_collisions(colliding_labels, print_collision, colliding2=colliding_tlds):
                yield col

    if not collided:
        yield MD
        yield "No collision in the list of labels"
        yield MD


def _write_simple_output(labels, tlds, label_indexes):
    """
    Output the collisions between labels
    :param label_indexes: the dictionary containing the primary labels and
                          their variants (with various information) for each index.
    """

    def print_collision(l1, l2, label_type):
        return f'{l1}: collides with {label_type} {l2}\n'

    for collisions in label_indexes.values():
        colliding_labels = list(labels.intersection(set([l['label'] for l in collisions])))
        colliding_tlds = list(tlds.intersection(set([l['label'] for l in collisions])))
        if len(colliding_labels) > 1:
            for col in dump_collisions(colliding_labels, print_collision, label_type="label"):
                yield col

        if colliding_tlds:
            for col in dump_collisions(colliding_labels, print_collision, colliding2=colliding_tlds, label_type="TLD"):
                yield col


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
            for label in not_in_lgr:
                yield "Label {}\n".format(label)
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
        for output in _write_complete_output(labels, label1_indexes):
            yield output
        if show_dump:
            yield "\n# Summary for LGR1 #\n"
            for output in _full_dump(label1_indexes):
                yield output
        yield "\n\n# Collisions for LGR2 #\n"
        for output in _write_complete_output(labels, label2_indexes):
            yield output
        if show_dump:
            yield "\n# Summary for LGR2 #\n\n"
            for output in _full_dump(label2_indexes):
                yield output


def _read_tlds(lgr, tlds_input):
    from lgr.tools.utils import read_labels

    tlds = set()
    errors = []
    for label, valid, error in read_labels(tlds_input, lgr.unicode_database):
        if valid:
            tlds.add(label)
        else:
            errors.append("TLD {}: {}\n (WARNING: this should not append, your TLD file may be corrupted)".format(
                label, error))
    return tlds, errors


def collision(lgr, labels_input, tlds_input, show_dump=False, quiet=True):
    """
    Show collisions in a list of labels for a given LGR

    :param lgr: The LGR object.
    :param labels_input: The file containing the labels
    :param tlds_input: The file containing the TLDs
    :param show_dump: Generate a full dump
    :param quiet: Do not print rules
    """
    from lgr.tools.utils import read_labels
    labels = dict()  # use dict to keep order
    for label, valid, error in read_labels(labels_input, lgr.unicode_database):
        if valid:
            labels[label] = None
        else:
            yield "Label {}: {}\n".format(label, error)

    tlds = None
    if tlds_input:
        tlds, errors = _read_tlds(lgr, tlds_input)
        for err in errors:
            yield err

        in_tld = labels.keys() & tlds
        if in_tld:
            yield "\n# Labels that are TLDs #\n\n"
            for label in sorted(in_tld):
                yield "Label {}\n".format(label)

    # only keep label without collision for a full dump
    label_indexes, not_in_lgr = _generate_indexes(lgr, list(labels.keys()), tlds=tlds, keep=show_dump, quiet=quiet)

    if not_in_lgr:
        yield "\n# Labels not in LGR #\n\n"
        for label in sorted(not_in_lgr):
            yield "Label {}\n".format(label)

    # output collisions
    yield "\n# Collisions #\n\n"
    for output in _write_complete_output(labels, label_indexes, tlds=tlds):
        yield output
    if show_dump:
        yield "\n# Summary #\n\n"
        for output in _full_dump(label_indexes):
            yield output


def basic_collision(lgr, labels_input, tlds_input, with_annotations=False):
    """
    Show collisions in a list of labels for a given LGR with no information

    :param lgr: The LGR object.
    :param labels_input: The file containing the labels
    :param tlds_input: The file containing the TLDs
    :param with_annotations: Add label annotation
    """
    from lgr.tools.utils import read_labels
    from lgr.tools.annotate import annotate

    if with_annotations:
        yield "# Validity #\n\n"
        for res in annotate(lgr, deepcopy(labels_input)):
            yield res
        yield "\n"

    label_errors = []
    labels = set()
    for label, valid, error in read_labels(labels_input, lgr.unicode_database):
        if valid:
            labels.add(label)
        else:
            label_errors.append("{}: {}".format(label, error))

    tlds, errors = _read_tlds(lgr, tlds_input)
    for err in errors:
        yield err

    yield "# Collisions #\n\n"
    has_one = False
    if tlds_input:
        in_tld = labels & tlds
        for label in sorted(in_tld):
            has_one = True
            yield "{}: is a TLD\n".format(label)

    # only keep label without collision for a full dump
    label_indexes, not_in_lgr = _generate_indexes(lgr, labels, tlds=tlds, keep=False, quiet=True)

    label_not_in_lgr = []
    if not_in_lgr:
        for label in sorted(not_in_lgr):
            label_not_in_lgr.append("{}: not in LGR".format(label))

    # output collisions
    for output in _write_simple_output(labels, tlds, label_indexes):
        has_one = True
        yield output

    if not has_one:
        yield "No collision\n"

    if label_errors or label_not_in_lgr:
        yield "\n# Errors #\n\n"
        for error in label_errors:
            yield error + '\n'

        for not_in_lgr in label_not_in_lgr:
            yield not_in_lgr + '\n'


def get_collisions(lgr, labels_input, quiet=True, cached_indexes=None):
    """
    Get collisions index in a list of labels for a given LGR

    :param lgr: The LGR object
    :param labels_input: The file containing the labels
    :param quiet: Do not get rules
    :param cached_indexes: The list of indexes already computed
    :return: The indexes for collisions
    """
    from lgr.tools.utils import read_labels
    labels = set()
    for label, valid, error in read_labels(labels_input, lgr.unicode_database):
        if valid:
            labels.add(label)
    label_indexes, _ = _generate_indexes(lgr, labels, keep=False, quiet=quiet, cached_indexes=cached_indexes)
    return label_indexes
