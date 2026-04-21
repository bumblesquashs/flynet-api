## Flynet API

Description TODO 

The API is built in Python, using FastAPI and SQL Alchemy. The backend datastore, is built using PostgresSQL. Each
request must be authenticated with a JWT token.

- Vue 3, vuetify 3
- Pydantic 2, SQLAlchemy 2
- https://docs.sqlalchemy.org/en/20/changelog/migration_20.html#the-1-4-2-0-migration-path migration guide for the latter

### Technology Stack 

Foundation:

- Python 3.9
- Poetry

Frameworks

- FastAPI
- Pydantic
- Starlette
- SQLAlchemy
- Psycopg2
- PyTest

Database Backends:

- PostgresSQL
- SQLite

### Getting Started

The main API is a `uvicorn` based application, and the dependencies are managed with `poetry` the recommended way to
get started is by first installing:

- Poetry
- PyEnv

#### Installing PyEnv on Linux (Ubuntu 20.04 LTS)

Quick side note here from James about installing PyEnv on linux -
The pyenv site didn't explain how to do it, but I found this article on google which worked out for me:
https://www.liquidweb.com/kb/how-to-install-pyenv-on-ubuntu-18-04/

That boiled down to the following commands which download the pyenv source and then modify your .bashrc to use it
(probably similar stuff for .zshrc if you use zsh or whatnot)

```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init --path)"\nfi' >> ~/.bashrc
exec "$SHELL"
```

I had to modify my commands from what the article said slightly (used `pyenv init --path`) based on this stack overflow article here:
https://stackoverflow.com/questions/33321312/cannot-switch-python-with-pyenv

### Getting Started Continued

Once those are installed, use PyEnv to install Python 3.9.(the most up-to-date version) and then use `poetry` to install the dependencies after
cloning the repo.

```shell
git clone ...
```

The command above would load your private key and make it accessible to `git` to use for authentication, otherwise
you can generate a PAT token in GitLab and use that.

After you've checked out the code, you'll need to create a couple of `.env` files; one in `src/` folder and one in the
`tests/` folder.

In the `src/` folder you will want to specify server host, and the connection details to your Postgres database.

Additionally, you'll need to fill in the mailgun domain and key here available on the mailgun portal. I have filled in
the domain calico has been using for staging environments.

```dotenv
FLYNET_API__SERVER_HOST=0.0.0.0
FLYNET_API__SERVER_PORT=9010
FLYNET_API__HOST_PREFIX=''
FLYNET_API__SQLALCHEMY_DATABASE_URI=sqlite:///./test.db
FLYNET_API__TOKEN_SECRET=001888b9e0759ff3090a95479866998285d521a57851301d515eba3c0a8139b8
FLYNET_API__AUDIENCE=http://0.0.0.0:9010
FLYNET_API__ISSUER=http://0.0.0.0:9010
FLYNET_API__INTERNAL_DEV_MODE=True
FLYNET_API__BACKEND_CORS_ORIGINS='["http://localhost:8080"]'
FLYNET_API__MAILGUN_DOMAIN=mg.cldevbox.com
FLYNET_API__MAILGUN_API_KEY=mailgun-key-here
```

NOTE: When it comes time to use the Postgres database, you want to instead use a .env file that looks like this.

```dotenv
FLYNET_API__SERVER_HOST=0.0.0.0
FLYNET_API__SERVER_PORT=9010
FLYNET_API__HOST_PREFIX=''
FLYNET_API__TOKEN_SECRET=001888b9e0759ff3090a95479866998285d521a57851301d515eba3c0a8139b8
FLYNET_API__AUDIENCE=http://0.0.0.0:9010
FLYNET_API__ISSUER=http://0.0.0.0:9010
FLYNET_API__INTERNAL_DEV_MODE=True
FLYNET_API__BACKEND_CORS_ORIGINS='["http://localhost:8080"]'
FLYNET_API__MAILGUN_DOMAIN=mg.cldevbox.com
FLYNET_API__MAILGUN_API_KEY=mailgun-key-here
FLYNET_API__POSTGRES_SERVER=localhost
FLYNET_API__POSTGRES_USER="postgres (or some other user)"
FLYNET_API__POSTGRES_PASSWORD="your db user's password here"
FLYNET_API__POSTGRES_DB="the database name you created in your local postgres server"
```

In the `tests/` folder you shouldn't really need to change much; since it's going to be using a SQLite database.

