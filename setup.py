import re
from setuptools import setup, find_packages

with open("README.md", mode="r", encoding="utf-8") as f:
    readme = f.read()

# parse the version instead of importing it to avoid dependency-related crashes
with open("src/__version.py", mode="r", encoding="utf-8") as f:
    line = f.readline()
    __version__ = line.split("=")[1].strip(" '\"\n")
    assert re.match(r"^\d+(\.\d+){2}(-(alpha|beta|rc)(\.\d+)?)?$", __version__)

test_requirements = [
    "appdirs",
    "bandit",
    "black",
    "codecov",
    "daiquiri",
    "flake8",
    "pylint",
    "pytest-cov>=2.5.1",
    "pytest-mock",
    "pytest>=4.0.0",
    "pyyaml",
]

setup(
    name="yamlike",
    version=__version__,
    description="Parser for a tiny subset of YAML",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Simon Larsén",
    author_email="slarse@slar.se",
    url="https://github.com/slarse/yamlike",
    download_url=(
        "https://github.com/slarse/yamlike/archive/v{}.tar.gz".format(
            __version__
        )
    ),
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=("tests", "docs")),
    py_modules=["yamlike"],
    tests_require=test_requirements,
    extras_require=dict(TEST=test_requirements),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: Windows",
    ],
)
