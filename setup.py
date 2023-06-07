# -*- coding: utf-8 -*-
"""
@author: 
    Lorenzo Rinaldi, Department of Energy, Politecnico di Milano, Italy
"""

from setuptools import find_packages, setup

setup(
    name="ieastats",
    description=(
        "A class to read IEA balances in Excel and rearrange them in supply-use format"
    ),
    url="https://github.com/LorenzoRinaldi/IEA-py",
    author="Lorenzo Rinaldi",
    author_email="lorenzo.rinaldi@polimi.it",
    version="0.1.0",
    packages=find_packages(),
    license="GNU General Public License v3.0",
    #python_requires=">.3.7.0",
    package_data={"": ["*.txt", "*.dat", "*.doc", "*.rst","*.xlsx"]},
    install_requires=[
        "mariopy >= 0.1.0",
        ],
    )