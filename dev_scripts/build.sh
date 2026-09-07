#!/usr/bin/env sh
set -e

python source_merger.py
cd build

python -m nuitka\
    --onefile\
    --lto=auto\
    --assume-yes-for-downloads\
    --nofollow-import-to=*.site-packages\
    --output-dir=.\
    --deployment \
    --python-flag=-O\
    --output-filename=storyteller\
    storyteller.py
