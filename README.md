# devchain

Command Line Tool that provides a Development-Toolchain-as-a-Service


## Motivation

In most projects, the development toolchain is automated in some way, such as with Rake or Invoke. \
Keeping that automation up to date across all projects is not easy. So this CLI tool aims to solve this problem by handling all the automation in one central place.


## Developer Guide


### Installation

```bash
# Open the virtualenv
poetry shell

# Build and install the tool
poetry install

# Check if the tool has been installed
which devchain
```


### Testing

```bash
# Run all tests that matches ./tests/test_*.py
poetry run pytest
```


### Deployment

```bash
# Create sdist and wheel
poetry build
```


## Installation

```bash
# Install previously built package on any maching with...
sudo pip install ./dist/devchain-0.1.0-py3-none-any.whl
```

Once the tool is installed, autocompletion can be enabled as follows:
```bash
devchain --install-completion

. ~/.bashrc
```


## Usage


### Common

Show information about the tool itself:
```bash
devchain about
```

Show information about the project in the current directory:
```bash
devchain info
```

Clean the project setup:
```bash
devchain clean
```


### Toolchain Set-up

Create a new toolchain in an empty directory:
```bash
mkdir -p /tmp/devchain/test && cd /tmp/devchain/test

devchain create --toolchain cpp
```
`--toolchain` is supported by the autocompletion. \
So you can select it with [tab].


### C++ Toolchain

Build the project, for example with clang-14:
```bash
devchain build --settings clang14__x86_64-pc-linux-elf__release
```
`--settings` is supported by the autocompletion. \
So you can select it with [tab].


Run a tool, for example clang-tidy or gtest:
```bash
devchain run --tool gtest
devchain run --tool benchmark
devchain run --tool clang-tidy
```
`--tool` is supported by the autocompletion. \
So you can select it with [tab].
