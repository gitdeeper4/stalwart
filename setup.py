#!/usr/bin/env python3
"""Setup script for STALWART."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="stalwart",
    version="1.0.0",
    author="Samir Baladi",
    author_email="gitdeeper@gmail.com",
    description="STALWART: Sensor-Driven Predictive Framework for Structural Health Monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/gitdeeper4/stalwart",
    project_urls={
        "Documentation": "https://stalwart.readthedocs.io",
        "Source": "https://gitlab.com/gitdeeper4/stalwart",
        "Tracker": "https://gitlab.com/gitdeeper4/stalwart/-/issues",
        "DOI": "https://doi.org/10.5281/zenodo.18655299",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.9.0",
            "pre-commit>=2.0.0",
        ],
        "ml": [
            "tensorflow>=2.13.0",
            "torch>=2.0.0",
            "xgboost>=1.7.0",
        ],
        "dashboard": [
            "fastapi>=0.95.0",
            "uvicorn>=0.21.0",
            "plotly>=5.13.0",
            "dash>=2.9.0",
        ],
        "field": [
            "pyserial>=3.5",
            "smbus2>=0.4.0",
            "RPi.GPIO>=0.7.0",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Civil Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="bridge monitoring structural health aeroelastic flutter corrosion predictive maintenance",
    entry_points={
        "console_scripts": [
            "stalwart=stalwart.cli:main",
            "stalwart-monitor=stalwart.cli:monitor",
            "stalwart-analyze=stalwart.cli:analyze",
            "stalwart-dashboard=stalwart.cli:dashboard",
            "stalwart-calibrate=stalwart.cli:calibrate",
        ],
    },
)
