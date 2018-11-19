# edl-cr

[![](https://img.shields.io/badge/edl--cr-vFirst-blue.svg)](https://pypi.org/project/edl-cr/) ![](https://img.shields.io/badge/license-Apache--2.0-blue.svg) [![](https://api.travis-ci.org/eXceediDeaL/edl-coderunner.svg?branch=master)](https://exceedideal.github.io/edl-coderunner/) ![](http://progressed.io/bar/30?title=developing)

A CLI tool to run code.

# Install

Use `pip` to install edl-cr.

```sh
pip install edl-cr
```

# Usage

Use command `ecr` to run edl-cr.

## CLI Mode

|Option|Description|
|-|-|
|`-w --wdir`|Set working directory|
|`-c --command`|Execute command just like in interactive mode|

## Interactive Mode

If you don't use `--command` options, edl-cr will run in interactive mode.

### Initialize

```sh
> init
```

Initialize ECR data. It will create a directory named `.ecr` in current directory.

If you want to clear ECR data, use this command:

```sh
> clear
```

### Create and Run

Create a new code file:

```sh
> new a.cpp
```

It will use code template in `.ecr/templates/` to create file and set current file with the new file.

If you want to set current file with a existed file, use this:

```sh
> now a.cpp
```

Then use `run` command to run code.

```sh
# run a.cpp
a.cpp> run

# run b.cpp
a.cpp> run b.cpp

# run a.cpp with file input and standard output
a.cpp> run -io fs
```

### Input and Output

The file input is at `.ecr/input.data`, and the file output is at `.ecr/output.data`.

### Clean

Clean the compiling output and something else:

```sh
> clean
```

# Config

The config files is at `.ecr/`

## config.json

This file contains basic config.

```json
{
    // File extension name to be cleaned
    "tempFileFilter": [
        "exe",
        "o",
        "class",
        "out"
    ],

    // Map name to system command
    "importedCommand": {
        "ls": "ls",
        "cls": "clear"
    },

    // The default shell to execute command
    "defaultShell": "powershell -c",

    // The default IO when run
    "defaultIO": "ss",

    // The default time limit for every step when run
    "defaultTimeLimit": 5
}
```

## executor.json

This file gives the way to run a code file.

You can use these varible in command:

- `fileName` The code file name
- `fileNameWithoutExt` The code file name without extension

```json
{
    "c": [
        "gcc {fileName} -o {fileNameWithoutExt}",
        "./{fileNameWithoutExt}"
    ],
    "cpp": [
        "g++ {fileName} -o {fileNameWithoutExt}",
        "./{fileNameWithoutExt}"
    ],
}
```


# Developing

- The `Makefile` use `SHELL` varible in Windows (as well as `PY`), so if you are in Linux, change it before use `make`.
- To build and upload the package, this requires these modules setuptools, wheel, twine. You can try `make prepare` to install these modules.

```sh
# Run
make run

make run RARG=-h # use command args

# Test
make test

# Test and get coverage
make cover

# Build
make build -B

# Install locally
make install

# Uninstall locally
make uninstall

# Clean
make clean

# Upload to PyPI
make upload

# Upload to TestPyPI
make uptest
```

# Requirements

- Python 3.7
- prompt_toolkit 2.0.7
