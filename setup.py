#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="unball",
    version="0.0.1",
    description="UnBall VSSS components",
    author="UnBall",
    packages=find_packages(),  # This will find all packages including VisionClient and SimulatorClient
    install_requires=["protobuf==3.20.3"],
)