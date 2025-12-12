#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

with open("README.md") as fp:
    long_description = fp.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="pomegranate",
    version='0.1',
    url="https://github.com/spiros/pomegranate",
    author="Spiros Denaxas",
    author_email="s.denaxas@ucl.ac.uk",
    keywords="electronic health records, uk biobank, phenotyping",
    description="Package creating and evaluating phenotypes in the UK Biobank",
    long_description=long_description,
    license="Other",
    entry_points = {
        'console_scripts': [
            'build_yaml = pomegranate.cli.build_yaml:main',
            # ETL:
            'extract_phenotype = pomegranate.cli.etl.extract_phenotype:main',
            'extract_complex_phenotype = pomegranate.cli.etl.extract_complex_phenotype:main',
            'extract_exacerbations = pomegranate.cli.etl.extract_exacerbations:main',

        ],
    },
    packages=find_packages(exclude=["code", "docs", "tests", "documentation", "python", "website"]),
    python_requires='>=3.6',
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "License :: Other/Proprietary License",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.6",
    ],
    zip_safe=False,
    include_package_data=True,
    package_data={
        'pomegranate.data.catalogue': ['*.gz', '*.csv', '*.tsv'],
        'pomegranate.data.lookups': ['*.gz', '*.csv', '*.tsv']
    },
    install_requires=requirements,
)
