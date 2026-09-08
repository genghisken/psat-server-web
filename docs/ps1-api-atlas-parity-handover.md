# ps1 API — ATLAS Parity: Session Handover

**Date:** 2026-09-08
**Branch:** `kws-claude/atlas-api-equivalence` (based on `master` @ `d678612`, **not pushed**)
**Status:** All 9 planned tasks complete, 27/27 tests passing. Not yet code-reviewed by a human beyond Ken's live participation during the session.

## What this was

Brought `ps1/psdbapi` (the Pan-STARRS REST API) up to functional parity with `atlas/atlasapi`, covering every ATLAS endpoint except the VRA (Virtual Research Assistant) ones — VRA has no Pan-STARRS equivalent and was explicitly out of scope throughout.

Two planning documents from earlier in the session are the primary references:
- `docs/atlas-ps1-api-reference.md` — the endpoint gap analysis and model/field-name traps this work was built against.
- `docs/superpowers/plans/2026-09-08-ps1-api-atlas-parity.md` — the 9-task implementation plan. **Note:** the plan's Task 1 originally called for a separate test database and a docker-compose change; both were superseded during execution (see below) — the plan file itself was not edited to reflect this, so read this handover doc's Testing section as the authoritative version of what actually happened.

## Commits (9, oldest first)

```
14b38b1 test: stand up ps1 test harness, run directly against panstarrs
584f26a feat: add api/objectlist/ endpoint to ps1 API
e3e167e feat: add api/objectgroups/ insert endpoint to ps1 API
10815bc feat: add api/objectgroupsdelete/ endpoint to ps1 API
e905368 feat: add api/objectgroupslist/ endpoint to ps1 API
be9b55c feat: add api/externalxmlist/ endpoint to ps1 API
e76d0cc feat: add api/objectdetectionlist/ endpoint to ps1 API
0f5e318 feat: add api/objects/ endpoint to ps1 API
412bb0e feat: log ps1 API requests via TcsAPIUsageLog, matching ATLAS's LoggingAPIView
```

18 files changed, ~955 insertions:

| File | Change |
|---|---|
| `psat_server_web/CLAUDE.md` | Committed to git for the first time (existed on disk but was never tracked) + one amendment about the E311 gotcha applying to ps1 too |
| `psat_server_web/ps1/psdb/apiutils.py` | **New.** Query-helper layer backing the API: `buildObjectListQueryFilter`, `getObjectList`, `getCustomListObjects`, `getExternalCrossmatchesList`, `transientObjectApi` |
| `psat_server_web/ps1/psdb/models.py` | Added `TcsAPIUsageLog` (the one managed, non-`managed=False` model in this file) |
| `psat_server_web/ps1/psdb/settings.py` | Added `TEST_RUNNER`, `SILENCED_SYSTEM_CHECKS` |
| `psat_server_web/ps1/psdb/testrunner.py` | **New.** `NoDbCreationTestRunner` |
| `psat_server_web/ps1/psdbapi/serializers.py` | All the commented-out ATLAS-derived stubs replaced with real serializers; `ObjectDetectionListSerializer`/`ExternalCrossmatchesListSerializer` written fresh (no stub existed) |
| `psat_server_web/ps1/psdbapi/urls.py` | 7 new `path()` entries |
| `psat_server_web/ps1/psdbapi/views.py` | 7 new view classes, `LoggingAPIView` base class, every view (old and new) now subclasses it |
| `psat_server_web/ps1/tests/` | **New directory**, didn't exist before this session — 8 test files, 27 tests total |

## Endpoints added

| Endpoint | Method | Auth | Notes |
|---|---|---|---|
| `api/objectlist/` | GET/POST | read | Filtered object listing |
| `api/objectgroups/` | POST | write | Insert into a custom group |
| `api/objectgroupsdelete/` | POST | write | Remove from a custom group |
| `api/objectgroupslist/` | GET/POST | read | List custom-group membership |
| `api/externalxmlist/` | GET/POST | read | External crossmatch lookup by designation |
| `api/objectdetectionlist/` | POST | write | Snooze/unsnooze (moves an object between detection lists) — **only list `4` is a valid target right now**, see below |
| `api/objects/` | GET/POST | read | Single/multi-object detail: lightcurve, forced photometry, Sherlock/TNS crossmatches |

