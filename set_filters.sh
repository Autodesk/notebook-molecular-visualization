#!/usr/bin/env bash

git config filter.notebooks.clean nbmolviz/notebooks/strip_nb_output.py
git config filter.notebooks.smudge cat

