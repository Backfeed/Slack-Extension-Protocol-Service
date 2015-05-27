Demo RESTful HTTP API using Flask, Flask-Restful and SQLAlchemy
===================

1. Install requisite packages:

    pip install -r requirements.txt

2. Run service:

    python ./application.py

3. Give it a try:  run: clientExample/curl.sh

```
>> import requests, json
>> requests.get('http://localhost:5000/todos').json()
[]
>> requests.post('http://localhost:5000/todos',
                 headers={'Content-Type': 'application/json'},
                 data=json.dumps({'task': 'go outside!'})).json()
{u'id': 1, u'task': u'go outside!', u'uri': u'http://localhost:5000/todos/1'}
>> requests.get('http://localhost:5000/todos/1').json()
{u'id': 1, u'task': u'go outside!', u'uri': u'http://localhost:5000/todos/1'}
>> requests.put('http://localhost:5000/todos/1',
                headers={'Content-Type': 'application/json'},
                data=json.dumps({'task': 'go to the gym'})).json()
{u'id': 1, u'task': u'go to the gym', u'uri': u'http://localhost:5000/todos/1'}
>> requests.delete('http://localhost:5000/todos/1')
>> requests.get('http://localhost:5000/todos').json()
[]
```

Don't forget that you must past a "Content-Type: application/json" header along
w/ your request!
