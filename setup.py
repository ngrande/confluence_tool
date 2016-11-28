#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    readme = f.read()

with open('LICENSE', 'r') as f:
    license = f.read()

setup(name='ticketmanager',
      version='0.0.1',
      description='Provides an interface to query information from a \
      confluence website (especially to get the ticketmanager timetable data)',
      long_description=readme,
      author='Niclas Grande',
      license=license,
      author_email='devlup@outlook.com',
      url='https://github.com/ngrande/confluence_tool',
      packages=find_packages(exclude=('tests', 'docs')),
      install_requires=['bs4', 'aiohttp'],
      scripts=['who_is_ticketmanager'])
