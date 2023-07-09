# Onboarding task for new developers

Please perform the following in a separate branch based off the main branch, and push it to GitHub so the branch is visible (but do not make a Pull Request to main):

- Define a new survey called <your_firstname>_test
- Create the appropriate functions and routes, where the format should be consistent with existing functions and routes
- Create the appropriate web pages, where the design is consistent with the remainder of the website (use Bootstrap)
- The new survey should consist of the following questions with the appropriate input types and ranges (see HTML input forms for details):
  - Your name (short input text)
  - Your email (email)
  - Your age (integer, limited to between)
  - Your gender (single selection, options: Male, Female, Other)
  - Please enter a random number (decimal, rounded to 1 decimal place)
- Note the survey cannot be submitted unless all the questions are answered
- The survey should compute a score (decimal) with the following formula: score = age * random_number * gender (1 for Male, 2 for Female, 3 for Other).
- The score (rounded to 1 decimal place) should be displayed on a results page along with the user's entered name and email address
- Make sure the new survey works without any errors and demo it to Bill.
