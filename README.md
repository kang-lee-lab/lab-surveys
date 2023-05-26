# lab-surveys

A Python + Flask implementation of some surveys from the Kang Lee Development Lab. These surveys utilize computational models to compute results dynamically. 

Currently hosted on a Heroku server.

https://kangleelab-surveys.herokuapp.com/


To run locally you must setup a postgresql database on your machine. The following link provides a tutorial on setting up a database:

https://www.postgresqltutorial.com/postgresql-administration/postgresql-create-database/

Once the database is creted, a table must be created with the name "responses" and must be created with matching data values and types as seen in Response class found in __innit__.py
