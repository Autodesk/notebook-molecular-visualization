#!/usr/bin/env bash

git config filter.notebooks.clean buckyball/notebooks/strip_nb_output.py
git config filter.notebooks.smudge cat

