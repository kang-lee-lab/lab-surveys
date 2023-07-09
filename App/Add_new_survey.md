# Adding a new survey

Please follow these instructions for adding a new survey to be displayed on the survey website:

1. Clone this repository onto your computer, and create a branch in git from the `main` branch (`git branch <your branch name>`).

2. Come up with a unique survey_ID that does not have spaces or special characters (except for "_"). 

3. Create a folder in `App/static/surveys` named after your survey_ID.

4. In your newly created folder `App/static/surveys/<survey_ID>`, create three JSON files containing your survey information: `metadata_<language>.json`, `questions_<language>.json`, `results_<language>.json`. Note the `language` must be "EN" (English), "CH" (Chinese), "FR" (French), or similar format (e.g. the filenames will be `metadata_EN.json`, `questions_EN.json`, etc. for English).

5. Fill in each JSON file according to the JSON schema format (The schema files are located in `App/static/schemas`. Please see https://json-schema.org/learn/getting-started-step-by-step.html to get started). Alternatively, you can follow the sample survey in `App/static/surveys/sample_survey`.

6. Once finished, you can run the `validate_schema.py` script in the main folder to validate all your schemas. To run in command line, run `python validate_schema.py <survey_id> <language>`.

7. Note if your survey comes in multiple languages, you must repeat steps 4-6 for each language.

8. Under `App/surveys`, create a Python file titled `<survey_ID>.py`. Please follow the exact format of the functions in `sample_survey.py`. You can add your custom logic for loading the questions and calculating the results.

9. Launch the web application locally (`python run.py`) and test your new survey. Make sure there are no errors. 

10. Push your branch (`git push`), then create a pull request on GitHub from your branch from your branch to the `main` branch.
