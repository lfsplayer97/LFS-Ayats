"""
LFS-Ayats: Live for Speed InSim Telemetry System
Setup configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="lfs-ayats",
    version="0.1.0",
    author="lfsplayer97",
    description="Modular telemetry system for Live for Speed using InSim",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lfsplayer97/LFS-Ayats",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment :: Simulation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.3.0",
            "flake8>=6.0.0",
            "pylint>=2.17.0",
            "mypy>=1.3.0",
        ],
        "test": [
            "pytest>=7.3.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lfs-ayats=src.main:main",
        ],
    },
)
