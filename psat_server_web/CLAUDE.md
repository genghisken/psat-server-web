# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A single pip package (`psat-server-web`, root `setup.py`) containing **two independent Django projects** for two separate astronomical transient surveys, sharing a similar underlying MySQL/MariaDB schema:

- `atlas/` — the ATLAS survey web interface. Settings/urls package: `atlas/atlas/`. REST API app: `atlas/atlasapi/`.
- `ps1/` — the Pan-STARRS survey web interface. Settings/urls package: `ps1/psdb/`. REST API app: `ps1/psdbapi/`.

They are structurally parallel (same shape of app: a big `views.py` with most of the page logic, an `accounts` app, an API app) but are **not code-shared** as Python packages — common code is duplicated or reached via a `sys.path.append('../../common')` hack (see Gotchas below), not imports of a shared library.

Each project is a normal Django project with its own `manage.py`, so commands below must be run from inside `atlas/` or `ps1/` as appropriate, not from the repo root.

## Environment / running locally

Dependencies are declared only in the root `setup.py` (`install_requires`) — there is no `requirements.txt`/`pyproject.toml`, and versions are **not pinned to a lockfile**, so installing into a fresh environment can pull newer packages than the codebase was written against (see the django-tables2 gotcha below).

Configuration is read from environment variables via `python-dotenv`'s `load_dotenv()` in each `settings.py` (e.g. `DJANGO_SECRET_KEY`, `DJANGO_MYSQL_DB*`, `DJANGO_DEBUG`, `WSGI_PREFIX`, `API_TOKEN_EXPIRY`, etc. — grep `os.environ.get` in `settings.py` for the full list). Provide these via a `.env` file or an externally-sourced env before running `manage.py`.

Two ways to run it locally:

1. **Docker Compose** (root `docker-compose.yml`/`Dockerfile`) — currently only wires up **atlas** (`atlas-web` + `tests` services), there is no `ps1` service defined. `docker compose up` starts a MariaDB `db`, `adminer`, and `atlas-web`. Requires a `.env` in the repo root and a dummy DB dump at `data/init.sql` (get from another developer — see README.md). Run the atlas test suite with `docker compose up tests` (runs `python manage.py test --keepdb --noinput` from `atlas/`).
2. **Direct/mod_wsgi**, used for testing an actual deployment: `python manage.py collectstatic`, `python manage.py makemigrations <app>`, `python manage.py migrate`, then either `python manage.py runserver` or `./generate_mod_wsgi_apachectl.sh` (present in both `atlas/` and `ps1/`) to generate an Apache config for a closer-to-production test.

## Known gotchas

- **`TcsGravityEventAnnotations.map_iteration` system check error** (`fields.E311`) is a pre-existing, known issue (documented in the repo's root `README.md`) unrelated to any feature work — it blocks `manage.py check`/`makemigrations`/`migrate`/`runserver` by default. Either pass `--skip-checks` on those commands, or apply the one-line fix in the README: in the `TcsGravityAlerts` model, swap which `map_iteration` line is commented out so it has `unique=True`. Confirmed present identically on `ps1/` too (same model shape) — `ps1/psdb/settings.py` silences it via `SILENCED_SYSTEM_CHECKS = ['fields.E311']` since `manage.py test` doesn't accept `--skip-checks` (that flag only applies to `check`/`makemigrations`/`migrate`/`runserver`).
- **Migrations are deliberately not committed to git** — `migrations/` is blanket-ignored in `.gitignore` ("Django migrations. Always run from scratch."). On any environment that doesn't already have generated migration files on disk (a fresh clone, a fresh deploy), you must run `python manage.py makemigrations <app>` yourself before `migrate` — `migrate` alone won't create anything new.
- **`STATIC_ROOT` (`atlas/static/`, `ps1/static/`) is also not committed** (`/static/` in `.gitignore`) — it's a `collectstatic` build artifact. `manage.py runserver` in `DEBUG=True` serves static files directly from `STATICFILES_DIRS` (`site_media/`) without needing this, but a real Apache/mod_wsgi deployment serves `STATIC_ROOT` directly and will 404 on every static asset (including things like Font Awesome CSS and the `celestial.js` sky-map's JSON data files) until `collectstatic` has been run.
- **`django-tables2` is pinned to `2.7.3`** in the root `setup.py` — do not casually bump it. Every `django_tables2.Table` subclass across both projects that sets `Meta.template_name = "bootstrap4_django_tables2_atlas.html"` (a template shared between `atlas/` and `ps1/`) depends on a custom `{% querystring %}` tag that only exists in django-tables2's 2.x series. Django 5.1 added its own builtin `{% querystring %}` tag with different (stricter) syntax; django-tables2 3.0 renamed its own tag to `querystring_replace` to avoid the collision. Installing django-tables2 >= 3.0 alongside this codebase's unmodified templates breaks pagination/sorting links across every paginated table view with a `TemplateSyntaxError`. Upgrading it requires updating that shared template's tag calls, not just bumping the version.
- Several page-serving view functions exist in multiple generations side by side (e.g. plain vs. "quickview" vs. "BootstrapPlotly"/"plotly" variants of the same followup/candidate pages). Check which one is actually wired up in the current `urls.py`/linked from templates before assuming a given view function is the live one — older variants are often left in place rather than deleted.

