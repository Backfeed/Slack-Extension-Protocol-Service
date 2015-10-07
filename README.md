Backfeed RESTful HTTP API 
===================

using Flask, Flask-Restful and SQLAlchemy.
and angularjs (for monitoring UI.)

to run locally:

1. set up a vagrant machine (see Vagrantfile, provosion.sh) or Install requisite packages:

    pip install -r requirements.txt  

2. create main.db (local sqlite database file) :

	python migrationManager.py db upgrade

3. Run service:

    python ./application.py

4. check it out at:  http://localhost:5000

<h3>Calling the Server API Remotely</h3>
<h6>TODO: we need to decouple the API from the slack extension. API client currently has to send `satellizer_token` with each request, which can only be retrieved by packaging the extension, installing it, logging in, and looking inside localStorage</h6>
This is the API URL: https://refactor.elasticbeanstalk.com/<br>
The list of endpoints: https://github.com/Backfeed/BF-Chrome-Extension/blob/develop/extension/contentScript/app/contentServices/services.js<br>
You could clone the BF-Chrome-Extension codebase and deep search for method names (e.g. `ContributionDetail.getDetail``) to find out the expected data model of the request object.<br>
Most requests require authentication data returned by https://refactor.elasticbeanstalk.com/api/me so make sure to call that before any subsequent calls.<br>

There are 2 _HTTP headers_ you need to add to all requests:

    1. `User-Agent`: the value is the string 'DEAP'
    2. `x-access-token`: the value should be the word `Bearer ` (with a whitespace after) immediately followed by the `satellizer_token` from the extension's localStorage.

![](http://backfeed.cc/wp-content/uploads/misc/where_to_find_satellizer_token.jpg)
You'll see it on a tab opened with domain *.slack.com while the extension in installed and you're logged in
