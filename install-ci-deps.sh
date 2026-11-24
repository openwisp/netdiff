#!/bin/bash
# Install dependencies used by CI and review.
set -e
python -m pip install -U pip wheel setuptools
python -m pip install -U -r requirements-test.txt
python -m pip install -U -e .
