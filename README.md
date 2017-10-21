# Python Pro Website

Source code of website www.python.pro.br

[![Build Status](https://travis-ci.org/pythonprobr/pythonpro-website.svg?branch=master)](https://travis-ci.org/pythonprobr/pythonpro-website)
[![codecov](https://codecov.io/gh/pythonprobr/pythonpro-website/branch/master/graph/badge.svg)](https://codecov.io/gh/pythonprobr/pythonpro-website)
[![Code Health](https://landscape.io/github/pythonprobr/pythonpro-website/master/landscape.svg?style=flat)](https://landscape.io/github/pythonprobr/pythonpro-website/master)
[![Updates](https://pyup.io/repos/github/pythonprobr/pythonpro-website/shield.svg)](https://pyup.io/repos/github/pythonprobr/pythonpro-website/)
[![Python 3](https://pyup.io/repos/github/pythonprobr/pythonpro-website/python-3-shield.svg)](https://pyup.io/repos/github/pythonprobr/pythonpro-website/)


It is been migrated from App Engine using Tekton to Heroky using Django

How to install in locally (supposing you have git and python 3 installed):

```console
git clone https://github.com/pythonprobr/pythonpro-website.git
cd pythonpro-website
cp contrib/settings-sample.yml settings.yml
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.dev
```

To run server locally (with virtualenv activated):

```console
python manager.py runserver
```

Have fun!