```dotenv
FLYNET_API__SERVER_HOST=0.0.0.0
FLYNET_API__SERVER_PORT=9010
FLYNET_API__HOST_PREFIX=''
FLYNET_API__SQLALCHEMY_DATABASE_URI=sqlite:///./test.db
FLYNET_API__TOKEN_SECRET=001888b9e0759ff3090a95479866998285d521a57851301d515eba3c0a8139b8
FLYNET_API__AUDIENCE=http://0.0.0.0:9010
FLYNET_API__ISSUER=http://0.0.0.0:9010
FLYNET_API__INTERNAL_DEV_MODE=True
FLYNET_API__BACKEND_CORS_ORIGINS='["http://localhost:8080"]'
FLYNET_API__MAILGUN_DOMAIN=mg.cldevbox.com
FLYNET_API__MAILGUN_API_KEY=abc
```

The key differences are that the SQLALCHEMY_DATABASE_URI is missing and the POSTGRES entries are present.

You'll also need all of your fancy dependencies, so from the project root, you'll need to run:

```shell
poetry install
```

If you have a system that Python doesn't hate, you should be good to go, otherwise, you might need to install
build-essentials and other junk; if you are one a Ubuntu flavoured Linux you can do the following:

```shell
sudo apt-get install python3 python3-setuptools python3-pkg-resources \
    python3-pip python3-dev libffi-dev build-essential git
```

Your millage may vary here; but that should get you a basic build tool chain for `gcc` based derivatives. Now that
you've gotten over getting the project dependencies installed, running things is actually pretty easy.

### Starting the API

To run the project all you really need to do is from the `src/` directory run:

```shell
python portal.py
```

Once it's running, check out the swagger and ReDoc endpoints!

Swagger: `/docs`

ReDoc: `/redoc`

To run the tests, you'll need to invoke `pytest` which involves a couple of steps if you aren't using PyCharm.
You'll need to do the following:

- Activate your `poetry` shell
- Export the correct `PYTHONPATH`
- Then run `pytest` from the correct location

So here's the shell commands from no particular environment, adjust them to fit yours.

To activate the `poetry` shell, it's pretty simple.

```shell
poetry shell
```

```shell
export PYTHONPATH=$(pwd)/src:$(pwd)/tests
```

```shell
python -m pytest ./tests
```

Now; all of this assumes you have a database, if you don't you'll need to create one, if you are going to run the API.
However, the unit tests, are actually self-contained and build their own SQLite database and data; that's probably
the easiest way to get started working with the API.

To create the DB, create a blank database in Postgres using your favorite DB access tool. Hopefully it's not `psql`
but if it is, that's great for you.

Once you've created that database you can run the script in `src/db/database.sql` and that should create all the
tables you need. However, this database will be empty, if you want example data look at the `tests/util/populate`
folder to see what the data should look like. If you run any of the tests that data will be populated into `test.db`
and you can look at it there.

At this point you should have a project you can run.

### Unit Tests, Linters and Merge Requests

TLDR; for `run_unit_tests` here's how you get a coverage report.

```shell
poetry shell
```

```shell
export PYTHONPATH=$(pwd)/src:$(pwd)/tests \
  && pytest ./tests \
  && coverage run --rcfile ./pyproject.toml -m pytest ./tests \
  && coverage report --fail-under 50
```

TLDR; for `run_linters` commit your changes, then run the following.

```shell
poetry shell
```

```shell
export PYTHONPATH=$(pwd)/src:$(pwd)/tests
```

```shell
black --config ./pyproject.toml src tests \
  && isort --settings-path ./pyproject.toml .
```

For a merge request, we have two pipelines that run:

- `run_linters`
- `run_unit_tests`

Both have to complete successfully for the MR to be safe to merge. The `run_unit_tests` is self-evident, it runs the
unit tests, and generates code-coverage based one those unit tests, if coverage drops to under 50%, or if the unit
tests fail, the `run_unit_tests` pipeline will fail.

Here's how you can run this locally and see the reports.

Active your `poetry` shell and set your `PYTHONPATH` if you have not done so already.

```shell
poetry shell
```

```shell
export PYTHONPATH=$(pwd)/src:$(pwd)/tests
```

Then from the `poetry` shell from the project root, run the following commands.

```shell
pytest ./tests \
  && coverage run --rcfile ./pyproject.toml -m pytest ./tests \
  && coverage report --fail-under 50
```

For `run_linters` it's a little less obvious, since we have a few installed in the project right now:

- `isort` - Sorts `using` and `import` statements, so you don't have to.
- `black` - Applies PEP8 in a very opinionated way, has been widely adopted, considered a "good" thing
- `flake8` - Another PEP8 based linter; complements `black`
- `pylint` - This actually inspects code for best practices, code duplication, and other more complex issues

So given the above what do we run automatically for MR?

- `isort`
- `black`

