#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'six',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pignacio_scripts',
    version='0.0.2',
    description="Reusable python scripts and snippets I find useful",
    long_description=readme + '\n\n' + history,
    author="Ignacio Rossi",
    author_email='rossi.ignacio@gmail.com ',
    url='https://github.com/pignacio/pignacio_scripts',
    packages=[
        'pignacio_scripts',
    ],
    package_dir={'pignacio_scripts':
                 'pignacio_scripts'},
    include_package_data=True,
    install_requires=requirements,
    license='LGPLv2.1',
    zip_safe=False,
    keywords='pignacio_scripts',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
