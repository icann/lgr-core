# Changelog for lgr-core

## 5.0.0 (2022-10-26)
### New features
- Allow using pre-computed index in collision calculation
- Allow filtering mixed-script variants in variants computation
### Improvements
- Update variant index computation algorithm
- Add new general rules check in IDN tables review
- Make RFC parsers handle asymetric variants sets
- Make collision tools less verbose and display only relevant data
- Enhance collision computation performance
### Fixes
- Correctly ignore comments in RFC3743 parser

## 4.0.2 (2021-06-07)
### Fixes
- Fix RFC 3743 parsing to handle sequences

## 4.0.1 (2021-05-28)
### Fixes
- Change IDN review empty summary result status

## 4.0.0 (2021-04-27)
### New features
- Add IDN table review tool
- Add an heuristic parser for any RFC format
- Drop compatibility for Python 2.7, 3.4 and 3.5
- Add compatibility for Python 3.8
### Improvements
- Factorize and create helpers for CLI tools
- Use Suppress-Script when retrieving LGR scripts from metadata
### Fixes
- Stop considering reflexive mapping when evaluating a variant label

## 3.0.0 (2020-12-04)
### New features
- Add a way to provide a list of TLDs to collision tool
- Add new collision tool API with simplified output
- Stop support for python 2.7
### Improvements
- Improve collision tool output
### Fixes
- Handle contextual rules symmetry when populating variants
- Fix symmetry validator to keep consistency with conditional variants validator
- Fix memory leak with logs not correctly flushed
- Fix variant generation with sequences

## 2.0.1 (2019-08-01)
### New features
- Add support for LGR validation:
    - Introduce the concept of test label. Each test label has a test (i.e. a predicate on LGR files) and a human readable description.
    - Introduce the concept of policy. A policy maps test labels to values of either "IGNORED", "WARNING" or "ERROR".
    - Assign test labels to already existing tests, e.g. "valid_unicode_version" and "metadata_language".
    - Add new labelled tests, e.g. tests for the "validity-start" and "validity-end" elements.
    - Add aggregation of test results in terms of successful test labels.
    - Add a method to calculate the validation result based on policy and test results.
    - Add an RFC 7940 validation tool.
