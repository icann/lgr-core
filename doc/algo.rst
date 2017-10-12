Algorithms used in LGR tools
============================

Label validation for LGR set
----------------------------

The following steps are done to process a label in a LGR set context:

* First, verify that a proposed label is valid by processing it with the Element LGR corresponding to the script that was selected for the label in the application.
If the label has 'invalid' disposition then processing is stopped.
* Second, process the now validated label against the common LGR to verify it does not collide with any existing delegated labels (and any of their variants, whether blocked or allocatable).
If a collision is found then processing is stopped.
* Third, now that the label is known to be valid, and not in collision, use the appropriate element LGR to generate all allocatable variants.

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

Merge Element LGRs
------------------

Given a list of Element LGR, the tool will create a merged LGR.

The merged LGR will contain all the repertoire from the Element LGRs and all the individual Whole Label Evaluation (WLE)
rules from the Element LGRs.

The following modifications are applied while merging the Element LGR:
 - the variant mapping is be the union of the variant mappings from the Element LGRs,
 - all variant allocations are marked as blocked as variants disposition is specific for each script,
 - the default rules and actions defined in MSR-2 are annotated in the merged LGR with the prefix "Common-",
 - the rules, tags and character classes defined by an Element LGR are prefixed with the script code for this LGR separated
   by "-",
 - all repertoire code points are tagged with their script extensions values,
 - actions are merged, preserving their order of precedence.

In case of a code point present in more than one LGR, the following rules are applied:
 - merged code point gets an union of tags, references and variants and a concatenated comment,
 - transitivity with variants
   (i.e. if b is variant of a in LGR 1, c is variant of a in LGR 2: set b as c variant and conversely),
 - if the code point is affected by a when rule in one Element LGR:

   - if the code point has no when rule of the same type in the other LGR, keep the when rule on the code point
     (if the when / not-when rules are complementary between the LGRs an error will be raised as a code point cannot get
     both when and not-when rules),

     .. code-block:: xml

       <char cp="0061" when="rule1" /> <!-- script sc1 -->
       <char cp="0061" />

     will be merged as:

     .. code-block:: xml

       <char cp="0061" when="sc1-rule1" />

   - if the code point has the "same" when rule ("same" means with the same name and same kind (when or not-when),
     the content of the rule is not  actually analyzed), prefix the when rule with the script code for both LGR,

     .. code-block:: xml

       <char cp="0061" when="rule1" /> <!-- script sc1 -->
       <char cp="0061" when="rule1" /> <!-- script sc2 -->

     will be merged as:

     .. code-block:: xml

       <char cp="0061" when="sc2-sc1-rule1" />

   - if the code point has a "different" when rule of the same kind ("different" means with a different name), return a
     duplicated code point exception.
