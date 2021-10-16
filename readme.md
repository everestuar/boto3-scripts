# Scripts

## Pre-requisites
- AWS CLI account profile
- Python 3

## Execution

~~~bash
$ cd cloudwatch-alarms-python
$ mkdir .venv
$ virtualenv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ . env.sh
$ python alarms.py
~~~

## TODO
- Delete alarms
- Load catalog from a file
- Catalog of resources that should not be alarmed
- Search from internal dict resource catalogs
