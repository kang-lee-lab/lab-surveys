# lab-surveys

A Python + Flask implementation of some surveys from the Kang Lee Development Lab. These surveys utilize computational models to compute results dynamically. 

Currently hosted on a Heroku server.

https://kangleelab-surveys.herokuapp.com/


## Running locally

To run locally you must set up a PostgreSQL database on your machine. The following link provides a tutorial on setting up a database:

https://www.postgresqltutorial.com/postgresql-administration/postgresql-create-database/

Once the database is created, a table must be created with the name "responses" and must be created with matching data values and types as seen in the Response class found in __init__.py

Below is a tutorial on how to create a table within a database on pgAdmin.

https://www.guru99.com/create-drop-table-postgresql.html

Make sure you have a Python runtime environment set up (preferably Anaconda Python 3.9 or higher).

Then make sure you install all the libraries (`pip install -r requirements.txt` or `conda install -r requirements.txt` for Anaconda)

Once created, launch the app by running `python run.py`
