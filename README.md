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
