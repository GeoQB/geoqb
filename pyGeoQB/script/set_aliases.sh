#!/bin/bash

if [ "$1" -eq "" ]
then
   envV=env1
else
   envV=$1
fi
clear
echo "********************************************************************************************"
echo "* Aliases for GeoQB commands will be defined for the virtual environment: $envV"
echo "********************************************************************************************"
alias gqws="source env/env.sh $envV; python3 examples/gqws.py"
alias gql="source env/env.sh $envV; python3 examples/gql.py"
alias gqblend="source env/env.sh $envV; python3 examples/gqblend.py"

alias