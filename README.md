# LGR Core library

Core library and LGR data structure used to manipulate an LGR.

This version conforms to the specification [RFC7940](https://www.rfc-editor.org/rfc/rfc7940.txt).

## Acknowledgment

This library was implemented by Viagenie (Julien Bernard, Michel Bernier, Guillaume Blanchet,
Marc Blanchet, Vincent Gonzalez, Audric Schiltknecht and Alexandre Taillon-Desrochers) 
and Wil Tan on an ICANN contract.



## License

Copyright (c) 2015-2020 Internet Corporation for Assigned Names and
Numbers (“ICANN”). All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

    * Neither the name of the ICANN nor the names of its contributors
      may be used to endorse or promote products derived from this
      software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY ICANN AND CONTRIBUTORS ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ICANN OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
THE POSSIBILITY OF SUCH DAMAGE.

## Pre-Requisites

* Python 3.6 and above
* [LibXML2](http://www.xmlsoft.org/) [MIT License] used by the lxml Python bindings

### Python Dependencies

#### Main Dependencies

The main dependencies are defined in the [requirements.txt](requirements.txt) file.

* [language-tags](https://github.com/OnroerendErfgoed/language-tags) [MIT License]
* [lxml](http://lxml.de/) [BSD License]
* [munidata](https://github.com/icann/munidata) for Unicode-related properties access [BSD License]
* [picu](https://pypi.python.org/pypi/picu) [MIT/X License]
* [pycountry](https://github.com/flyingcircusio/pycountry) [L-GPL License]

#### Testing Dependencies

The dependencies to run the test suite are defined in the [tests requirements.txt](tests/requirements.txt).

* [idna](https://github.com/kjd/idna) [BSD License]
* [pytest](https://docs.pytest.org/en/stable/) [MIT License]
* [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) [MIT License]

#### Documentation Dependencies

The dependencies to build the documentation are defined in the [doc requirements.txt](doc/requirements.txt) file.

* [Graphviz](http://www.graphviz.org/) [Eclipse Public License]
* [pylint](https://pylint.pycqa.org/en/latest/index.html) [GNU GPL License]
* [Sphinx](https://www.sphinx-doc.org/en/master/) [BSD License]

## Virtual Environment setup

If your distribution does not package the required dependencies, the easiest way
to get a working environment in no-time is to use Python's virtual environments.

* Install [virtualenv](https://github.com/pypa/virtualenv)
* Create a python virtualenv:

		$ virtualenv venv

* Activate the environment:

		$ source ./venv/bin/activate

* Download dependencies:

		(venv) $ pip install -r requirements.txt

## Tools

The `tools` directory contains some tools to exercise the library.

* `xml_dump.py` parses an XML LGR file, creates the LGR structure, and convert
  it back to XML.
* `make_idna_repertoire.py` generates the IDNA2008 starting repertoire, by
  parsing the [IDNA2008 table registry](http://www.iana.org/assignments/idna-tables/idna-tables.xhtml)
  available on IANA website, and collecting all `PVALID`, `CONTEXTO` and `CONTEXTJ` characters.
* `lgr_cli.py` parsed an XML LGR file, and validate it against configured MSR
  and Unicode version.
* `rfcXXXX_dump.py` parses inputs in RFC XXXX format, and generate an XML LGR.
* `one_per_line_dump.py` parses input in the "one per line" format, and generate an XML LGR.
* `rfc7940_validate.py` takes an LGR and checks it for compliance with RFC 7940.

Other tools are available to manipulate LGR files and labels:
* `lgr_annotate.py` takes an LGR and a list of labels and output
  the list of labels with their respective disposition.
* `lgr_collision.py` takes an LGR and a list of labels and check
  for collision(s) between the labels/variants.
* `lgr_compare.py` is used to compare 2 LGR (output textual diff, merge, intersection).
* `lgr_diff_collision.py` takes 2 LGR and one set of labels,
  and test for collisions between labels and generated variants from the 2 LGR.
* `lgr_merge_set.py` takes some LGRs and create a merged LGR from the provided set.
* `lgr_check_harmonized` checks that variants code points from a list of LGRs are symmetric and transitive in each LGR,
  and list missing variants from one LGR to another.
* `lgr_cross_script_variants` takes some LGRs and generate the list of cross-script variants.
* `lgr_idn_table_review.py` reviews IDN tables against reference LGRs.

## Testing and coverage

Tests and coverage report can be run as follows:

	(venv) $ pip install pytest pytest-cov
	(venv) $ ./runtests.sh

Open `htmlcov/index.html` in a web browser for the coverage report.

## Documentation

To generate the documentation, go to the `doc` directory and run the following command:

	(venv) $ make html

The generated documentation is available in `doc/_build/html/index.html`.
