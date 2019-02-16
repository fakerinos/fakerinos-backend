# Running a Local Server

## Get the Repository

If you don't already have a local copy of the repository, go ahead and clone it:

```bash
$ git clone https://github.com/escape-ai/fakerinos-backend
```

____

## Install Windows Subsystem for Linux

**This step is mandatory if you're running Windows**

*Skip if you're already running Linux or Mac OS X*

Fakerinos-backend requires the `uvicorn` ASGI Server to run. `uvicorn` is based on `gunicorn`, which only supports UNIX-based systems.

Fakerinos-backend also requires `redis-server` to be running locally, and this currently isn't supported on Windows.

[*Windows Subsystem for Linux*](https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux) offers a Linux shell directly in Windows 10. This lets you run `uvicorn` as if it were being run right in Windows.

[Follow these instructions to get it running.](http://wsl-guide.org/en/latest/installation.html)

_____

## Set Up Your Environment

**If you're running Windows, open up a Linux shell before proceeding.**

### Create a Virtual Environment

This step is strongly recommended. You can use either Virtualenv or Anaconda, but only the Anaconda way is documented here.

```bash
$ conda create -n fakerinos python=3.6
$ conda activate fakerinos
```

### Install Python Requirements

The repository comes with several requirements files, each for a different environment.

Ensure that you've activated your virtual environment before installing anything.

```bash
$ pip install -r requirements/linux.txt
$ python -m django --version  # check if django installed correctly
2.1.7
```

### Install Heroku CLI

The Heroku CLI allows you to run the app with as close a configuration to the deployed version as possible.

```bash
$ sudo apt update
$ sudo apt install snapd
$ sudo snap install --classic heroku
$ heroku -v  # check installation
heroku/7.20.1 linux-x64 node-v11.3.0
```

### Install Redis Server

```bash
$ sudo apt update
$ sudo apt install redis-server
$ redis-server -v  # check installation
Redis server v=4.0.9 sha=00000000:0 malloc=jemalloc-3.6.0 bits=64 build=76095d16786fbcba
```

____

## Django Project Setup

Django needs to set some things up before it can serve anything.

From within the project directory:

```bash
$ python manage.py migrate
$ python manage.py collectstatic
$ python manage.py createsuperuser
```

`createsuperuser` lets you create an admin account in the project's local database. This can be pretty useful for doing things like manually creating and removing user accounts.

____

## Heroku Local Requirements

The Heroku CLI offers an option to run your project locally with similar configuration to the deployed app.

Fakerinos-backend requires 2 configuration files in order to run:

- `Procfile.dev`: Contains the Heroku dyno run configuration used by `heroku local`
- `.env`: Contains environment variable values that `heroku local` reads and applies

> `.env` contains potentially sensitive information, and is therefore not included in the repository. Make sure you have the latest version of this file if you face any issues with environment variables.

_____

## Run the Local Server

That should conclude the setup, and you should now be able to run a local server:

```bash
$ heroku local -f Procfile.dev
```

the `-f` option of `heroku local` tells it which run configuration to use.

By default, the local server should bind to port 5000.

You can now test this by visiting http://127.0.0.1:5000/api/docs.