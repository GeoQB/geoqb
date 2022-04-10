#!/bin/bash

#
# Let's build a wheel ...
#

cd ../geoanalysis

python setup.py bdist_wheel

check-wheel-contents dist
