#!/usr/bin/env python3

from setuptools import setup

setup(name='ticketmanager',
      version='0.1',
      description='Shows the dates when you are ticketmanager and tells you \
                   if this day is today',
      author='ngrande',
      packages=['ticketmanager'],
      install_requires=['bs4', 'aiohttp'],
      scripts=['who_is_ticketmanager'])
