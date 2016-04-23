#!/usr/bin/env python

from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session=False)

reqs = [str(ir.req) for ir in install_reqs]

setup(name='Know-SQL',
      version='0.1',
      description='Tiny Postgres HTTP JSON gateway',
      author='Michel Pelletier',
      url='https://github.com/michelp/know-sql',
      install_requires=reqs,
     )
