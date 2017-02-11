#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

long_description = "Behavioral conditioning with mice"


setup(
    name='pymouse',
    version='0.1.dev1',
    description="State system for mouse behavior",
    long_description=long_description,
    author='Emmanouil Froudarakis',
    author_email='froudara@bcm.edu',
    license="GNU LGPL",
    url='https://github.com/olakiril/PyMouse',
    keywords='mouse behavior control',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['numpy', 'concurrent', 'pygame', 'imageio', 'datajoint'],
    classifiers=[
        'Development Status :: 1 - Beta',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU LGPL',
        'Topic :: Database :: Front-Ends',
    ]
)
