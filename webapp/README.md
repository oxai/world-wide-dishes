# Development

## Install dependencies
```bash
conda create -n wwd_app python=3.10
conda activate wwd_app
pip install -r requirements.txt
python manage.py createcachetable
```

## Create a .env file
Follow the example shown in `.env.example` to create a `.env` file in the same directory.
DEBUG should be set to `True` for development and `False` for production.

## Create a database (you only need to do once)
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py createcachetable
```

## Run the server
```bash
python manage.py runserver
```

# Development
When you are developing, your local .env file should be set as shown in `.env.dev.example`. Importantly,
```
DEBUG=true
DEV_MODE=true
USE_CLOUD_SQL_AUTH_PROXY=false
```

and the `DATABASE_URL` and `DEPLOY_URL` should be commented out.

## Start proxy connection to Postgres Database on Google Cloud
By default, during local development django will create a local `.sqlite` database. If you need to connect to the remote database, change the `.env` setting to include
```
USE_CLOUD_SQL_AUTH_PROXY=true
DATABASE_URL=<your database url>
```

and run the following in a separate terminal.

```bash
./cloud-sql-proxy <project_name>:<region_name>:<database_name>
```

# Deployment
When you deploy, your local .env file should be set to the following:
```
DEBUG=false
DEV_MODE=true
USE_CLOUD_SQL_AUTH_PROXY=true
```

and the `DATABASE_URL` and `DEPLOY_URL` should be uncommented. 

When you deploy, you should run the following from this directory:

```bash
python manage.py collectstatic      # collects static files in a local directory called 'staticfiles'
python manage.py compress --force   # creates `compressed/manifest.json`
gcloud storage cp --recursive staticfiles/** gs://<bucket-name>   # this syncs the files collected in 'staticfiles' to the google storage bucket 
```

In a separate terminal, connect to the remote database by running
```bash
./cloud-sql-proxy <project-name>:<region-name>:<database-name>
```

Back in the main terminal, run
```bash
python manage.py migrate
```
Hopefully you won't have to makemigrations since the migration files should already be committed.

Finally, run
```
gcloud app deploy --quiet
```
This uploads all files under this directory that is not escaped by '.gcloudignore', including the 'manifest.json' file,  to the GCP instance.

To check for logs, 
```bash
gcloud app logs tail -s default
```

## Downloading all dish images
```
gsutil -m cp -r "gs://<bucket-name>/dishes" .
```

# Resources
### Learn Django
- [Official Django Tutorial](https://docs.djangoproject.com/en/5.0/intro/)
- [A Complete Beginner's Guide to Django](https://simpleisbetterthancomplex.com/series/beginners-guide/1.11/) (Slightly outdated but easy to follow)
- [Django Tutorial by Mozilla](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/)

### User authentication
#### Creating a custom user model
- https://testdriven.io/blog/django-custom-user-model/

### Libraries
- [Django Select2](https://django-select2.readthedocs.io/en/latest/)
- [Django Guest User](https://django-guest-user.readthedocs.io/en/latest/)