"""setuptools entry point."""

from codecs import open
from os import path
from setuptools import find_packages, setup

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, "README.rst"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

with open(path.join(HERE, "src", "den", "VERSION")) as version_file:
    VERSION = version_file.read().strip()

setup(
    name="den",
    version=VERSION,
    description="Den is a home for your Nest thermostat data.",
    long_description=LONG_DESCRIPTION,
    author="Kris Molendyke",
    author_email="kris@k20e.com",
    url="https://git.io/k20e",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5"
    ],
    keywords="nest thermostat smoke alarm camera",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "influxdb",
        "python-forecastio",
        "requests"
    ],
    extras_require={
        "dev": [
            "yapf",
        ],
        "doc": [
            "Sphinx",
            "alabaster",
            "sphinx-argparse",
            "sphinx-autobuild",
        ],
        "notebook": [
            "jupyter",
        ],
        "test": [
            "coverage",
            "prospector",
            "mock",
            "responses",
        ],
    },
    package_data={},
    include_package_data=True,
    data_files=[],
)
