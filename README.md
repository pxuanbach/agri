# AgriBlock-Backend


## Features

* FastAPI
* React Admin
* SQLAlchemy and Alembic
* Pre-commit hooks (black, autoflake, isort, flake8, prettier)
* Github Action
* Dependabot config
* Docker images


## Good to know

The frontend of this project uses React Admin. Follow the quick tutorial to understand how [React Admin](https://marmelab.com/react-admin/Tutorial.html) works.

## Requirement before starting
* Install Docker
* Install Postgresql
* Install FastApi
    - https://fastapi.tiangolo.com/tutorial/
* Install SQLAlchemy and Alembic

## Step 1: Getting started

Start a local development instance with docker-compose

```bash
docker-compose up -d

# Run database migration
docker-compose exec backend alembic upgrade head

# Create database used for testing
docker-compose exec postgres createdb apptest -U postgres
```

Now you can navigate to the following URLs:

- Backend OpenAPI docs: http://localhost:9000/docs/


### Step 2: Setup pre-commit hooks and database

Keep your code clean by using the configured pre-commit hooks. Follow the [instructions here to install pre-commit](https://pre-commit.com/). Once pre-commit is installed, run this command to install the hooks into your git repository:

```bash
pre-commit install
```

### Local development

The backend setup of docker-compose is set to automatically reload the app whenever code is updated. However, for frontend it's easier to develop locally.

```bash
docker-compose stop frontend
cd frontend
yarn
yarn start
```


### Rebuilding containers

If you add a dependency, you'll need to rebuild your containers like this:

```bash
docker-compose up -d --build
```

### Rengerate front-end API package

Instead of writing frontend API client manually, OpenAPI Generator is used. Typescript bindings for the backend API can be recreated with this command:

```bash
yarn genapi
```

### Database migrations


These two are the most used commands when working with alembic. For more info, follow through [Alembic's tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html).

```bash
# Auto generate a revision
docker-compose exec backend alembic revision --autogenerate -m 'message'

# Apply latest changes
docker-compose exec backend alembic upgrade head
```

### Backend tests
Backend uses a hardcoded database named apptest, first ensure that it's created

```bash
docker-compose exec postgres createdb apptest -U postgres
```

Then you can run tests with this command:

```bash
docker-compose exec backend pytest
```

### Create supper user
```bash
docker compose exec backend python create_supper_user.py
```


### Postgresql Tutorial

1. Connect to postgres user 
```bash
psql -h localhost -p 5432 -U postgres
```
2. Show all database
```
\l
```
3. In `postgres=#` connect with `app/apptest` database by
```
\c apptest
```
4. Show all table
```
\dt;
```
5. Show table detail
```
\d [table name]
```
6. Show all relations of database
```
\d+;
```
7. Get data from table with sql query
```
select * from [table name]
select * from users;
delete from users where email='reactjs.tisoha@gmail.com';
update users set full_name='Pham' where email='xuanbach123@gmail.com';
delete role where name='customer';
```
