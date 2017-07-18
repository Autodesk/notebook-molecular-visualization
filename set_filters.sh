#!/usr/bin/env bash

git config filter.notebooks.clean notebooks/strip_nb_output.py
git config filter.notebooks.smudge cat