These are the two linters we run for every MR. For MRs they run in `--check` or `--check-only` modes, which means
that they fail if the have to produce any changes, that is to say if they have not been run before committing the code.

So here's what you need to do in order for your MR to have the `run_linters` task complete successfully, before you
create your MR.

Active your `poetry` shell and set your `PYTHONPATH` if you have not done so already.

```shell
poetry shell
```

```shell
export PYTHONPATH=$(pwd)/src:$(pwd)/tests
```

Then from the `poetry` shell from the project root, run the following commands.

```shell
black --config ./pyproject.toml src tests \
  && isort --settings-path ./pyproject.toml .
```

### PyCharm the IDE

Ideally, you are working with PyCharm Professional, since it has tons of great features and makes debugging and
running test a breeze. However, in order to do that you need a few Plugins, the following are helpful:

- Pydantic
- Pylint
- .env file support
- .ignore

There are a few others, but that's left up to the reader to adjust to their preference.

From there the only real key is to configure the "Python Interpreter" to use the `poetry` environment you've setup,
and that's pretty straight forward after you've installed the `poetry` plugin.

\*\*\*\*Menu Drilling:

From the app bar, _File  (or PyCharm on mac) -> Settings -> Project: flynet-api -> Python Interpreter -> Gear icon -> Add... -> Poetry Environment (on the left)
-> Poetry Environment (the upper radio button) -> Check install packages from the toml file -> Ok_

Wait some time for the IDE to do stuff, and all the things should be good.

After that you just need a `Python` configuration and point it at `portal.py` and you should be able to hit the little
"Debug" button or the little "Run" button to get the API functional.

One note, make sure you mark the "Sources Root" and the "Tests Root" you can find those settings by right-clicking
in the Project view on the `src` and the `tests` directories and find "Mark Directory as" and select the appropriate
option.

## DB Migrations and Alembic:

We have set up Alembic to create and apply DB migrations now! Hooray! 

### What is an alembic anyway
Alembic kind of works like git for database model changes - instead of commits you have
versions, which are like commits for your database schema. 

You can have branches, too, but we don't really use them.
Instead of checking out a commit, you can upgrade or downgrade your database so that it is at a specific migration 
revision.

Each database revision is defined by a revision script which is an autogenerated python file which includes code to
apply or remove a revision from the database. 

Glancing through these files is important and instructive - you will want to 
ensure these db changes are correct before running them on your precious data!


The migration scripts that define each version are found in:
`src/migrations/versions`

### Env stuff

Alembic needs the same .env file as the portal does to work. For now, we
have simply duplicated the normal .env file in the migrations folder.

*Make sure that the migrations .env file is up-to-date when you run any migration related things! Especially the DB
Connection Settings. I know this means maintaining two env files but such is life for now.*


### How to use it
*Be sure that the api is not running when you run alembic commands*

Some useful commands to manage the migrations state (you'll need to be in poetry shell to run these and PYTHONPATH probably 
needs to be set correctly)

To set PYTHONPATH run the following from the project root.
```shell
export PYTHONPATH=$(pwd)/src:$(pwd)/tests
```

`alembic current` <- View which migration is currently applied to the database. Shows the hash of the current version.
This is kinda like `git status`.

`alembic history` <- View the list of all migrations that exist going back in history. 
Kinda like `git log` but if that showed commits that came after the checked-out one too.

`alembic revision --autogenerate -m "some message"` <- This is how you create a migration revision after you 
have made some changes to the schema

`alembic upgrade head` <- After you create a revision you need to apply it to your database. 
Head means the very newest migration. You can also specify a particular hash to upgrade to instead. *(double-check that the api is stopped before you run this, or alembic will get stuck whiletrying to access the database)*

`alembic downgrade <hash>` <- The inverse of the last one, this one moves you BACK through the revisions, but be warned
that you will lose data if you are undoing the adding of tables and columns and such.

*Warning: If you want to add new tables to the system (and so you made a new schema python file), 
you will need to make sure alembic can find that schema file before running the alembic revision generation.*

*To do this, import that new schema file under `src/schema/alembic.py` like the others.*

##MISC:

- Linux server timezone must be set properly to get the reported on times to be correct for vancouver time:

```
timedatectl set-timezone America/Vancouver

```

- When setting up an api with postgres for the first time, after population, the id increments aren't updated
- This means that when you try to create a record, it fails since id is already in use
- Some SQL commands to fix that:

```sql
alter SEQUENCE airport_id_seq RESTART WITH 100;
alter SEQUENCE flight_logs_id_seq RESTART WITH 100;
alter SEQUENCE user_id_seq RESTART WITH 100;
alter SEQUENCE user_profile_id_seq RESTART WITH 100;

```
