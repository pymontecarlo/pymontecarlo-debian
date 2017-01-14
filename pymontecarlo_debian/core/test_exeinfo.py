#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os

# Third party modules.

# Local modules.
from pymontecarlo_debian.core.exeinfo import extract_exe_info

# Globals and constants variables.

class Testexeinfo(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testextract_exe_info(self):
        filepath = os.path.join(os.path.dirname(__file__), 'sigcheck.exe')
        info = extract_exe_info(filepath)

        self.assertEqual('2.03', info['Prod version'])
        self.assertEqual('Microsoft Corporation', info['Publisher'])

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
