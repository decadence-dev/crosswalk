# crosswalk

## Description
Crosswalk is a microservices social network project.

## Launching
### Installation
Every single service inside project is independent program. 
For launching services you can use native tools and environment but in that case everysing is up to you an there is not specific recipe for how you should do it.

But if you are dicided to using docker then first of all you should install it with using specific destributive for yout OS which you can find [here](https://docs.docker.com/get-docker/).

### Building
The next step is to build project services.

For that purpose you can use docker-compose utility. It is makes building of project services and network much easier than native docker utility do.

docker-compose is a python's package so for it using you need a installed python and pip.

For example for MacOS you can use brew to install python:
```
brew install python
```
... but of course brew is should have been already installed.

How to install brew you can find [here](https://brew.sh/index_ru).

After python will be installed on yout OS you can to install docker-compose:
```
pip install docker-compose
```

At last when your enviroment is ready you can start project services building.

Inside project root directory (directory with docker-cmopose.yml file) run:
```
docker-compose build
```
It is will build all services images inside project.

If you need to build some specific service you can use:
```
docker-compose build <service_name>
```

### Launching
The final step is to run service  and play with it.

To launch whole project you need run:
```
docker-compose up
```

To launch some specific service you can use:
```
docker-compose up <service_name>
```

To start services in the backgroun you can add `-d` option:
```
docker-compose up -d <service_name>
```

After needed services is launched is it time to play.

You can find services by it is host and port configuration inside docker-compose.yml.

Usualy all opened services using your localhost and specific port inside docker-compose.yml ports serction.

For example:
```
version: '3'
services:
  events:
    volumes:
      ...
    ports:
      - 8000:8000
    environment:
      ...
```

Service events can be found by url http://localhost:8000/docs
