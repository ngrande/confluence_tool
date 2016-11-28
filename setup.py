#!/usr/bin/env python3

from setuptools import setup

setup(name='ticketmanager',
      version='0.1',
      description='Provides an interface to query information from a \
      confluence website (especially to get the ticketmanager timetable data)',
      author='ngrande',
      author_email='devlup@outlook.com'
      packages=['ticketmanager'],
      install_requires=['bs4', 'aiohttp'],
      scripts=['who_is_ticketmanager'])
