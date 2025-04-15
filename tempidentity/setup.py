#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tempidentity",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for generating temporary email addresses and phone numbers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tempidentity",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "colorama>=0.4.4",
        "rich>=10.0.0",
        "yaspin>=2.1.0",
    ],
    entry_points={
        "console_scripts": [
            "tempidentity=tempidentity.tempidentity:main",
        ],
    },
)
