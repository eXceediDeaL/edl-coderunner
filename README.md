# edl-cr

![](https://img.shields.io/badge/edl--cr-vFirst-blue.svg) ![](https://img.shields.io/badge/license-Apache--2.0-blue.svg) [![](https://img.shields.io/badge/test-passed-green.svg)](https://exceedideal.github.io/edl-coderunner/dev/reports/test/) [![](http://progressed.io/bar/90?title=coverage)](https://exceedideal.github.io/edl-coderunner/dev/reports/coverage/) ![](http://progressed.io/bar/10?title=developing)


A CLI tool to run code.

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

# Clean
make clean

# Upload to PyPI
make upload

# Upload to TestPyPI
make uptest
```

# Requirements

- Python 3.7
