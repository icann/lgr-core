This directory contains test cases.

They are divided into two classes:
	* unit test cases, to validate small portion (specific functions,
	  etc) of the code.
	* functional test cases, to validate API in general.

To run a test:

$ PYTHONPATH=.. python2 unit/test_lgr_core.py

To run all tests, use the runtest.sh script located in the top directory.