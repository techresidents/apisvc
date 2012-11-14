#!/usr/bin/env python

from distutils.core import setup

setup(name='trapisvc',
      version='${project.version}',
      description='Tech Residents Service',
      packages=['trapisvc',
                'trapisvc.gen']
    )

