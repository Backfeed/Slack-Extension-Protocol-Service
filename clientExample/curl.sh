#!/bin/bash
#
#    curl example
#    ~~~~~~~~~~~~
#
#    This provides an example of using Flask-Restless on the server-side to
#    provide a ReSTful API and `curl <http://curl.haxx.se/>`_ on the client
#    side to make HTTP requests to the server.
#
#    In order to use this script, you must first run the quickstart server
#    example from this directory::
#
#        PYTHONPATH=.. python quickstart.py
#
#    Now run this script from this directory (that is, the ``examples/``
#    directory) to see some example requests made from curl::
#
#        ./curl.sh
#
#    The important thing to note in this example is that the client must
#    remember to specify the ``application/json`` MIME type when sending
#    requests.
#
#    :copyright: 2012 Jeffrey Finkelstein <jeffrey.finkelstein@gmail.com>
#    :license: GNU AGPLv3+ or BSD

# We expect the server to be running at 127.0.0.1:5000, the Flask default.
HOST=127.0.0.1:5000
#HOST = 'sparkapp-env.elasticbeanstalk.com'


echo
echo "Making an initial GET request..."
echo
# curl makes GET requests by default.

curl -X POST -H "Content-type: application/json" http://$HOST/users \
    -d '{"slackId": "slackId","name":"name"}'

curl -X POST -H "Content-type: application/json" http://$HOST/bids \
    -d '{"reputation": "50","tokens":"20","resourceId":"resId","ownerId":"owner_Id"}'

: '	
echo
echo
echo "Making a POST request..."
echo
curl -X POST -H "Content-type: application/json" http://$HOST/characters \
    -d '{"name": "logi"}'	
 

echo
echo
echo "Making taskLogs GET request for geva."
echo
curl http://$HOST/tasklogs



echo
echo
echo "Making a POST request..."
echo
curl -X POST -H "Content-type: application/json" http://$HOST/monsters \
    -d '{"race": "Squid"}'

echo
echo
echo "Making a GET request for the entire collection..."
echo
curl -H "Content-type: application/json" http://$HOST/monsters

echo
echo
echo "Making a GET request for the added person..."
echo
curl -H "Content-type: application/json" http://$HOST/monsters/1
echo
'

# Note: don't include spaces when specifying the parameters of the search with
# the `d` argument. If you want spaces, encode them using URL encoding (that
# is, use "%20" instead of " ").

: '
echo
echo
echo "Searching for all people whose names contain a 'y'..."
echo

curl \
  -G \
  -H "Content-type: application/json" \
  -d "q={\"filters\":[{\"race\":\"race\",\"op\":\"like\",\"val\":\"%y%\"}]}" \
  http://$HOST/monsters
echo
'