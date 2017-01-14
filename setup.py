#!/usr/bin/env python

# Standard library modules.
import os

# Third party modules.
from setuptools import setup, find_packages

# Local modules.
import versioneer

# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

PACKAGES = find_packages()
INSTALL_REQUIRES = ['python-debian',
                    'chardet', # Uncovered dependency of python-debian
                    'deb_pkg_tools',
                    'requests',
                    'beautifulsoup4']

CMDCLASS = versioneer.get_cmdclass()

setup(name="pymontecarlo-debian",
      version=versioneer.get_version(),
      url='https://github.com/pymontecarlo/pymontecarlo-debian',
      description="Create DEB for Monte Carlo programs",
      author="Philippe T. Pinard",
      author_email="philippe.pinard@gmail.com",
      license="Apache License, Version 2.0",
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: Apache Software License',
                   'Natural Language :: English',
                   'Programming Language :: Python :: 3 :: Only',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Physics'],

      packages=PACKAGES,

      cmdclass=CMDCLASS,

      setup_requires=['nose'],
      install_requires=INSTALL_REQUIRES,

      test_suite='nose.collector',
)

