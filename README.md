[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](http://choosealicense.com/licenses/apache-2.0/)

# Hydra Prime

This repository stores the source code of our solver *Hydra Prime* for the Exact track of the [PACE 2023](https://pacechallenge.org/2023/) challenge.

### Solver Description

- Full version PDF: https://raw.githubusercontent.com/wiki/mogproject/twinwidth-2023/pace-2023-description.pdf

### Dependencies

- C++ compiler supporting the C++14 standard ([GCC](https://gcc.gnu.org/) recommended)
- [GNU Make](https://www.gnu.org/software/make/)
- [CMake](https://cmake.org/) Version 3.14 or later
- [CLI11](https://github.com/CLIUtils/CLI11)
- [The Kissat SAT Solver 3.0.0](https://github.com/arminbiere/kissat)

### Build usage

Use `make` in this project directory.

| Operation | Command |
|:---|:---|
|Build release version | `make build` $\to$ executalbe `exact-solver` will be generated in the `dist` directory|
|Build debug version (with logging features etc.) | `make build-debug` $\to$ creates `build/Debug/exact-solver`|
|Run unit tests | `make test` |
|Create submission file for OPTIL.io | `make publish` $\to$ creates `dist/exact-solver.tgz` |
|Clean build files | `make clean` |

### Program usage

| Operation | Command |
|:---|:---|
|Print help message | `exact-solver --help`|
|Print version | `exact-solver --version`|
|Output optimal contraction sequence | `exact-solver PATH` or `exact-solver < PATH` <br>(PATH: path to a problem instance file)|
|Output only twin-width | `exact-solver --tww PATH` |

##### DOI of Version 0.0.1

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7996823.svg)](https://doi.org/10.5281/zenodo.7996823)
