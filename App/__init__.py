"""
Initialization module for the lab surveys website app.
"""
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from App import routes

app = Flask(__name__, static_url_path="")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL").replace(
    "://", "ql://", 1
)
db = SQLAlchemy(app)


class Response(db.Model):
    """
    A class representing a response to a survey.

    Attributes:
        - id: The unique identifier for a response.
        - time_stamp: The timestamp indicating when the response was recorded.
        - response_type: The type or category of the response.
        - response_answers: JSON data representing the user's answers.
        - response_results: JSON data representing the results associated with the response.
    """

    __tablename__ = "responses"
    id = db.Column(db.Integer, primary_key=True)
    time_stamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    response_type = db.Column(db.String(40), nullable=False)
    response_answers = db.Column(db.JSON, nullable=False)
    response_results = db.Column(db.JSON, nullable=False)

    def __init__(
        self, response_type: str, response_answers: JSON, response_results: JSON
    ) -> None:
        """
        Initialize a new Response object.

        Arguments:
            - response_type (str): The type or category of the response.
            - response_answers (JSON): JSON data representing the user's answers.
            - response_results (JSON): JSON data representing the results associated with the response.
        """
        self.response_type = response_type
        self.response_answers = response_answers
        self.response_results = response_results


application = app
