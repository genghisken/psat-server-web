# psat-server-web
Python 3 web interface for the Pan-STARRS and ATLAS surveys.

To install:

pip install psat-server-web

Once installed, don't forget to add the "data" symlinks in the:

site-packages/psat\_server\_web/atlas/media/images
site-packages/psat\_server\_web/ps1/media/images

directories which point to the location of the image stamps.

--- 

# Local development version 

A localised development instance can be run with docker compose. You will need a 
`.env` file in your repository root to define some environment variables, 
looking something like:

``` .env
# Django settings
SECRET_KEY={YOUR_SECRET_KEY_HERE}
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]

# MySQL/MariaDB settings
MYSQL_ROOT_USER=root
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=atlas
MYSQL_USER=atlas
MYSQL_PASSWORD=atlas
MYSQL_PORT=3306
MYSQL_TEST_DATABASE=atlas_test
MYSQL_TEST_PORT=3306
MYSQL_TEST_USER=root
MYSQL_TEST_PASSWORD=root

DJANGO_MYSQL_DBUSER=atlas
DJANGO_LASAIR_TOKEN=

```

Several of the values are omitted but aren't necessary to run a development 
environment. Also ruch simple passwords should not be used in production, but this should get you something running locally. Hopefully it's then as simple as running the following:

``` bash
docker compose up
```

Which will start 4 services, comprised of:
- `db` - A MariaDB instance. By default served at `localhost:3036` 
- `atlas-web` - A mod-wsgi instance to serve the django front end. By default 
  served at `localhost:8086` and requires `db` to be running.
- `adminer` - A web interface for interacting with the db. By default served at 
  `localhost:8080` and requires `db` to be running.
- `tests` - A single-use run of the unit tests, requires `db` to be running.

Each of these services can be run independently with 

``` bash
docker compose up {service_name}
```

So if for example you just wanted to run the tests you could put `docker compose up tests`
and it would first check that `db` is running, start it if it is not already up, 
and so a single run of the unit tests. 

## A dummy database

There are a few things you will likely need to do to get a fully working version 
of the web-server so as to make your local version useful, namely: 
1. Get a dummy database dump .sql file from one of the developers and place it into `data/init.sql`
2. [Optional] Get an image dump and place it into `data/db_data/`
3. Fix a mild issue with the database model (see next section)

If you are having problems with any of this, contact one of the developers.

### Issue with `TcsGravityEventAnnotations.map_iteration`

If you are getting an error along the lines of 

```
atlas-web-1  | ERRORS:
atlas-web-1  | atlas.TcsGravityEventAnnotations.map_iteration: (fields.E311) 'TcsGravityAlerts.map_iteration' must be unique because it is referenced by a foreign key.
atlas-web-1  | 	HINT: Add unique=True to this field or add a UniqueConstraint (without condition) in the model Meta.constraints.
```

Then you may need to make an adjustment to the models, specifically by 
uncommenting the line declaring `TcsGravityAlerts.map_iteration` which adds a 
unique `kwarg`, and commenting the line without the unique `kwarg`, should solve 
the problem. Specifically, the lines should look like 
```
# map_iteration = models.CharField(max_length=100, blank=True, null=True)
map_iteration = models.CharField(max_length=100, blank=True, null=True, unique=True)
``` 
This is within the `TcsGravityAlerts(models.Model)` class. Again, please speak 
to one of the developers if this is unclear. 

