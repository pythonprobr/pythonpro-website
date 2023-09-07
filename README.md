# Dev Pro Website

Source code of website [https://painel.dev.pro.br](https://painel.dev.pro.br/checkout/pagarme/comunidade-devpro)


[![codecov](https://codecov.io/gh/pythonprobr/pythonpro-website/branch/master/graph/badge.svg)](https://codecov.io/gh/pythonprobr/pythonpro-website)


The web site is developed using Django.
The project uses Pipenv as dependecy management tool and Python Decouple for configurations.


How to install in locally (supposing you have git and python >= 3.7 installed):

```console
git clone https://github.com/pythonprobr/pythonpro-website.git
cd pythonpro-website
cp contrib/env-sample .env
python -m pip install pipenv
pipenv install -d
```

The project uses Postgres as database. You can use docker compose to install it as a service running:

```console
docker compose up -d
``` 

You can apply migrations to generate database schema:

```console
python manage.py migrate
``` 

You can seed database to create an admin and other usefull models:

```console
python manage.py seed_dev_db
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


and install docker and run:

```console
docker-compose up -d
```


#License Details

The AGPL license here cover everything relate to source code but Dev Pro logo and Image. So you need to change this data
for you own trademark.


Have fun!
