Algorithms used in LGR tools
============================

Comparison tools
----------------

These tools take 2 LGR and apply a comparison function on them: ``union``, ``intersection`` and ``difference``.
``union`` and ``intersection`` return a new LGR, while ``difference`` is a textual output (like the Unix ``diff`` command).

Note: ``Let user choose`` means that both values will be appended in the output. As the resulting LGR might then be invalid, it requires a manual edition.

* Metadata
    - Version:
        + Union: ``Let user choose``
        + Intersection: ``Let user choose``
        + Diff: Compare as string
    - Version comment:
        + Union: ``Let user choose``
        + Intersection: ``Let user choose``
        + Diff: Compare as string
    - Date:
        + Union: ``Today()``
        + Intersection: ``Today()``
        + Diff: Compare as date
    - Language:
        + Union: Keep all languages
        + Intersection: Keep common languages
        + Diff: Compare as list of strings
    - Scopes:
        + Union: Keep all scopes
        + Intersection: Keep common scopes
        + Diff: Compare as list of strings
    - Description:
        + Union: Concatenate both description
        + Intersection: ``Let user choose``
        + Diff: Compare as string
    - Description mimetag:
        + Union: ``text/plain``
        + Intersection: ``text/plain``
        + Diff: Compare as string
    - Validity start date:
        + Union: Latest value
        + Intersection: Latest value
        + Diff: Compare as string
    - Validity end date:
        + Union: Earliest
        + Intersection: Earliest
        + Diff: Compare as string
    - Unicode version:
        + Union: Latest
        + Intersection: Latest
        + Diff: Compare as string
    - References:
        + Union: Keep all references (will regenerate all ids)
        + Intersection: Intersection of strings
        + Diff: Compare as string (only for value, not id and/or comment)

* Repertoire
    - References: are dropped on all operations
    - Code point:
        + Union: Keep all code points. For code points defined in both LGRs:
            - Comments: ``Let user choose``
            - Tags: Keep all tags
            - Variants: Keep all variants, drop comments
        + Intersection: Keep code points defined in both LGRs:
            - Comments: ``Let user choose``
            - Tags: Keep tags defined in both LGR
            - Variants: Keep variants defined in both LGR (same code point, when/not-when rules), drop comments
        + Diff: List of code points defined in one LGR and not the other. For common code points:
            - Comments: Compare as strings
            - Tags: Compare as list of strings
            - Variants: Compare on code point, type, when/not-when rules and comments
    - Rules:
        + Union: Keep all rules. For rules existing in both LGRs (same name), suffix them ``_1`` and ``_2``
        + Intersection: Keep common rules (same name), suffix them ``_1`` and ``_2``
        + Diff: Compare as strings
    - Classes:
        + Union: Keep all classes. For classes existing in both LGRs (same name), suffix them ``_1`` and ``_2``
        + Intersection: Keep common classes (same name), suffix them ``_1`` and ``_2``
        + Diff: Compare as strings
    - Actions:
        + Union: Keep all actions
        + Intersection: Keep common actions (same disposition, match/not-match, any-variant, all-variants, only-variants)
        + Diff: Compare as strings


Annotate
--------

This tool takes an LGR and a list of labels and validate each of the label in the file against the LGR. The output is the list of labels annotated with their disposition.

As label validation is a process that might take a long time, the tool is asynchronous: a notification will be sent by email when the processing is done.

Collision/Diff
--------------

The outputs produced by these tools make use of terms like ``Primary`` or ``Variant``.

A ``Primary`` label is a label which is present in the input label list.
A ``Variant`` label is a variant of a label present in the input label list.

For example, given a repertoire of ``[a-z], oe, œ`` with the variant set ``oe, œ, x, y`` and the input list of labels ``oeuf œuf oeil``, the tool will detect collisions for ``oeuf`` and ``œuf`` and classify them as follows:

::

    Primary-Primary:
        oeuf-œuf
    Primary-Variant:
        oeuf-xuf
        oeuf-yuf
        œuf-xuf
        œuf-yuf
    Variant-Variant
        xuf-yuf

Collision
~~~~~~~~~

Given an LGR and a label list, the tool will:

* Generate the index of all the labels in the list (see `section 8.5 of RFC 7940`_)
* Add the index and some information related to the label to index list -> might have more than one label per index. All of these labels have a category of ``Primary``.
* For each index:
    * Take every labels associated to that index. For each label:
        * Compute all the variants of the label in the LGR. For each variant:
            * Check if variant is already in label list, or add it to the list with ``Variant`` category.
* Dump the output

As generating the labels' variants is a very expensive process, the tool is asynchronous: a notification will be sent by email when the processing is done.


Diff
~~~~

Given 2 LGR and a label list, the tool will:

* Generate the index for all labels in the list against the first LGR (same method as collision).
* Generate the index for all labels in the list against the second LGR (same method as collision).
* Compare the generated labels (and variants) for the 2 LGRs.

As generating the labels' variants is a very expensive process, the tool is asynchronous: a notification will be sent by email when the processing is done

Cross-script variants
---------------------

Given an LGR set and a label list, the tool will iterate through the label list and for each label:

* Check that the label is eligible in the merged LGR.
* Generate all the variants in the merged LGR.
* For each of the variant:
  * Retrieve the Element LGR(s) for each of their code points.
  * If the variants is composed of code points from more than one Element LGR, then it is a cross-script variant.

As generating the labels' variants is a very expensive process, the tool is asynchronous: a notification will be sent by email when the processing is done

.. _`section 8.5 of RFC 7940`: https://tools.ietf.org/html/rfc7940#section-8.5