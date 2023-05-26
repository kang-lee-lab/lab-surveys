from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import DateTime
import time
from datetime import datetime, timedelta
import os

app = Flask(__name__, static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
db = SQLAlchemy(app)

class Response(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer, primary_key=True)
    time_stamp = db.Column(db.String(40), server_default= datetime.utcnow())
    response_type = db.Column(db.String(40), nullable=False)
    response_answers = db.Column(db.JSON, nullable = False)
    response_results = db.Column(db.JSON, nullable = False)
    
    def __init__(self, response_type, response_answers, response_results):
        self.response_type = response_type
        self.response_answers = response_answers
        self.response_results = response_results

from App import routes

application=app