## Cross-cutting architecture

**The `accounts` app** (present in both `atlas/` and `ps1/`, same design in each) owns auth beyond Django's defaults:
- `UserProfile` — avatar image (stored as both a file and a base64 copy for cheap template rendering) and a `password_unuseable_fl` flag that forces a password change on next login.
- `GroupProfile` — one per `auth.Group`, carries `token_expiration_time` (API token lifetime for members of that group) and `api_write_access` (whether the group's API tokens can perform writes).
- `GlobalPermissions` — a fieldless dummy model whose sole purpose is to define the `has_write_access` Django permission.
- `has_write_permissions(user)` (`accounts/permissions.py`) is the single check used to gate **write actions in plain Django views** (not DRF): staff/superuser, or a user explicitly granted `has_write_access` (directly, or by permission on a group they belong to). The pattern in `views.py` is: fetch the object, compute `can_edit_fl = has_write_permissions(request.user)`, gate the mutating branch with `elif can_edit_fl:` (falling through harmlessly otherwise — it does not raise), and pass `can_edit_fl` into the template context so the template disables the submit control and shows a "no permission" notice rather than hiding the form entirely.
- Only a small number of view functions in each project's `views.py` actually mutate data (look for `.save()`/`.update()`/`.delete()` calls) — most of the many view functions are read-only pages, even though most require login.

**The `<project>api` apps** (`atlasapi`, `psdbapi`) are DRF, token-authenticated, with their own layer on top of Django's default token auth:
- `ExpiringTokenAuthentication`/`QueryAuthentication` (header vs. `?token=` query param) look up `request.user.groups.first().profile.token_expiration_time` to decide if a token has expired, falling back to `settings.TOKEN_EXPIRY` if the user has no group; staff users' tokens never expire.
- `HasReadAccess`/`HasWriteAccess` permission classes gate write HTTP methods based on `GroupProfile.api_write_access` (or staff), independently of the `accounts.has_write_access` Django permission used by the plain web views above — the two systems are not linked.
- Token issuance/refresh goes through a custom `ObtainExpiringAuthToken` view rather than DRF's stock `obtain_auth_token`, since refreshing needs to rotate the token and reset its expiry clock once the old one has expired.
- A user's effective API token lifetime and write access come from `user.groups.first()` — a user in zero groups always gets `settings.TOKEN_EXPIRY` and no write access regardless of individual permissions.

**Shared, non-imported code**: `common/` at the repo root holds Python modules (e.g. `psat_api_client.py`) that both `atlas/atlas/views.py` and `ps1/psdb/views.py` reach via `sys.path.append('../../common')` followed by a plain `import` — this is relative to the process's current working directory, not the file's location, so it is fragile to how/where the server is actually launched from. `schema/` at the repo root holds the raw SQL DDL for the shared database schema.

## Porting the Pan-STARRS (ps1) API up to ATLAS API parity

`ps1/psdbapi` is being brought up to parity with `atlas/atlasapi`, deliberately excluding all VRA (Virtual Research Assistant) endpoints/models — VRA is ATLAS-only. See `docs/atlas-ps1-api-reference.md` (repo root) for the endpoint-by-endpoint gap list, the model/field-name traps (e.g. `TcsObjectGroups.object_group_id` is a plain int on ATLAS but a ForeignKey on ps1), and suggested porting order. Read it before touching either `atlasapi/` or `psdbapi/`, and update it if the gap list changes.
