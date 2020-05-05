#!/bin/bash

pip install virtualenv

virtualenv env

source env/bin/activate

pip install -r requirements.txt

echo "\n\nActivate the virtual environment with the following command: \nsource env/bin/activate \n\nThen, run\npython .\nto run the __main__.py file"