### Improvements
- Mark out-of-script codepoints as warnings instead of errors (Fixes #15).
### Fixes
- Fix processing of contextual rule without anchor (Fixes #14).

## 2.0.0 (2018-09-06)
### New features
- Support of Python 3. Compatibility with python2 is preserved for this release.
- Add tox configuration for testing multiple Python versions (2.7 and 3.X).
- Add MSR-3 validating repertoire.
- Delete a tag from the LGR.
- Check id format when adding reference.
### Improvements
- Update harmonization tool.
- Better error reporting for CharInvalidContextRule.
- Collision-based tools do not stop at the first label not in the LGR.
- Include invalid variants in x-script variants.
- Add missing language exception in order to clarify cross script variant tool output.
- Remove label length limits based on heuristic by method that computes estimated number of variants.
- Make description of LGR union as text/html.
- Force inclusion of invalid code points when rebuilding LGR.
- Remove script parameter from harmonization function.
- Display rule name(s) when a code point does not comply with a contextual rule.
- Better notification for invalid language tags.
### Fixes
- Remove code points from tag-based classes on deletion.
- Replace number of variants by number of variant mappings in LGR validation statistics.
- Add 'blocked' type to tools that add variants.
- Update make_idna_repertoire to handle IDNA tables <= 6.0.0.
- In union comparison and intersection tools, do not duplicate rules, classes and actions.
- Add missing variants in LGR union.
- Workaround a libxml2 bug that do not normalize EOL in CDATA.

## 1.9 (2018-03-09)
New features:
- New tool to check that multiple LGRs are harmonized.
- New function to populate the missing symmetric and transitive variants.
Fixes:
- Validate that a generated variant label is valid based on LGR rules.
- Reduce verbosity of lgr\_compare's diff output
- Improve handling of large LGR.
- Improve display for summary (now renamed to LGR validation).
- Fix generation of prefix list with a code point sequence and look-around rule.

## 1.8.1 (2017-11-15)
Fixes:
 - Remove script/mimetype from merged description when all descriptions use the text/html mimetype.
 - Fix cross-script variants tool: output variants composed of code point which are in other scripts
   than the one(s) defined in the LGR.

## 1.8 (2017-10-18)
Fixes:
 - Merge LGR containing the same code point.
 - Improve HTML formatting for description in HTML output.
 - Improve merge for metadata's description element: if all descriptions are using HTML, then output will be in HTML.
 - Include references in WLE table in HTML output.
 - Better display of regex for WLE in HTML output.
 - Order metadata section per language then per script.
 - Fix size of variant set in HTML output.
 - Download result links are now ordered with newest on top.
 - Emphasize that the "Allocated set labels" file is optional.
 - Fix typo on homepage.
 - Update links to published RFC.
 - Allow import of an LGR part of a set as a standalone LGR.
 - Improve cross-script variants tool: generate the variants using the merged LGR,
   and list element LGRs used by the variants' code points.
 - Use redis as default Celery's broker for better stability.

## 1.7 (2017-06-26)
New features:
 - Handling of LGR sets: import multiple LGR documents to create a set (merged LGR).
 - Update difference and annotation tools to process LGR sets.
 - New tool to list cross-script variants for LGR sets.
 - HTML output of LGR: render LGR (or LGR set) in an HTML page.

Fixes:
 - Update dispositions to RFC: default for variants is "blocked", update default rules.
 - Improve design of homepage.
 - 500 error when clicking on a code point's variant that is not in LGR.
 - Fix Dockerfile: follow redirects for ICU downloads, add SHA-sum checks.

## 1.6 (2016-06-16)
Fixes:
 - Fix disposition handling in collision and diff tools
 - Improve tools error description provided in e-mail
 - Improve tools output
 - Manage bidirectional text in tools output
 - Improve tools performance

## 1.5 (2016-06-03)
New features:
 - Add cancel button on metadata screen                             
 - Add a list of current and imported LGRs into import/new panels         
 - Add supported Unicode version in about page  
 - Add an annotation tool
 - Add a checkbox to limit rules output in tools
 - Save tools output on server and display download link in session
 - Add a management command to clean storage
 - Some comparison leads to invalid LGR, return a download link for user to fix it

Fixes:
 - Fix manual import of RFC3743
 - Fix error field position in "Import CP from file" screen         
 - Improve code point details view
 - Various fixes in union and intersection
 - Various fixes in variant generation
 - Various display improvements
 - Limit logging output
 - Update RNG file
 - Various code factorization

## 1.4 (2016-04-27)
New features:
- Add documentation for core API and web-application global design.
- New tool for computing label collisions with two versions of an LGR.
  Add asynchronous interface for users to submit their requests
  and get result by email.

Fixes:
- Update RNG file to last version.
- Enable definition of when/not-when attribute on range.

## 1.3 (2016-03-02)
Fixes:
- Fix processing of look-around when anchor code point was repeated.
- Fix processing of infinite look-behind rules.
- Fix range expansion references.
- Correctly process variant label in context rule.
- Catch regex exceptions.
- Fix WLE validation.
- Handle empty set/pattern in WLE processing.
- Ensure label is in LGR when computing variants when dealing with sequences.
- When/Not-when attributes are mutually exclusive.
- Fix count attributes on char match operator.
- Fix class combinations for intersection and symetric-difference.
- Update RNG file.
- Make the title more clear to be clickable as « home »
- Correctly include Docker configuration.

## 1.2 (2016-02-05)
New features:
- WLE rules editor.
- Tag edition on code points.
- Context rules selection on code points.
- Expand ranges to single code point.
- New LGR comparison application:
	- Union of 2 LGRs.
	- Intersection of 2 LGRs.
	- Diff (text output) of 2 LGRs.
- Save summary to file.
- Delete LGR from working session.
- Add Dockerfile.
- Update namespace: imported LGRs will be converted to new namespace on export.

Fixes:
- Disable external entities when parsing XML (security review report).
- Properly handle IDNA errors in label validation.
- Import variants when manually importing from RFC file.
- Fix label variants generation when context rules are used.
