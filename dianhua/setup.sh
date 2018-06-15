#/bin/bash
pip install virtualenv
rm -rf venv/
virtualenv venv/
source venv/bin/activate
pip install -r requirements.txt
