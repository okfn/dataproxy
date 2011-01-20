from setuptools import setup, find_packages

import sys, os

version = '0.1.0'
sys.path.insert(0, 'dataproxy')

from app import __doc__ as long_description

setup(
    name='dataproxy',
    version=version,
    description="A (JSONP) dataproxy",
    long_description=long_description,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        #'Environment :: Web Environment',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python',
    ],
    keywords='',
    author='James Gardner, Stefan Urbanek, Rufus Pollock',
    author_email='ckan@okfn.org',
    url='http://ckan.org/wiki/Extensions',
    license='GNU AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'example', 'test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    extras_require={
        'test': [],
    },
    entry_points="""
    """,
)
