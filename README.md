FIBO 0.0.3
==========

**The project provides a RESTful web service.**

The web service accepts a number, n, as input and returns the first n Fibonacci
numbers, starting from 0. I.e. given n  = 5, appropriate output would represent
the sequence [0, 1, 1, 2, 3].

Requirements
------------

Ensure that you have [Docker](https://docker.io) installed.

Installation
------------

Build docker container from repository

```sh

    $ make docker

```

Or pull it as 'horneds/fibo'.

```sh

    $ docker pull horneds/fibo

```


Usage
-----

Run the container with choosen port (For example port 8000):

```sh

    $ docker run -p 8000:8000 horneds/fibo

```

Make API requests:

```sh

    $ curl <docker_ip>:8000/
    $ curl <docker_ip>:8000/-40
    $ curl <docker_ip>:8000/100

```

Enjoy yourself.

Run tests
---------

Ensure that you have python3 and virtualenv installed.
Run the project's tests:

```sh

    $ make test

```
