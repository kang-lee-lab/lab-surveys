# lab-surveys

A Python + Flask implementation of some surveys from the Kang Lee Development Lab. These surveys utilize computational models to compute results dynamically.

Currently hosted on a Heroku server.

https://kangleelab-surveys.herokuapp.com/


## Running locally

To run locally you must set up a PostgreSQL database on your machine.

To create a database locally you must download a database manager such as pgAdmin (As shown on the link above). PgAdmin is available on both Mac and Windows.

Once the database is created, a table must be created with the name "responses" and must be created with matching data values and types as seen in the Response class found in `__init__.py`

Below is a tutorial on how to create a table within a database on pgAdmin.

https://www.guru99.com/create-drop-table-postgresql.html

Once the database is created, get a link for the database from pgAdmin and replace it with the current link on line 10 of '__init__.py'

Then run the following commands in your terminal to import the database and model:

from App import db, Response
db.create_all()

The following link provides some more information on these commands
https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application

Make sure you have a Python runtime environment set up (preferably Anaconda Python 3.9 or higher).

Then make sure you install all the libraries (`pip install -r requirements.txt` or `conda install -r requirements.txt` for Anaconda)

Once created, launch the app by running `python run.py`


## Development

The `main` branch is locked, and all changes should come in the form of a pull request (PR) on GitHub from your development branch.

Please name your branches `<yourname>/<issue_ID>/<brief description of your changes>`.

Please test your application in the QA Heroku environment (https://dashboard.heroku.com/apps/kangleelab-surveys-qa) before pushing to the "main" branch (you can deploy a branch on Heroku)

If you have any suggestions about how to improve this app, please add a ticket on the project page (https://github.com/orgs/kang-lee-lab/projects/2/views/2)
