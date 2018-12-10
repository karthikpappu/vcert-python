#!/usr/bin/env python

from setuptools import setup


setup(name='vcert-python',
      version='0.0.1',
      url="https://github.com/Venafi/vcert-python",
      packages=['vcert'],
      modules=['vcert'],
      install_requires=['requests'],
      description='Python bindings for Venafi TPP/Venfi Cloud API.',
      author='Denis Subbotin',
      author_email='denis.subbotin@venafi.com',
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Operating System :: OS Independent',
      ])
