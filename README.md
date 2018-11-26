# edl-cr

[![](https://img.shields.io/github/stars/eXceediDeaL/edl-coderunner.svg?style=social&label=Stars)](https://github.com/eXceediDeaL/edl-coderunner) [![](https://img.shields.io/github/forks/eXceediDeaL/edl-coderunner.svg?style=social&label=Fork)](https://github.com/eXceediDeaL/edl-coderunner) ![](http://progressed.io/bar/60?title=developing) [![](https://img.shields.io/github/license/eXceediDeaL/edl-coderunner.svg)](https://github.com/eXceediDeaL/edl-coderunner/blob/master/LICENSE)

A CLI tool to run code. See more at [here](https://exceedideal.github.io/edl-coderunner/)

Project Status:

|||
|-|-|
|Repository|[![](https://img.shields.io/github/issues/eXceediDeaL/edl-coderunner.svg)](https://github.com/eXceediDeaL/edl-coderunner/issues/) [![](https://img.shields.io/github/issues-pr/eXceediDeaL/edl-coderunner.svg)](https://github.com/eXceediDeaL/edl-coderunner/pulls/)|
|Dependencies|![](https://img.shields.io/pypi/pyversions/edl-cr.svg) ![](https://img.shields.io/librariesio/github/eXceediDeaL/edl-coderunner.svg)|
|Build|[![](https://img.shields.io/travis/eXceediDeaL/edl-coderunner/master.svg?label=master)](https://travis-ci.org/eXceediDeaL/edl-coderunner) ![](https://img.shields.io/travis/eXceediDeaL/edl-coderunner/dev.svg?label=dev)|
|Release|[![](https://img.shields.io/github/release/eXceediDeaL/edl-coderunner.svg)](https://github.com/eXceediDeaL/edl-coderunner/releases/latest/) [![](https://img.shields.io/github/tag/eXceediDeaL/edl-coderunner.svg)](https://github.com/eXceediDeaL/edl-coderunner/tags)|
|Package|[![](https://img.shields.io/pypi/v/edl-cr.svg)](https://pypi.org/project/edl-cr/) ![](	https://img.shields.io/pypi/status/edl-cr.svg) ![](https://img.shields.io/pypi/dd/edl-cr.svg)|

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
|`-d --dir`|Set working directory|
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

Then use `edit` to open default editor to edit code:

```sh
> edit
```

Then use `run` command to run code.

```sh
# run a.cpp
a.cpp> run

# run b.cpp
a.cpp> run b.cpp

# run a.cpp with file input and standard output
a.cpp> run -io fs

# watch the file a.cpp and run auto
a.cpp> run -w
```

If you give `input.data` and `std.data` for input data and standard output data, use `judge` to run and judge output data.

```sh
# run a.cpp's output
a.cpp> judge

# run and judge b.cpp's output
a.cpp> judge b.cpp -r

# watch the file a.cpp and run&judge auto
a.cpp> judge -w -r
```

### Use Directory

Not only use files, you can also use directories to create a unique environment for codes.

```sh
# Create a new directory env
> new project -d

# Set a directory env for current
> now project -d

# Run
@project> run

# Judge
@project> judge
```

For `run` and `judge` commands, it will use the command list in `config.yml` in the directory. You can write your own commands in it.

```yaml
judge: null
run: null
```

### Input and Output

The file input is at `.ecr/input.data`, and the file output is at `.ecr/output.data`.

The standard output data for judging is at `.ecr/std.data`

### Clean

Clean the compiling output and something else:

```sh
> clean
```

### Variables

You can use builtin variables just like in bash:

```sh
> echo $wdir
```

|Variable|Description|
|-|-|
|`wdir`|Working directory|
|`edir`|ECR directory|
|`jdir`|Judger directory|
|`tdir`|Template directory|
|`current`|Current file|
|`input`|Input file|
|`output`|Output file|
|`config`|Config file|

### Commands

These are builtin commands. You can use system command in `importedCommand` list.

If you want to call a system command that isn't in `importedCommand` list, use `>` prefix like `>ls`.

|Command|Description|
|-|-|
|`init`|Initialize ECR data|
|`clear`|Clear ECR data|
|`new [file] [-e --edit] [-d --dir]`|Create new code file|
|`now [file] [-d --dir]`|Change current file|
|`edit [file] [-n --now] [-d --dir]`|Edit code file|
|`run [file] [-io --io] [-w] [-d --dir]`|Run code file|
|`judge [file] [-r --re] [-w] [-j --judger] [-d --dir]`|Judge output data|
|`clean`|Clean temp files|
|`pwd`|Print working directory|
|`cd`|Change working directory|
|`version`|Get version|
|`cls`|Clear console|
|`exit`|Exit|
|`-h --help`|Get help|

# Config

The config files is at `.ecr/`

## config.yml

This file contains basic config.

```yaml
# The default editor
defaultEditor: vim

# The default judger's name
defaultJudger: diff

# The default IO when run
defaultIO: ss

# The default shell to execute command
defaultShell: powershell -c

# The default time limit for every step when run
defaultTimeLimit: 10

# Map name to system command
importedCommand:
    bash: bash
    cat: cat
    copy: copy
    cp: cp

# File extension name to be cleaned
tempFileFilter:
- exe
- o
- class
- out
```

## executor.yml

This file gives the way to run a code file.

You can use these varibles in command:

- `fileName` The code file name
- `fileNameWithoutExt` The code file name without extension

```yaml
c:
- gcc {fileName} -o {fileNameWithoutExt}
- ./{fileNameWithoutExt}

cpp:
- g++ {fileName} -o {fileNameWithoutExt}
- ./{fileNameWithoutExt}
```

## judger.yml

This file gives the way to judge.

You can use these varibles in command:

- `judgerDir` The directory path for judgers. It will be pointed to `$wdir/.ecr/judgers`
- `expectFile` The expect output file
- `realFile` The real output file

```yaml
diff: # Judger name
- python -u {judgerDir}/diff.py {expectFile} {realFile}
```

## judgers/

This directory contains some judgers, you can 

# Developing

- The `Makefile` use `SHELL` varible in Windows (as well as `PY`), so if you are in Linux, change it before use `make`.
- To build and upload the package, this requires these modules setuptools, wheel, twine. You can try `make prepare` to install these modules.
- Maybe there are some differences between win's command and linux's command, so feel free to modify `Makefile` when you meet some errors.

```sh
# Run
make run

make run RARG=-h # use command args

# Use pylint to check
make lint

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
- [See more](https://github.com/eXceediDeaL/edl-coderunner/network/dependencies)
