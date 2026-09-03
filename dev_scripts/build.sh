#!/usr/bin/env sh
set -e

python source_merger.py
cd build

python -m nuitka --onefile --output-dir=. --static-libpython=yes --output-filename=storyteller storyteller.py
