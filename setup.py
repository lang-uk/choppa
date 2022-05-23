#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


requirements = ["regex"]

test_requirements = [
    # TODO: put package test requirements here
    "pytest"
]

setup(
    name="choppa",
    version="1.0.0",
    description="",
    python_requires=">=3.6",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dmitro Chaplynskyi",
    author_email="chaplinsky.dmitry@gmail.com",
    url="https://github.com/lang-uk/choppa",
    packages=[
        "choppa",
    ],
    package_dir={"choppa": "choppa"},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords="sentence tokenizer,natural language processing,srx",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries",
        "Typing :: Typed",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Natural Language :: Ukrainian",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    test_suite="tests",
    tests_require=test_requirements,
    package_data={'choppa': ['data/*.srx']},
)
