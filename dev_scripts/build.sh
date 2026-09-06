#!/usr/bin/env sh
set -e

python source_merger.py
cd build

python -m nuitka\
    --onefile\
    --output-dir=.\
    --python-flag=-O\
    --output-filename=storyteller\
    storyteller.py
