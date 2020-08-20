# Python Pro Website

Source code of website www.python.pro.br

[![Build Status](https://travis-ci.org/pythonprobr/pythonpro-website.svg?branch=master)](https://travis-ci.org/pythonprobr/pythonpro-website)
[![codecov](https://codecov.io/gh/pythonprobr/pythonpro-website/branch/master/graph/badge.svg)](https://codecov.io/gh/pythonprobr/pythonpro-website)
[![Code Health](https://landscape.io/github/pythonprobr/pythonpro-website/master/landscape.svg?style=flat)](https://landscape.io/github/pythonprobr/pythonpro-website/master)
[![Updates](https://pyup.io/repos/github/pythonprobr/pythonpro-website/shield.svg)](https://pyup.io/repos/github/pythonprobr/pythonpro-website/)
[![Python 3](https://pyup.io/repos/github/pythonprobr/pythonpro-website/python-3-shield.svg)](https://pyup.io/repos/github/pythonprobr/pythonpro-website/)


It's developed using Django

How to install in locally (supposing you have git and python >= 3.7 installed):

```console
git clone https://github.com/pythonprobr/pythonpro-website.git
cd pythonpro-website
cp contrib/env-sample .env
python -m pip install pipenv
pipenv install -d
```

If you want use SQLite on your dev environment, please remove DATABASE_URL from .env file.
Otherwise fill this value with your database credentials.

You can apply migrations to generate database schema:

```console
python manage.py migrate
``` 

You can also create a user:

```console
python manage.py createsuperuser
```

To run server locally (with virtualenv activated):

```console
python manager.py runserver
```

If you want populate the database with some content run: 

```console
python manage.py loaddata pythonpro_contents
```

To tun the tests:

```console
pytest pythonpro
```

If you want run your amb dev using postgres, you can add to your .env 

```console
DATABASE_URL=postgres://postgres:pass@localhost:5432/postgres
```


and install docker and run:

```console
docker-compose up -d
```


#License Details

The AGPL license here cover everything relate to source code but Python Pro logo and Image.
So you need to change this data for you own trademark.


Have fun!
