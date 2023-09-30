#!/bin/bash


echo "Cleanup..."
test -d env && rm -Rf env
test -d website/output && rm -Rf website/output
test -d website/cache && rm -Rf website/cache
test -f website/.doit.db && rm -f website/.doit.db

echo "Building venv..."
python3.10 -m venv env

echo "Activating venv..."
source env/bin/activate

echo "Installing dependencies..."
if pip install -r requirements.txt
then
  echo "Building and running Website"
  cd website
  nikola build && nikola serve
fi

echo "Deactivating venv..."
deactivate