`api/cone/` and `api/auth-token/` were already at parity before this session — untouched.

## Key decisions a new collaborator needs to know

These were all worked out live with Ken during the session and are **not** fully captured in the original plan document — read this section before assuming the plan file is ground truth.

### 1. Tests run directly against the real `panstarrs` database — there is no separate test database

The `panstarrs` MySQL user has no `CREATE DATABASE` privilege (confirmed: attempting it fails with `1044 Access Denied`), and even if it could create one, most models here are `managed = False` (mapped onto hand-written schema in `schema/*.sql`, not Django migrations) — a fresh empty database would have none of that schema.

Fix: `ps1/psdb/testrunner.py`'s `NoDbCreationTestRunner` overrides `setup_databases`/`teardown_databases` to no-ops. `ps1/psdb/settings.py` sets `TEST_RUNNER` to it. Tests run straight against `DATABASES['default']` — the real `panstarrs` DB. **Ken confirmed this is acceptable** — he holds a full backup of `panstarrs` and is fine with tests writing to it.

### 2. Several core tables are MyISAM — TestCase's automatic rollback does NOT protect them

`tcs_transient_objects`, `tcs_object_group_definitions`, and `tcs_object_groups` are MyISAM (non-transactional), confirmed via `information_schema.TABLES`. Django's `TestCase` wraps each test in a DB transaction and rolls it back — but that only works for InnoDB tables. Any row a test creates in these three tables **stays permanently** unless explicitly deleted.

Fix: every test class that touches these tables has an explicit `tearDown()` that deletes exactly what `setUp()` created. **If you add new tests against these tables, you must add `tearDown()` cleanup too** — there is no automatic safety net.

### 3. Test fixture IDs use deliberately out-of-real-data ranges, split by column type

- `tcs_transient_objects.id` — `bigint`, real IDs are ~10^18-scale IPP-style identifiers. Test fixtures use `900000001`–`900000008` (one per task that needed a transient row) — confirmed zero collision risk.
- `tcs_object_group_definitions.id` — **`smallint unsigned`, max 65535**, real data currently tops out at 102. Test fixtures use `60001`–`60005`. **Do not reuse the `900000001`-style range for this table** — it will overflow.
- `tcs_forced_photometry.id`, `sherlock_crossmatches.id`, `tcs_cross_matches_external.id` — all `bigint`, safe with the `900000001`-style range.

### 4. `TcsTransientObjects.date_inserted` is required with no default

Not obvious from the Django model alone — the real DB column is `NOT NULL` with no default. Every test fixture creating a `TcsTransientObjects` row passes `date_inserted=now()` (from `django.utils.timezone`) explicitly.

### 5. The FK gotcha (documented in `docs/atlas-ps1-api-reference.md`, confirmed throughout)

`TcsObjectGroups.object_group_id` is a plain `IntegerField` on ATLAS but a `ForeignKey` on ps1 — inserts/filters need `object_group_id_id=<int>`, not `object_group_id=<int>`. Applied consistently across Tasks 3–5.

### 6. Pre-existing Django system-check issue, silenced

`TcsGravityEventAnnotations.map_iteration` (`fields.E311`) was already a known ATLAS-side issue (documented in `CLAUDE.md` before this session) but had never been exercised on ps1 since ps1 had zero tests before this session. Confirmed identical on ps1. `manage.py test` doesn't accept `--skip-checks` the way `check`/`migrate`/etc. do, so it's silenced via `SILENCED_SYSTEM_CHECKS = ['fields.E311']` in `ps1/psdb/settings.py` instead. (An earlier draft also silenced a `fields.E001` that turned out not to actually exist — checked directly and removed before committing.)

### 7. `getLightcurvePoints`/`getLightcurveNonDetections` need `djangoRawObject=`, not `conn=connection`

A real bug caught while building Task 8: passing Django's ORM `connection` object as `conn=` breaks (`cursor() takes 1 positional argument but 2 were given`) — these functions expect either a genuine raw MySQLdb connection or a `djangoRawObject=` (a raw-query model like `CustomLCPoints`). Fixed to use `djangoRawObject=CustomLCPoints`, matching how `ps1/psdb/lightcurvequeries.py` already calls them elsewhere.

