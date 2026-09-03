#!/usr/bin/env sh
set -e

mypy src --strict
mypy source_merger.py --strict
