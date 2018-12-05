import os
import codecs
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


long_description = read('README.md')

setup(
    name="edl-cr",
    version="0.0.3.2",
    description="A CLI tool to run code",
    long_description=long_description,
    long_description_content_type="text/markdown",

    license="Apache-2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
    ],
    url="https://github.com/eXceediDeaL/edl-coderunner",
    project_urls={
        "Bug Tracker": "https://github.com/eXceediDeaL/edl-coderunner/issues",
        "Documentation": "https://github.com/eXceediDeaL/edl-coderunner/wiki",
        "Source Code": "https://github.com/eXceediDeaL/edl-coderunner",
    },
    keywords="code runner",

    author="eXceed-iDeaL",
    author_email="exceedideal@163.com",

    package_dir={"": "src"},
    packages=find_packages(
        where="src",
        exclude=[],
    ),
    entry_points={
        "console_scripts": [
            "ecr = ecr.__main__:outmain",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.7',
    install_requires=[
        "prompt_toolkit>=2.0.7",
        "click>=7.0",
        "watchdog>=0.9.0",
        "pygments>=2.2.0",
        "PyYAML>=3.13"
    ]
)