### 8. `api/objects/` response shape is a new design, not a port

ATLAS's single-object endpoint dumps raw rows from its DDC (difference-detection-chain) pipeline, which ps1 has no equivalent of. ps1's version builds `lc`/`lcnondets` from `commonqueries.getLightcurvePoints`/`getLightcurveNonDetections` as simple `{mjd, mag, magerr}`/`{mjd}` dicts, and `fp` from a plain `TcsForcedPhotometry` ORM query (skipping `uJy`/`duJy`/`texp` — ps1's model doesn't have those convenience properties). **Ken reviewed and approved this design directly during the session** ("Your proposed solution is exactly what I would have done").

### 9. `api/objectdetectionlist/`'s valid target list is `(4,)` only, per Ken

ATLAS's equivalent hardcodes `(3, 4, 12)`. Per Ken: ps1 has no equivalent of ATLAS's list `12`, and ps1's list `3` ("Possible Candidates") is used differently — so only `4` ("Not Yet Eyeballed") is currently valid. `VALID_TARGET_LISTS = (4,)` in `ObjectDetectionListSerializer`. Expand later if more targets are needed — this was an explicit "for now" scoping call, not a technical constraint.

### 10. `TcsAPIUsageLog` required a real schema change

Unlike every other model touched this session, `TcsAPIUsageLog` is **managed** (not `managed = False`) — its table didn't exist in `panstarrs` before this session. Created via `python manage.py makemigrations psdb && python manage.py migrate psdb` against the live `panstarrs` database — **confirmed with Ken before running**, since this is actual DDL, not just test row churn. The migration file (`ps1/psdb/migrations/0001_initial.py`) is gitignored per this repo's existing convention ("migrations are deliberately not committed... always run from scratch") — **it will need to be regenerated with the same two commands on any other environment** (a fresh clone, another collaborator's machine, a deploy) before `TcsAPIUsageLog`-touching code will work there.

## How to run the tests

No Docker involved anywhere in this work — Ken was explicit about that (twice, across sessions).

```bash
# Anaconda env "panstarrs311" already exists (created ahead of this session)
source /path/to/anaconda3/etc/profile.d/conda.sh
conda activate panstarrs311

cd psat_server_web/ps1
source ~/.config/django/django_env_panstarrs311   # DB creds + other required env vars
python manage.py test tests.psdbapi --noinput
```

Requires a local MariaDB instance reachable at the host/port in that env file, with the `panstarrs` database already populated with real/test data (it's a working database with a backup, not an empty schema).

If `TcsAPIUsageLog`'s table doesn't exist yet in whatever DB you're pointing at:
```bash
python manage.py makemigrations psdb --noinput
python manage.py migrate psdb --noinput
```

## What's explicitly NOT done

- **VRA endpoints** (`api/vrascores*`, `api/vratodo*`, `api/vrarank*`) — deliberately excluded, no Pan-STARRS equivalent exists. Do not add these unless a future task explicitly asks for them.
- **docker-compose integration** — the original plan's Task 1 called for extending the docker-compose `tests` service; this was dropped per Ken's no-docker preference. There is currently no CI-style automated test run for `ps1` — tests are run locally against `panstarrs` as above.
- **Code review** — nothing in this branch has been through a formal review pass (`/code-review`, a PR review, etc.) beyond Ken's live participation task-by-task during the session. Worth doing before merging.
- **The two pre-existing model bugs are silenced, not fixed** — `TcsGravityEventAnnotations.map_iteration`'s missing `unique=True` on its FK target is still there under the hood (see #6 above); a real fix (matching the one-line fix already documented in the repo's README for the ATLAS side) is a reasonable follow-up but was out of scope here.

## Suggested next steps for whoever picks this up

1. Read `docs/atlas-ps1-api-reference.md` for the original gap analysis and field-name trap list.
2. Run the test suite locally (above) to confirm it's still green before making changes.
3. Decide whether/when to push `kws-claude/atlas-api-equivalence` and open a PR — nothing has been pushed yet.
4. Consider a `/code-review` pass before merging, given the volume of new code and that it touches a real database's schema.
