# trip-signup

A small Flask app where students register interest in a study abroad trip.
Signups are stored in a local SQLite database, and a password-protected
admin page lists them all.

## Features

- **Signup form** (`/`): collects name, email and major. All fields are
  required and the email must look valid; otherwise the form is shown again
  with an error.
- **Thank-you page** (`/thanks`): shown after a successful signup.
- **Admin page** (`/admin`): lists every signup (name, email, major, time
  signed up) with a total count. Protected by HTTP Basic Auth.

## Requirements

- Python 3.14
- [Pipenv](https://pipenv.pypa.io/)

## Setup

```sh
pipenv install --dev
```

Create a `.env` file in the project root with the admin password:

```
ADMIN_PASSWORD=choose-a-strong-password
```

`pipenv run` loads `.env` automatically. Never commit this file. It is
already listed in `.gitignore`.

## Running

```sh
pipenv run flask run --debug
```

Then open <http://127.0.0.1:5000>.

The database file `signups.db` is created automatically on first use. It is
also ignored by git.

## Admin page

Visit <http://127.0.0.1:5000/admin>. Your browser will prompt for a username
and password: any username works, and the password is the `ADMIN_PASSWORD`
value from `.env`.

If `ADMIN_PASSWORD` is not set, the admin page refuses all logins.

Basic Auth sends the password with every request, so serve the app over
HTTPS if you deploy it anywhere other than your own machine.

## Tests

```sh
pipenv run pytest -q
```

Tests use a temporary database and never touch `signups.db`.

## Project layout

```
app.py             Flask app: routes, database access, admin auth
templates/         Jinja templates (base, signup, thanks, admin)
test_app.py        pytest suite
Pipfile(.lock)     Dependencies
```

## Contributing notes

- Database access uses the built-in `sqlite3` module (no ORM), with
  parameterized queries (`?`) only.
- Never print or log applicant emails.
- Templates are plain HTML styled with Bootstrap CSS; no JavaScript frameworks.
- Add or update a test for every change, and run the test suite before
  considering it done.
- Add packages with `pipenv install` (`--dev` for test tools).
