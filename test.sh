#!/bin/bash

_opt_dev=false

while [ "${#}" -gt 0 ]
do
    case "${1}" in
        --dev)
            _opt_dev=true
        ;;
    esac
    shift
done

echo "Cleanup..."
test -d env && rm -Rf env
test -d website/output && rm -Rf website/output
test -d website/cache && rm -Rf website/cache
test -f website/.doit.db && rm -f website/.doit.db

echo "Building venv..."
python3.10 -m venv env

echo "Activating venv..."
source env/bin/activate

_requirements_file="requirements.txt"
if $_opt_dev
then
    _requirements_file="requirements-dev.txt"
fi

echo "Installing dependencies..."
if pip install -r "${_requirements_file}"
then
  echo "Building and running Website"
  cd website
  nikola build && nikola serve
fi

echo "Deactivating venv..."
deactivate


