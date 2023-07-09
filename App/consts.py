""" Define constants and paths as global variables """

import os

# Constants


# Paths
STATIC_PATH = os.path.join('App', 'static')
SCHEMAS_PATH = os.path.join(STATIC_PATH, 'schemas')
SURVEYS_PATH = os.path.join(STATIC_PATH, 'surveys')
METADATA_SCHEMA_PATH = os.path.join(SCHEMAS_PATH, 'metadata.json')
QUESTIONS_SCHEMA_PATH = os.path.join(SCHEMAS_PATH, 'questions.json')
RESULTS_SCHEMA_PATH = os.path.join(SCHEMAS_PATH, 'results.json')
