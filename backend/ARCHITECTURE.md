# Kang Lee Lab Surveys Architecture

This details the architecture of the kangleelabs-survey website.

## Tech-stack

1. Front-end: React, JavaScript, HTML, CSS
2. Back-end: Python, Django, SQL
3. Data layer: PostgreSQL
4. Tools: VSCode, pgAdmin, Heroku, Vercel, Supabase, Auth0

## Deployment in Production

Currently our production website is being hosted on Heroku, Vercel, and Supabase. Heroku hosts our back-end, Vercel hosts our front-end and Supabase holds our production database.

## Authentication

We are using Auth0 for our authentication needs, this provides the API for us to securely login/logout and store user information. We currently do not support creating an account through our website, all accounts are manually created on Auth0 to control who has access to survey data.

### Maintenance/Gotchas

1. When deploying to the backend, make sure that all environment variables are up to date. Sometimes when you have a bug, it may be because you have created an environment variable locally but have not added it to Heroku, meaning the application cannot access the variable.

2. Since we are using the free tier version of Supabase, it will deactivate our database after a certain amount of time if there is no activity. If we run into an issue submitting a survey or etc. try seeing if our database is inactivated on Supabase.

3. If we make any changes on our databases, we will have to also run a migration on Supabase, so our production database structure matches our local changes.
