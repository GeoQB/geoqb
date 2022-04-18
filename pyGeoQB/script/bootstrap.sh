#!/bin/bash

#
# the argument $1 is the name
#
python3 -m venv $1
source $1/bin/activate

brew install curl

pip install --upgrade pip
pip install --upgrade -q gspread
pip install -r requirements.txt

source set_aliases.sh $1