#!/usr/bin/env sh
set -e

python source_merger.py
cd build

python -m nuitka\
    --mode=app\
    --company-name=VBismuth\
    --product-name=Storyteller\
    --output-dir=.\
    --python-flag=-O\
    --output-filename=storyteller\
    storyteller.py
