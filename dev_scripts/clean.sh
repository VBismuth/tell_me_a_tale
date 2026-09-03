#!/usr/bin/env sh
set -e

if [ `basename $(pwd)` != "tell_me_a_tale" ]
then
    >&2 echo "ERROR: clean: should be ran in the root dir \"tell_me_a_tale\""
    exit 1
fi
git clean -fdx -e tmp -e .mypy_cache
