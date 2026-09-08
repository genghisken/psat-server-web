# Pan-STARRS (ps1) API — ATLAS Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring `ps1/psdbapi` up to functional parity with `atlas/atlasapi`, covering every ATLAS API endpoint except the VRA (Virtual Research Assistant) ones, which have no Pan-STARRS equivalent and are explicitly out of scope.

**Architecture:** `ps1/psdbapi` (DRF views/serializers/urls) gains one new endpoint per task, each backed by new query-helper functions in a new `ps1/psdb/apiutils.py` (mirroring `atlas/atlas/apiutils.py`, VRA functions excluded). Auth/permissions/throttling are already at parity and untouched. Each task is a vertical slice: helper function(s) → serializer → view → url → tests, independently deployable and reviewable.

**Tech Stack:** Django 5.x, Django REST Framework, MySQL/MariaDB (`managed = False` models over an existing shared schema), `django.test.TestCase` + DRF's `APIClient` for tests (`unittest`-style, run via `manage.py test`).

**Spec:** `docs/atlas-ps1-api-reference.md` (repo root) — the endpoint gap list and model/field-name traps this plan implements against. No separate design spec was written; the ATLAS implementation (`atlas/atlasapi/`, `atlas/atlas/apiutils.py`) serves as the reference implementation for every task except Task 8, which is a deliberate re-design (see that task's notes).

## Global Constraints

- **No VRA.** Do not add `TcsVra*` models, `api/vrascores*`, `api/vratodo*`, `api/vrarank*`, or any VRA-derived fields to ps1. If a task below looks like it should include a VRA-shaped filter (e.g. `vra_gte`/`vra_lte`), it is deliberately omitted — do not add it back "for consistency" with ATLAS.
- **Collab mode (default, per `~/.claude/CLAUDE.md`).** Implement code directly. Do **not** add or edit comments/docstrings, except a single-line flag on genuinely new logic that needs human review, e.g. `# Claude wrote this (collab mode, unreviewed) — <date>`. Do not backfill docstrings on existing ATLAS-derived code being ported.
- **Commit trailers.** Every commit in this plan ends with:
  ```
  Oversight-Mode: collab
  Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
  Claude-Session: <session URL>
  ```
- **The commented-out block in `ps1/psdbapi/serializers.py`** (everything after `ConeSerializer`, currently lines ~90–512) is reference-only. As each serializer below is implemented, delete its corresponding commented block — do not leave it commented out alongside the new code.
- **Field-name deltas to apply everywhere:** `AtlasDiffObjects` → `TcsTransientObjects`; `atlas_designation` → `ps1_designation`; import root `atlas.*` → `psdb.*`/`psdbapi.*`.
- Tests run with `cd ps1 && python manage.py test psdbapi --keepdb --noinput` against a MySQL/MariaDB instance with the shared schema loaded (`schema/create_schema.sql` + friends) — same DB the `atlas` tests already use. Task 1 wires this up so `--keepdb` is safe to reuse across the whole plan.

---

## File Structure

| File | Status | Responsibility |
|---|---|---|
| `ps1/psdb/apiutils.py` | **new** | DB-query helpers backing the API (`buildObjectListQueryFilter`, `getObjectList`, `getCustomListObjects`, `getExternalCrossmatchesList`, `transientObjectApi`) |
| `ps1/psdbapi/serializers.py` | modify | Replace commented stubs with real serializers, one per task |
| `ps1/psdbapi/views.py` | modify | Add one view class per task; Task 9 adds `LoggingAPIView` base |
| `ps1/psdbapi/urls.py` | modify | Add one `path()` per task |
| `ps1/psdb/models.py` | modify (Task 9 only) | Add `TcsAPIUsageLog` |
| `ps1/psdb/settings.py` | modify (Task 1 only) | Add `DATABASES['default']['TEST']` |
| `docker-compose.yml` | modify (Task 1 only) | Extend `tests` service to also run ps1's suite |
| `ps1/tests/psdbapi/test_*.py` | **new** | One test file per task |

---

### Task 1: ps1 test harness parity

**Files:**
- Create: `ps1/tests/__init__.py`
- Create: `ps1/tests/psdbapi/__init__.py`
- Create: `ps1/tests/psdbapi/test_authentication.py`
- Modify: `ps1/psdb/settings.py` (add `TEST` sub-dict to `DATABASES['default']`)
- Modify: `docker-compose.yml` (extend the `tests` service)

**Interfaces:**
- Consumes: `psdbapi.authentication.ExpiringTokenAuthentication` (already exists, untested, identical to ATLAS's).
- Produces: nothing new consumed by later tasks — this task's deliverable is "ps1 has a working, running test suite," proven by the tests it adds.

ps1 currently has **no** `ps1/tests/` directory at all, and `ps1/psdb/settings.py`'s `DATABASES` has no `'TEST'` block (ATLAS's does — that's what lets `manage.py test` pick a separate test database via `DJANGO_MYSQL_TEST_DB*` env vars). The docker-compose `tests` service also only runs the ATLAS suite (`cd ../atlas && python manage.py test`). This task closes all three gaps using ATLAS's already-working setup as the template, and adds a first real test for the one piece of ps1 API code that already exists and is currently untested.

- [ ] **Step 1: Write the failing test**

`ps1/tests/__init__.py` and `ps1/tests/psdbapi/__init__.py`: empty files.

`ps1/tests/psdbapi/test_authentication.py`:
```python
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import now, timedelta
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

from psdbapi.authentication import ExpiringTokenAuthentication
from accounts.models import GroupProfile


class TokenAuthenticationUserTests(TestCase):
    def setUp(self):
        self.week_group = Group.objects.create(name="Weekly Expiring")
        GroupProfile.objects.create(group=self.week_group, token_expiration_time=timedelta(weeks=1))
        self.no_group_user = User.objects.create_user(username="no_group_user", password="password")
        self.week_user = User.objects.create_user(username="week_user", password="password")
        self.week_user.groups.add(self.week_group)
        self.no_group_token = Token.objects.create(user=self.no_group_user)
        self.week_token = Token.objects.create(user=self.week_user)
        self.auth = ExpiringTokenAuthentication()

    def test_default_expiry_for_user_with_no_group(self):
        self.assertEqual(
            self.auth.authenticate_credentials(self.no_group_token.key),
            (self.no_group_user, self.no_group_token),
        )
        self.no_group_token.created = now() - timedelta(days=settings.TOKEN_EXPIRY + 1)
        self.no_group_token.save()
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate_credentials(self.no_group_token.key)

    def test_group_expiry_is_honoured(self):
        self.assertEqual(
            self.auth.authenticate_credentials(self.week_token.key),
            (self.week_user, self.week_token),
        )
        self.week_token.created = now() - timedelta(weeks=2)
        self.week_token.save()
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate_credentials(self.week_token.key)
```

- [ ] **Step 2: Wire up the test database and run to see the real failure mode**

In `ps1/psdb/settings.py`, find the `DATABASES` block:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DJANGO_MYSQL_DBNAME'),
        'USER': os.environ.get('DJANGO_MYSQL_DBUSER'),
        'PASSWORD': os.environ.get('DJANGO_MYSQL_DBPASS'),
        'HOST': os.environ.get('DJANGO_MYSQL_DBHOST'),
        'PORT': int(os.environ.get('DJANGO_MYSQL_DBPORT')),
    }
}
```
Replace with:
```python
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DJANGO_DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.environ.get('DJANGO_MYSQL_DBNAME'),
        'USER': os.environ.get('DJANGO_MYSQL_DBUSER'),
        'PASSWORD': os.environ.get('DJANGO_MYSQL_DBPASS'),
        'HOST': os.environ.get('DJANGO_MYSQL_DBHOST'),
        'PORT': int(os.environ.get('DJANGO_MYSQL_DBPORT')),
        'TEST': {
            'NAME': os.environ.get('DJANGO_MYSQL_TEST_DBNAME'),
            'PORT': os.environ.get('DJANGO_MYSQL_TEST_DBPORT'),
            'USER': os.environ.get('DJANGO_MYSQL_TEST_DBUSER'),
            'PASSWORD': os.environ.get('DJANGO_MYSQL_TEST_DBPASS'),
        }
    }
}
```

Run: `cd ps1 && DJANGO_MYSQL_TEST_DBNAME=... DJANGO_MYSQL_TEST_DBUSER=... DJANGO_MYSQL_TEST_DBPASS=... DJANGO_MYSQL_TEST_DBPORT=... python manage.py test psdbapi --keepdb --noinput` (same env var names ATLAS's `tests` docker service already uses, pointed at the same shared test DB — the schema is shared per `psat_server_web/CLAUDE.md`).

Expected: this should actually **pass** already, since it only exercises existing, correct code — this step confirms the harness itself works end-to-end (DB connects, app is discovered, tests run) before Task 2 onward starts relying on it. If it fails, the failure is infrastructural (missing `ps1` entry in `INSTALLED_APPS` test discovery, DB connectivity, etc.) and must be fixed here, not deferred.

- [ ] **Step 3: Extend the docker-compose `tests` service**

In `docker-compose.yml`, the `tests` service's `command` currently ends with `cd ../atlas && python manage.py test --keepdb --noinput`. Extend it to also run ps1's suite against the same shared test DB, and mount the ps1 app/test directories the same way `atlasapi`/`atlas`/`tests` are mounted for ATLAS:

```yaml
  tests:
    build: .
    image: local/psat-server-web
    command: >
      bash -c "
      python manage.py makemigrations --noinput && 
      mysql -h db -u root -p${MYSQL_ROOT_PASSWORD} < sql/init.sql &&
      cd ../schema &&
      mysql -h db -u root -p${MYSQL_ROOT_PASSWORD} ${MYSQL_TEST_DATABASE} < create_schema.sql &&
      cd ../atlas &&
      python manage.py test --keepdb --noinput &&
      cd ../ps1 &&
      python manage.py makemigrations --noinput &&
      python manage.py test --keepdb --noinput
      || exit $?"
    volumes:
      - ./data/db_data:/images 
      - ./psat_server_web/atlas/atlasapi:/app/psat_server_web/atlas/atlasapi
      - ./psat_server_web/atlas/atlas:/app/psat_server_web/atlas/atlas
      - ./psat_server_web/atlas/accounts:/app/psat_server_web/atlas/accounts
      - ./psat_server_web/atlas/tests:/app/psat_server_web/atlas/tests
      - ./psat_server_web/schema:/app/psat_server_web/schema
      - ./docker/init.sql:/app/psat_server_web/atlas/sql/init.sql
      - ./psat_server_web/ps1/psdbapi:/app/psat_server_web/ps1/psdbapi
      - ./psat_server_web/ps1/psdb:/app/psat_server_web/ps1/psdb
      - ./psat_server_web/ps1/tests:/app/psat_server_web/ps1/tests
    # ports/depends_on/environment unchanged from current file — DJANGO_MYSQL_TEST_DB* env vars
    # already present are reused as-is by ps1/psdb/settings.py's new TEST block.
```
(Only the `command` and `volumes` keys change; leave `ports`, `depends_on`, and `environment` as they are in the current file.)

- [ ] **Step 4: Run the full docker test loop**

Run: `docker compose up tests`
Expected: both the `atlas` suite and the new `ps1` suite (currently just `test_authentication.py`) report `OK`.

- [ ] **Step 5: Commit**

```bash
git add ps1/tests ps1/psdb/settings.py docker-compose.yml
git commit -m "$(cat <<'EOF'
test: stand up ps1 test harness, wire into docker-compose tests service

Oversight-Mode: collab
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: <session URL>
EOF
)"
```

---

### Task 2: `api/objectlist/` — `ObjectListView`

**Files:**
- Create: `ps1/psdb/apiutils.py`
- Modify: `ps1/psdbapi/serializers.py` (replace the commented `ObjectListSerializer` stub, lines ~119–136)
- Modify: `ps1/psdbapi/views.py`
- Modify: `ps1/psdbapi/urls.py`
- Test: `ps1/tests/psdbapi/test_object_list_filters.py`

**Interfaces:**
- Produces (in `psdb/apiutils.py`, consumed by Tasks 2, 5): `OBJECT_LIST_FIELD_TO_LOOKUP: dict[str, str]`, `buildObjectListQueryFilter(validated_data: dict) -> dict`, `getObjectList(request, listId, getCustomList=False, dateThreshold=None, queryFilter=None) -> list[dict]`.
- Consumes: `psdb.views.followupClassList` (list of 9 `WebViewFollowupTransients*` classes, index 0–8 — **note this is a different length and taxonomy than ATLAS's 14-entry list; do not assume the indices mean the same thing across surveys**), `psdb.dbviews.WebViewUserDefined`.

- [ ] **Step 1: Write the failing tests**

`ps1/tests/psdbapi/test_object_list_filters.py`:
```python
import unittest

from django.test import TestCase

from psdbapi.serializers import ObjectListSerializer
from psdb.apiutils import buildObjectListQueryFilter


FILTER_FIELDS = [
    'rb_pix_gte', 'rb_pix_lte',
    'ra_gte', 'ra_lte',
    'dec_gte', 'dec_lte',
    'sherlock_class', 'spec_type',
]

EMPTY_VALIDATED_DATA = {
    'rb_pix_gte': None, 'rb_pix_lte': None,
    'ra_gte': None, 'ra_lte': None,
    'dec_gte': None, 'dec_lte': None,
    'sherlock_class': None, 'spec_type': None,
}


class TestObjectListSerializerFilters(TestCase):
    def test_filters_default_to_none_when_absent(self):
        serializer = ObjectListSerializer(data={'objectlistid': 0})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        for field in FILTER_FIELDS:
            self.assertIsNone(serializer.validated_data[field])

    def test_no_vra_fields_exist(self):
        serializer = ObjectListSerializer(data={'objectlistid': 0})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('vra_gte', serializer.validated_data)
        self.assertNotIn('vra_lte', serializer.validated_data)

    def test_numeric_filters_accept_valid_floats(self):
        data = {'objectlistid': 0, 'rb_pix_gte': 0.5, 'dec_lte': 5.0}
        serializer = ObjectListSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['rb_pix_gte'], 0.5)
        self.assertEqual(serializer.validated_data['dec_lte'], 5.0)

    def test_numeric_filter_rejects_non_numeric_value(self):
        serializer = ObjectListSerializer(data={'objectlistid': 0, 'rb_pix_gte': 'nope'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('rb_pix_gte', serializer.errors)


class TestBuildObjectListQueryFilter(unittest.TestCase):
    def test_empty_validated_data_returns_empty_filter(self):
        self.assertEqual(buildObjectListQueryFilter(EMPTY_VALIDATED_DATA), {})

    def test_numeric_bounds_map_to_orm_lookups(self):
        data = dict(EMPTY_VALIDATED_DATA, rb_pix_gte=0.8, dec_lte=0.9)
        self.assertEqual(
            buildObjectListQueryFilter(data),
            {'rb_pix__gte': 0.8, 'dec__lte': 0.9},
        )

    def test_string_fields_map_to_exact_match_lookups(self):
        data = dict(EMPTY_VALIDATED_DATA, sherlock_class='SN', spec_type='confirmed')
        self.assertEqual(
            buildObjectListQueryFilter(data),
            {'sherlockClassification': 'SN', 'observation_status': 'confirmed'},
        )
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd ps1 && python manage.py test psdbapi.test_object_list_filters --keepdb --noinput` (via the `ps1/tests` package: `python manage.py test tests.psdbapi.test_object_list_filters --keepdb --noinput`)
Expected: `ModuleNotFoundError: No module named 'psdb.apiutils'`.

- [ ] **Step 3: Create `ps1/psdb/apiutils.py` and implement `ObjectListSerializer`/`ObjectListView`**

`ps1/psdb/apiutils.py` (new file):
```python
from django.forms.models import model_to_dict

from .dbviews import WebViewUserDefined
from .views import followupClassList


OBJECT_LIST_FIELD_TO_LOOKUP = {
    'rb_pix_gte': 'rb_pix__gte',
    'rb_pix_lte': 'rb_pix__lte',
    'ra_gte': 'ra__gte',
    'ra_lte': 'ra__lte',
    'dec_gte': 'dec__gte',
    'dec_lte': 'dec__lte',
    'sherlock_class': 'sherlockClassification',
    'spec_type': 'observation_status',
}


def buildObjectListQueryFilter(validated_data):
    queryFilter = {}
    for field, lookup in OBJECT_LIST_FIELD_TO_LOOKUP.items():
        value = validated_data.get(field)
        if value is not None:
            queryFilter[lookup] = value
    return queryFilter


def getObjectList(request, listId, getCustomList=False, dateThreshold=None, queryFilter=None):
    if queryFilter is None:
        queryFilter = {}

    if getCustomList:
        filters = {'object_group_id': listId}
        if dateThreshold is not None:
            filters['followup_flag_date__gt'] = dateThreshold
        filters.update(queryFilter)
        querySet = WebViewUserDefined.objects.filter(**filters)
    else:
        filters = {}
        if dateThreshold is not None:
            filters['followup_flag_date__gt'] = dateThreshold
        filters.update(queryFilter)
        querySet = followupClassList[int(listId)].objects.filter(**filters)

    return [model_to_dict(row) for row in querySet]
```

In `ps1/psdbapi/serializers.py`, delete the commented `ObjectListSerializer` block and add:
```python
from psdb.apiutils import buildObjectListQueryFilter, getObjectList

class ObjectListSerializer(serializers.Serializer):
    objectlistid = serializers.IntegerField(required=True)
    getcustomlist = serializers.BooleanField(required=False, default=False)
    datethreshold = serializers.DateTimeField(required=False, default=None)
    rb_pix_gte = serializers.FloatField(required=False, default=None)
    rb_pix_lte = serializers.FloatField(required=False, default=None)
    ra_gte = serializers.FloatField(required=False, default=None)
    ra_lte = serializers.FloatField(required=False, default=None)
    dec_gte = serializers.FloatField(required=False, default=None)
    dec_lte = serializers.FloatField(required=False, default=None)
    sherlock_class = serializers.CharField(required=False, default=None)
    spec_type = serializers.CharField(required=False, default=None)

    def save(self):
        objectlistid = self.validated_data['objectlistid']
        getcustomlist = self.validated_data['getcustomlist']
        datethreshold = self.validated_data['datethreshold']

        request = self.context.get("request")

        dateThreshold = None
        if datethreshold is not None:
            dateThreshold = self.validated_data['datethreshold']

        queryFilter = buildObjectListQueryFilter(self.validated_data)

        return getObjectList(request, objectlistid, getCustomList=getcustomlist, dateThreshold=dateThreshold, queryFilter=queryFilter)
```

In `ps1/psdbapi/views.py`, add (import `ObjectListSerializer` in the existing `from .serializers import ConeSerializer` line):
```python
class ObjectListView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated & HasReadAccess]

    def get(self, request):
        serializer = ObjectListSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ObjectListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

In `ps1/psdbapi/urls.py`, add: `path('api/objectlist/', views.ObjectListView.as_view()),`

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_object_list_filters --keepdb --noinput`
Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add ps1/psdb/apiutils.py ps1/psdbapi/serializers.py ps1/psdbapi/views.py ps1/psdbapi/urls.py ps1/tests/psdbapi/test_object_list_filters.py
git commit -m "$(cat <<'EOF'
feat: add api/objectlist/ endpoint to ps1 API

Oversight-Mode: collab
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: <session URL>
EOF
)"
```

---

### Task 3: `api/objectgroups/` — `TcsObjectGroupsView` (insert)

**Files:**
- Modify: `ps1/psdbapi/serializers.py` (replace commented `TcsObjectGroupsSerializer`, lines ~327–373)
- Modify: `ps1/psdbapi/views.py`, `ps1/psdbapi/urls.py`
- Test: `ps1/tests/psdbapi/test_object_groups.py`

**Interfaces:**
- Consumes: `psdb.models.TcsTransientObjects`, `TcsObjectGroups`, `TcsObjectGroupDefinitions`.
- Produces: nothing new consumed elsewhere.

**The FK gotcha (see `docs/atlas-ps1-api-reference.md`):** on ATLAS, `TcsObjectGroups.object_group_id` is a plain `IntegerField`, so the insert dict can say `{'object_group_id': <int>}`. On ps1 it's a `ForeignKey` to `TcsObjectGroupDefinitions` — the model attribute `object_group_id` expects a model *instance*; the raw pk must be assigned via `object_group_id_id`.

- [ ] **Step 1: Write the failing test**

`ps1/tests/psdbapi/test_object_groups.py`:
```python
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import GroupProfile
from psdb.models import TcsTransientObjects, TcsObjectGroups, TcsObjectGroupDefinitions


class TestObjectGroupsInsert(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.write_group = Group.objects.create(name="Write Access")
        GroupProfile.objects.create(api_write_access=True, group=self.write_group, token_expiration_time=timedelta(days=365))
        self.user.groups.add(self.write_group)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.transient = TcsTransientObjects.objects.create(id=1, ra_psf=10.0, dec_psf=-5.0)
        self.group_def = TcsObjectGroupDefinitions.objects.create(id=1, name='Test Group')

    def test_insert_creates_row(self):
        response = self.client.post('/api/objectgroups/', {'objectid': self.transient.id, 'objectgroupid': self.group_def.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            TcsObjectGroups.objects.filter(transient_object_id=self.transient.id, object_group_id_id=self.group_def.id).exists()
        )

    def test_insert_rejects_missing_object(self):
        response = self.client.post('/api/objectgroups/', {'objectid': 99999, 'objectgroupid': self.group_def.id})
        self.assertEqual(response.data['info'], 'Object does not exist.')

    def test_insert_rejects_missing_group(self):
        response = self.client.post('/api/objectgroups/', {'objectid': self.transient.id, 'objectgroupid': 99999})
        self.assertEqual(response.data['info'], 'Object group ID does not exist.')
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_object_groups --keepdb --noinput`
Expected: `404` (no `/api/objectgroups/` route yet) or `ImportError` for `TcsObjectGroupsSerializer`.

- [ ] **Step 3: Implement**

In `ps1/psdbapi/serializers.py`, delete the commented `TcsObjectGroupsSerializer` block and add:
```python
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from psdb.models import TcsTransientObjects, TcsObjectGroups, TcsObjectGroupDefinitions

class TcsObjectGroupsSerializer(serializers.Serializer):
    objectid = serializers.IntegerField(required=True)
    objectgroupid = serializers.IntegerField(required=True)

    def save(self):
        objectid = self.validated_data['objectid']
        objectGroupId = self.validated_data['objectgroupid']

        replyMessage = 'Row created.'

        try:
            TcsTransientObjects.objects.get(pk=objectid)
        except ObjectDoesNotExist:
            return {"objectid": objectid, "info": "Object does not exist."}

        try:
            TcsObjectGroupDefinitions.objects.get(pk=objectGroupId)
        except ObjectDoesNotExist:
            return {"objectgroupid": objectGroupId, "info": "Object group ID does not exist."}

        try:
            TcsObjectGroups(transient_object_id_id=objectid, object_group_id_id=objectGroupId).save(force_insert=True)
        except IntegrityError:
            replyMessage = 'Duplicate row. Cannot add row.'

        return {"objectgroupid": objectid, "info": replyMessage}
```

In `ps1/psdbapi/views.py`:
```python
class TcsObjectGroupsView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated & HasWriteAccess]

    def get(self, request):
        return Response({"Error": "GET is not implemented for this service."})

    def post(self, request, format=None):
        serializer = TcsObjectGroupsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

In `ps1/psdbapi/urls.py`, add: `path('api/objectgroups/', views.TcsObjectGroupsView.as_view()),`

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_object_groups --keepdb --noinput`
Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add ps1/psdbapi/serializers.py ps1/psdbapi/views.py ps1/psdbapi/urls.py ps1/tests/psdbapi/test_object_groups.py
git commit -m "$(cat <<'EOF'
feat: add api/objectgroups/ insert endpoint to ps1 API

Oversight-Mode: collab
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: <session URL>
EOF
)"
```

---

### Task 4: `api/objectgroupsdelete/` — `TcsObjectGroupsDeleteView`

**Files:**
- Modify: `ps1/psdbapi/serializers.py` (replace commented `TcsObjectGroupsDeleteSerializer`, lines ~374–420)
- Modify: `ps1/psdbapi/views.py`, `ps1/psdbapi/urls.py`
- Test: `ps1/tests/psdbapi/test_object_groups.py` (extend from Task 3)

**Interfaces:**
- Consumes: same models as Task 3. Depends on Task 3 being merged (reuses its test fixtures' setup pattern).

- [ ] **Step 1: Write the failing test**

Append to `ps1/tests/psdbapi/test_object_groups.py`:
```python
class TestObjectGroupsDelete(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='deleteuser', password='testpassword')
        self.write_group = Group.objects.create(name="Write Access 2")
        GroupProfile.objects.create(api_write_access=True, group=self.write_group, token_expiration_time=timedelta(days=365))
        self.user.groups.add(self.write_group)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.transient = TcsTransientObjects.objects.create(id=2, ra_psf=11.0, dec_psf=-6.0)
        self.group_def = TcsObjectGroupDefinitions.objects.create(id=2, name='Test Group 2')
        TcsObjectGroups.objects.create(transient_object_id_id=self.transient.id, object_group_id_id=self.group_def.id)

    def test_delete_removes_row(self):
        response = self.client.post('/api/objectgroupsdelete/', {'objectid': self.transient.id, 'objectgroupid': self.group_def.id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            TcsObjectGroups.objects.filter(transient_object_id=self.transient.id, object_group_id_id=self.group_def.id).exists()
        )

    def test_delete_missing_row_returns_400(self):
        response = self.client.post('/api/objectgroupsdelete/', {'objectid': self.transient.id, 'objectgroupid': 99999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_object_groups.TestObjectGroupsDelete --keepdb --noinput`
Expected: fails (no route / no serializer).

- [ ] **Step 3: Implement**

In `ps1/psdbapi/serializers.py`, delete the commented `TcsObjectGroupsDeleteSerializer` block and add:
```python
class TcsObjectGroupsDeleteSerializer(serializers.Serializer):
    objectid = serializers.IntegerField(required=True)
    objectgroupid = serializers.IntegerField(required=True)

    def save(self):
        objectid = self.validated_data['objectid']
        objectGroupId = self.validated_data['objectgroupid']

        try:
            TcsTransientObjects.objects.get(pk=objectid)
        except ObjectDoesNotExist:
            return {"objectid": objectid, "info": "Object does not exist."}

        try:
            TcsObjectGroupDefinitions.objects.get(pk=objectGroupId)
        except ObjectDoesNotExist:
            return {"objectgroupid": objectGroupId, "info": "Object group ID does not exist."}

        try:
            instance = TcsObjectGroups.objects.get(transient_object_id__id=objectid, object_group_id_id=objectGroupId)
        except ObjectDoesNotExist:
            return {"objectgroupid": objectGroupId, "objectid": objectid, "info": "Object group ID does not exist or object ID does not exist."}

        instance.delete()
        return {"objectgroupid": objectid, "info": "Row deleted."}
```

In `ps1/psdbapi/views.py`:
```python
class TcsObjectGroupsDeleteView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated & HasWriteAccess]

    def get(self, request):
        return Response({"Error": "GET is not implemented for this service."})

    def post(self, request, format=None):
        serializer = TcsObjectGroupsDeleteSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if "deleted" in message['info']:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
```

In `ps1/psdbapi/urls.py`, add: `path('api/objectgroupsdelete/', views.TcsObjectGroupsDeleteView.as_view()),`

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_object_groups --keepdb --noinput`
Expected: `OK` (all of Task 3 + Task 4's tests).

- [ ] **Step 5: Commit**

```bash
git add ps1/psdbapi/serializers.py ps1/psdbapi/views.py ps1/psdbapi/urls.py ps1/tests/psdbapi/test_object_groups.py
git commit -m "$(cat <<'EOF'
feat: add api/objectgroupsdelete/ endpoint to ps1 API

Oversight-Mode: collab
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: <session URL>
EOF
)"
```

---

### Task 5: `api/objectgroupslist/` — `TcsObjectGroupsListView`

**Files:**
- Modify: `ps1/psdb/apiutils.py` (add `getCustomListObjects`)
- Modify: `ps1/psdbapi/serializers.py` (replace commented `TcsObjectGroupsListSerializer`, lines ~421–435)
- Modify: `ps1/psdbapi/views.py`, `ps1/psdbapi/urls.py`
- Test: `ps1/tests/psdbapi/test_object_groups_list.py`

**Interfaces:**
- Consumes: `buildObjectListQueryFilter` (Task 2), `psdb.dbviews.WebViewUserDefined`, `psdb.models.TcsObjectGroups`.
- Produces (in `psdb/apiutils.py`): `getCustomListObjects(request, objectid=None, objectgroupid=None, queryFilter=None) -> list[dict]`.

- [ ] **Step 1: Write the failing test**

`ps1/tests/psdbapi/test_object_groups_list.py`:
```python
from django.test import TestCase
from psdbapi.serializers import TcsObjectGroupsListSerializer
from psdb.models import TcsTransientObjects, TcsObjectGroups, TcsObjectGroupDefinitions


class TestTcsObjectGroupsListSerializerValidation(TestCase):
    def test_requires_objectid_or_objectgroupid(self):
        serializer = TcsObjectGroupsListSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_no_vra_fields_exist(self):
        serializer = TcsObjectGroupsListSerializer(data={'objectgroupid': 1})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('vra_gte', serializer.validated_data)


class TestObjectGroupsListQuery(TestCase):
    def setUp(self):
        self.transient = TcsTransientObjects.objects.create(id=3, ra_psf=12.0, dec_psf=-7.0)
        self.group_def = TcsObjectGroupDefinitions.objects.create(id=3, name='Test Group 3')
        TcsObjectGroups.objects.create(transient_object_id_id=self.transient.id, object_group_id_id=self.group_def.id)

    def test_lookup_by_objectgroupid_returns_row(self):
        serializer = TcsObjectGroupsListSerializer(data={'objectgroupid': self.group_def.id})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['transient_object_id'], self.transient.id)
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_object_groups_list --keepdb --noinput`
Expected: `ImportError: cannot import name 'TcsObjectGroupsListSerializer'`.

- [ ] **Step 3: Implement**

In `ps1/psdb/apiutils.py`, add:
```python
from psdb.models import TcsObjectGroups


def getCustomListObjects(request, objectid=None, objectgroupid=None, queryFilter=None):
    querySet = None

    if queryFilter:
        filters = dict(queryFilter)
        if objectgroupid is not None:
            filters['object_group_id'] = objectgroupid
        if objectid is not None:
            filters['id'] = objectid
        matchingIds = list(WebViewUserDefined.objects.filter(**filters).values_list('id', flat=True))
        querySet = TcsObjectGroups.objects.filter(transient_object_id__id__in=matchingIds)
        if objectgroupid is not None:
            querySet = querySet.filter(object_group_id_id=objectgroupid)
    elif objectid is None and objectgroupid is not None:
        querySet = TcsObjectGroups.objects.filter(object_group_id_id=objectgroupid)
    elif objectid is not None and objectgroupid is None:
        querySet = TcsObjectGroups.objects.filter(transient_object_id__id=objectid)

    if querySet is None:
        return []
    return [model_to_dict(row) for row in querySet]
```
(Note the `object_group_id_id=` filter kwargs — same FK gotcha as Task 3/4; `object_group_id=<int>` would try to compare the FK column against a raw int instead of a related-object lookup and raise on ps1, unlike ATLAS.)

In `ps1/psdbapi/serializers.py`, delete the commented `TcsObjectGroupsListSerializer` block and add:
```python
from psdb.apiutils import getCustomListObjects

class TcsObjectGroupsListSerializer(serializers.Serializer):
    objectid = serializers.IntegerField(required=False, default=None)
    objectgroupid = serializers.IntegerField(required=False, default=None)
    rb_pix_gte = serializers.FloatField(required=False, default=None)
    rb_pix_lte = serializers.FloatField(required=False, default=None)
    ra_gte = serializers.FloatField(required=False, default=None)
    ra_lte = serializers.FloatField(required=False, default=None)
    dec_gte = serializers.FloatField(required=False, default=None)
    dec_lte = serializers.FloatField(required=False, default=None)
    sherlock_class = serializers.CharField(required=False, default=None)
    spec_type = serializers.CharField(required=False, default=None)

    def validate(self, data):
        if data.get('objectid') is None and data.get('objectgroupid') is None:
            raise serializers.ValidationError("Either objectid or objectgroupid must be provided.")
        return data

    def save(self):
        objectid = self.validated_data['objectid']
        objectGroupId = self.validated_data['objectgroupid']
        request = self.context.get("request")
        queryFilter = buildObjectListQueryFilter(self.validated_data)
        return getCustomListObjects(request, objectid, objectGroupId, queryFilter=queryFilter)
```

In `ps1/psdbapi/views.py`:
```python
class TcsObjectGroupsListView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated & HasReadAccess]

    def get(self, request):
        serializer = TcsObjectGroupsListSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = TcsObjectGroupsListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

In `ps1/psdbapi/urls.py`, add: `path('api/objectgroupslist/', views.TcsObjectGroupsListView.as_view()),`

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_object_groups_list --keepdb --noinput`
Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add ps1/psdb/apiutils.py ps1/psdbapi/serializers.py ps1/psdbapi/views.py ps1/psdbapi/urls.py ps1/tests/psdbapi/test_object_groups_list.py
git commit -m "$(cat <<'EOF'
feat: add api/objectgroupslist/ endpoint to ps1 API

Oversight-Mode: collab
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: <session URL>
EOF
)"
```

---

### Task 6: `api/externalxmlist/` — `ExternalCrossmatchesListView`

No commented reference exists for this one (added to ATLAS 2024-09-24, after the ps1 scaffold copy was made) — written fresh from the ATLAS implementation.

**Files:**
- Modify: `ps1/psdb/apiutils.py` (add `getExternalCrossmatchesList`)
- Modify: `ps1/psdbapi/serializers.py`, `ps1/psdbapi/views.py`, `ps1/psdbapi/urls.py`
- Test: `ps1/tests/psdbapi/test_external_crossmatches.py`

**Interfaces:**
- Produces (in `psdb/apiutils.py`): `getExternalCrossmatchesList(request, externalObjects=[]) -> list[list[dict]]`.
- Consumes: `psdb.models.TcsCrossMatchesExternal` (already exists on ps1, unmodified from atlas's field names — confirmed by reading `ps1/psdb/models.py`).

- [ ] **Step 1: Write the failing test**

`ps1/tests/psdbapi/test_external_crossmatches.py`:
```python
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import GroupProfile
from psdb.models import TcsTransientObjects, TcsCrossMatchesExternal


class TestExternalCrossmatchesList(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='xmuser', password='testpassword')
        self.read_group = Group.objects.create(name="Read Access")
        GroupProfile.objects.create(api_write_access=False, group=self.read_group, token_expiration_time=timedelta(days=365))
        self.user.groups.add(self.read_group)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.transient = TcsTransientObjects.objects.create(id=4, ra_psf=13.0, dec_psf=-8.0)
        TcsCrossMatchesExternal.objects.create(
            id=1, transient_object_id_id=self.transient.id, external_designation='SN2026aa',
        )

    def test_returns_matches_for_known_designation(self):
        response = self.client.get('/api/externalxmlist/', {'externalObjects': 'SN2026aa'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0][0]['external_designation'], 'SN2026aa')

    def test_returns_empty_list_for_unknown_designation(self):
        response = self.client.get('/api/externalxmlist/', {'externalObjects': 'nonexistent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_external_crossmatches --keepdb --noinput`
Expected: `404` (no route).

- [ ] **Step 3: Implement**

In `ps1/psdb/apiutils.py`, add:
```python
from psdb.models import TcsCrossMatchesExternal


def getExternalCrossmatchesList(request, externalObjects=[]):
    externalCrossmatchesList = []
    for xm in externalObjects:
        querySet = TcsCrossMatchesExternal.objects.filter(external_designation=xm)
        miniList = [model_to_dict(x) for x in querySet]
        if miniList:
            externalCrossmatchesList.append(miniList)
    return externalCrossmatchesList
```

In `ps1/psdbapi/serializers.py`, add:
```python
from psdb.apiutils import getExternalCrossmatchesList

class ExternalCrossmatchesListSerializer(serializers.Serializer):
    externalObjects = serializers.CharField(required=False, default=None)

    def save(self):
        externalObjects = self.validated_data['externalObjects']
        request = self.context.get("request")

        olist = []
        if externalObjects is not None:
            olist = [tok.strip() for tok in externalObjects.split(',')]

        return getExternalCrossmatchesList(request, externalObjects=olist)
```

In `ps1/psdbapi/views.py`:
```python
class ExternalCrossmatchesListView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated & HasReadAccess]

    def get(self, request):
        serializer = ExternalCrossmatchesListSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ExternalCrossmatchesListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

In `ps1/psdbapi/urls.py`, add: `path('api/externalxmlist/', views.ExternalCrossmatchesListView.as_view()),`

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_external_crossmatches --keepdb --noinput`
Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add ps1/psdb/apiutils.py ps1/psdbapi/serializers.py ps1/psdbapi/views.py ps1/psdbapi/urls.py ps1/tests/psdbapi/test_external_crossmatches.py
git commit -m "$(cat <<'EOF'
feat: add api/externalxmlist/ endpoint to ps1 API

Oversight-Mode: collab
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: <session URL>
EOF
)"
```

---

### Task 7: `api/objectdetectionlist/` — `ObjectDetectionListView`

No commented reference exists for this one either (same 2024-09-24 ATLAS addition as Task 6). Despite the name, this doesn't touch a detections table — it updates `detection_list_id`/`date_modified` directly on the transient object row (the snooze/unsnooze mechanism).

**Files:**
- Modify: `ps1/psdbapi/serializers.py`, `ps1/psdbapi/views.py`, `ps1/psdbapi/urls.py`
- Test: `ps1/tests/psdbapi/test_object_detection_list.py`

**Interfaces:**
- Consumes: `psdb.models.TcsTransientObjects` (has `detection_list_id`, `date_modified` fields, confirmed present on ps1's model).

**Note:** ATLAS's version hardcodes the allowed target list ids to `(3, 4, 12)` (its own detection-list numbering for "possible"/"eyeballed"/similar). ps1's `TcsDetectionLists` table has a different, survey-specific set of rows (`followupClassList` in Task 2 only has 9 entries vs ATLAS's 14) — **do not copy the literal `(3, 4, 12)` tuple**; confirm the correct ps1 list ids with Heloise/Ken before merging this task, and treat the value below as a placeholder to replace, not a guess to ship.

- [ ] **Step 1: Write the failing test**

`ps1/tests/psdbapi/test_object_detection_list.py`:
```python
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import GroupProfile
from psdb.models import TcsTransientObjects


class TestObjectDetectionList(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='snoozeuser', password='testpassword')
        self.write_group = Group.objects.create(name="Write Access 3")
        GroupProfile.objects.create(api_write_access=True, group=self.write_group, token_expiration_time=timedelta(days=365))
        self.user.groups.add(self.write_group)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.transient = TcsTransientObjects.objects.create(id=5, ra_psf=14.0, dec_psf=-9.0, detection_list_id_id=1)

    def test_updates_detection_list_id(self):
        response = self.client.post('/api/objectdetectionlist/', {'objectid': self.transient.id, 'objectlist': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transient.refresh_from_db()
        self.assertEqual(self.transient.detection_list_id_id, 2)

    def test_rejects_missing_object(self):
        response = self.client.post('/api/objectdetectionlist/', {'objectid': 99999, 'objectlist': 2})
        self.assertEqual(response.data['info'], 'Object does not exist.')
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_object_detection_list --keepdb --noinput`
Expected: `404` (no route).

- [ ] **Step 3: Implement**

In `ps1/psdbapi/serializers.py`, add:
```python
from datetime import datetime

class ObjectDetectionListSerializer(serializers.Serializer):
    objectid = serializers.IntegerField(required=True)
    objectlist = serializers.IntegerField(required=True)
    insertdate = serializers.DateTimeField(required=False, default=None)

    def save(self):
        objectid = self.validated_data['objectid']
        objectlist = self.validated_data['objectlist']
        insertdate = self.validated_data['insertdate']

        insertDate = insertdate if insertdate is not None else datetime.now()

        try:
            transient = TcsTransientObjects.objects.get(pk=objectid)
        except ObjectDoesNotExist:
            return {"objectid": objectid, "info": "Object does not exist."}

        # TODO(Heloise/Ken): confirm the valid ps1 detection_list_id values for this
        # endpoint (ATLAS's equivalent restricts to its own list ids 3, 4, 12).
        VALID_TARGET_LISTS = (3, 4, 12)
        if objectlist not in VALID_TARGET_LISTS:
            return {"objectid": objectid, "info": "Error updating row."}

        transient.detection_list_id_id = objectlist
        transient.date_modified = insertDate
        transient.save()

        return {"objectid": objectid, "info": "Row created."}
```

In `ps1/psdbapi/views.py`:
```python
class ObjectDetectionListView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated & HasWriteAccess]

    def get(self, request):
        return Response({"Error": "GET is not implemented for this service."})

    def post(self, request, format=None):
        serializer = ObjectDetectionListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

In `ps1/psdbapi/urls.py`, add: `path('api/objectdetectionlist/', views.ObjectDetectionListView.as_view()),`

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_object_detection_list --keepdb --noinput`
Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add ps1/psdbapi/serializers.py ps1/psdbapi/views.py ps1/psdbapi/urls.py ps1/tests/psdbapi/test_object_detection_list.py
git commit -m "$(cat <<'EOF'
feat: add api/objectdetectionlist/ endpoint to ps1 API

VALID_TARGET_LISTS placeholder copied from ATLAS's list ids (3, 4, 12) —
needs confirming against ps1's tcs_detection_lists before this is
treated as done.

Oversight-Mode: collab
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: <session URL>
EOF
)"
```

---

### Task 8: `api/objects/` — `ObjectsView` (single-object detail: lightcurve, forced photometry, crossmatches)

**This is the highest-risk task in the plan** (per explicit scoping decision — see `docs/atlas-ps1-api-reference.md`). ATLAS's `candidateddcApi` dumps raw rows from its DDC (difference-detection-chain) pipeline tables via `model_to_dict`, which have no ps1 equivalent. ps1's lightcurve data instead comes through `commonqueries.getLightcurvePoints`/`getLightcurveNonDetections`, which return fixed-shape `[g, r, i, z, y, w, x, B, V, fullList]` arrays of raw `[mjd, mag, magerr]`/`[mjd, limit]` tuples from hand-written SQL (`django.db.connection`), not queryset rows. **The response shape below is a new design, not a port** — expect Ken/Heloise to want changes to it in review; that's expected, not a sign the task was done wrong.

Also note: ATLAS's `candidateddcApi` computes a `gw = TcsGravityEventAnnotations.objects.filter(...)` queryset that is **never used** in its returned `data` dict — dead code. Do not port it.

**Files:**
- Modify: `ps1/psdb/apiutils.py` (add `transientObjectApi`)
- Modify: `ps1/psdbapi/serializers.py` (replace commented `ObjectsSerializer`, lines ~90–116)
- Modify: `ps1/psdbapi/views.py`, `ps1/psdbapi/urls.py`
- Test: `ps1/tests/psdbapi/test_objects.py`

**Interfaces:**
- Produces: `transientObjectApi(request, transient_object_id, mjdThreshold=None) -> dict` with keys `object`, `lc`, `lcnondets`, `fp`, `sherlock_crossmatches`, `sherlock_classifications`, `tns_crossmatches`, `external_crossmatches` (matching ATLAS's key names for client-side consistency, even though `lc`/`lcnondets`/`fp` contents differ in shape).
- Consumes: `psdb.models.TcsTransientObjects`, `TcsForcedPhotometry`, `SherlockClassifications`, `SherlockCrossmatches`, `TcsCrossMatchesExternal`; `psdb.commonqueries.getLightcurvePoints`, `getLightcurveNonDetections`.

- [ ] **Step 1: Write the failing test**

`ps1/tests/psdbapi/test_objects.py`:
```python
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import GroupProfile
from psdb.models import TcsTransientObjects, TcsForcedPhotometry
from psdb.apiutils import transientObjectApi


class TestTransientObjectApi(TestCase):
    def setUp(self):
        self.transient = TcsTransientObjects.objects.create(id=6, ra_psf=15.0, dec_psf=-10.0, ps1_designation='PS26aa')
        TcsForcedPhotometry.objects.create(
            id=1, transient_object_id_id=self.transient.id, ra_psf=15.0, dec_psf=-10.0,
            mjd_obs=60000.0, fptype=0,
        )

    def test_returns_object_and_forced_photometry(self):
        data = transientObjectApi(None, self.transient.id)
        self.assertEqual(data['object']['id'], self.transient.id)
        self.assertEqual(len(data['fp']), 1)
        self.assertEqual(data['fp'][0]['mjd_obs'], 60000.0)
        self.assertEqual(data['sherlock_crossmatches'], [])
        self.assertEqual(data['sherlock_classifications'], [])
        self.assertEqual(data['external_crossmatches'], [])
        self.assertEqual(data['tns_crossmatches'], [])

    def test_returns_empty_shell_for_unknown_object(self):
        data = transientObjectApi(None, 99999)
        self.assertIsNone(data['fp'])
        self.assertIn('object', data)

    def test_mjd_threshold_filters_forced_photometry(self):
        data = transientObjectApi(None, self.transient.id, mjdThreshold=60001.0)
        self.assertEqual(data['fp'], [])


class TestObjectsEndpoint(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='objuser', password='testpassword')
        self.read_group = Group.objects.create(name="Read Access 2")
        GroupProfile.objects.create(api_write_access=False, group=self.read_group, token_expiration_time=timedelta(days=365))
        self.user.groups.add(self.read_group)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.transient = TcsTransientObjects.objects.create(id=7, ra_psf=16.0, dec_psf=-11.0)

    def test_get_single_object(self):
        response = self.client.get('/api/objects/', {'objects': str(self.transient.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['object']['id'], self.transient.id)

    def test_rejects_too_many_objects(self):
        objects = ','.join(str(n) for n in range(50_001))
        response = self.client.get('/api/objects/', {'objects': objects})
        self.assertIn('info', response.data)
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_objects --keepdb --noinput`
Expected: `ImportError: cannot import name 'transientObjectApi'`.

- [ ] **Step 3: Implement**

In `ps1/psdb/apiutils.py`, add:
```python
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
from psdb.models import TcsForcedPhotometry, SherlockClassifications, SherlockCrossmatches, TcsCrossMatchesExternal
from psdb.commonqueries import getLightcurvePoints, getLightcurveNonDetections


def _lcPointsToDicts(fullList):
    return [{'mjd': row[0], 'mag': row[1], 'magerr': row[2]} for row in fullList]


def _lcNonDetsToDicts(fullList):
    return [{'mjd': row[0]} for row in fullList]


def transientObjectApi(request, transient_object_id, mjdThreshold=None):
    try:
        transient = TcsTransientObjects.objects.get(pk=transient_object_id)
    except ObjectDoesNotExist as e:
        return {
            'object': str(e),
            'lc': None,
            'lcnondets': None,
            'fp': None,
            'sherlock_crossmatches': None,
            'sherlock_classifications': None,
            'tns_crossmatches': None,
            'external_crossmatches': None,
        }

    sc = SherlockClassifications.objects.filter(transient_object_id_id=transient.id)
    sx = SherlockCrossmatches.objects.filter(transient_object_id_id=transient.id)
    externalXMs = TcsCrossMatchesExternal.objects.filter(transient_object_id=transient.id).exclude(matched_list='Transient Name Server').order_by('external_designation')
    tnsXMs = TcsCrossMatchesExternal.objects.filter(transient_object_id=transient.id, matched_list='Transient Name Server')

    if mjdThreshold is not None:
        forcedPhotometry = TcsForcedPhotometry.objects.filter(transient_object_id=transient.id).filter(mjd_obs__gte=mjdThreshold).order_by('mjd_obs')
    else:
        forcedPhotometry = TcsForcedPhotometry.objects.filter(transient_object_id=transient.id).order_by('mjd_obs')

    *_, lcFullList = getLightcurvePoints(transient.id, conn=connection)
    *_, lcNonDetsFullList = getLightcurveNonDetections(transient.id, conn=connection)

    return {
        'object': model_to_dict(transient),
        'lc': _lcPointsToDicts(lcFullList),
        'lcnondets': _lcNonDetsToDicts(lcNonDetsFullList),
        'fp': [model_to_dict(f) for f in forcedPhotometry],
        'sherlock_crossmatches': [model_to_dict(s) for s in sx],
        'sherlock_classifications': [model_to_dict(s) for s in sc],
        'tns_crossmatches': [model_to_dict(t) for t in tnsXMs],
        'external_crossmatches': [model_to_dict(e) for e in externalXMs],
    }
```

In `ps1/psdbapi/serializers.py`, delete the commented `ObjectsSerializer` block and add:
```python
from psdb.apiutils import transientObjectApi

class ObjectsSerializer(serializers.Serializer):
    objects = serializers.CharField(required=True)
    mjd = serializers.FloatField(required=False, default=None)

    def save(self):
        objects = self.validated_data['objects']
        mjd = self.validated_data['mjd']

        olist = [tok.strip() for tok in objects.split(',')]
        if len(olist) > 50_000:
            return {"info": "Max number of objects for each requests is 50,000"}

        request = self.context.get("request")
        return [transientObjectApi(request, candidate, mjdThreshold=mjd) for candidate in olist]
```

In `ps1/psdbapi/views.py`:
```python
class ObjectsView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, QueryAuthentication]
    permission_classes = [IsAuthenticated & HasReadAccess]

    def get(self, request):
        serializer = ObjectsSerializer(data=request.GET, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ObjectsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(message, status=retcode(message))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

In `ps1/psdbapi/urls.py`, add: `path('api/objects/', views.ObjectsView.as_view()),`

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_objects --keepdb --noinput`
Expected: `OK`. If `getLightcurvePoints`/`getLightcurveNonDetections` error against an object with no photometry rows at all (empty raw-SQL result set) rather than returning empty lists, adjust `transientObjectApi` to guard for that — confirm actual behaviour against the test DB rather than assuming.

- [ ] **Step 5: Commit**

```bash
git add ps1/psdb/apiutils.py ps1/psdbapi/serializers.py ps1/psdbapi/views.py ps1/psdbapi/urls.py ps1/tests/psdbapi/test_objects.py
git commit -m "$(cat <<'EOF'
feat: add api/objects/ endpoint to ps1 API

Response shape for lc/lcnondets/fp is a new design, not a port of
ATLAS's DDC-based candidateddcApi -- ps1 has no DDC-equivalent
pipeline. Flagging for review, expect this to change.

Oversight-Mode: collab
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: <session URL>
EOF
)"
```

---

### Task 9: Request usage logging (`TcsAPIUsageLog` + `LoggingAPIView`)

Cross-cutting — done last since it touches every view added in Tasks 2–8 (and `ConeView`). ATLAS's version (`atlas/atlasapi/views.py`, search "HELOISE SHENANIGANS") logs every validated request via a shared `LoggingAPIView` base class. ps1 has neither the model nor the base class yet. `TcsAPIUsageLog` is a **managed** Django model (no `managed = False` in its `Meta`, unlike almost every other model in this codebase) — its table doesn't exist yet on either survey's DB and gets created by `makemigrations`/`migrate`, which is why the docker `tests` service already runs `makemigrations` before `test`.

**Files:**
- Modify: `ps1/psdb/models.py` (add `TcsAPIUsageLog`)
- Modify: `ps1/psdbapi/views.py` (add `LoggingAPIView`, change every view added in Tasks 2–8 plus `ConeView` to subclass it)
- Test: `ps1/tests/psdbapi/test_usage_logging.py`

**Interfaces:**
- Produces: `psdb.models.TcsAPIUsageLog`, `psdbapi.views.LoggingAPIView.log_request(validated_data)`.
- Consumes: every serializer's `validated_data` from Tasks 2–8.

- [ ] **Step 1: Write the failing test**

`ps1/tests/psdbapi/test_usage_logging.py`:
```python
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import timedelta
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import GroupProfile
from psdb.models import TcsAPIUsageLog, TcsTransientObjects


class TestUsageLogging(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='loguser', password='testpassword')
        self.read_group = Group.objects.create(name="Read Access 3")
        GroupProfile.objects.create(api_write_access=False, group=self.read_group, token_expiration_time=timedelta(days=365))
        self.user.groups.add(self.read_group)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        TcsTransientObjects.objects.create(id=8, ra_psf=17.0, dec_psf=-12.0)

    def test_get_request_creates_usage_log_row(self):
        self.assertEqual(TcsAPIUsageLog.objects.count(), 0)
        self.client.get('/api/objects/', {'objects': '8'})
        self.assertEqual(TcsAPIUsageLog.objects.count(), 1)
        row = TcsAPIUsageLog.objects.first()
        self.assertEqual(row.endpoint, '/api/objects/')
        self.assertEqual(row.user, 'loguser')
        self.assertEqual(row.validated_data['objects'], '8')
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd ps1 && python manage.py test tests.psdbapi.test_usage_logging --keepdb --noinput`
Expected: `ImportError: cannot import name 'TcsAPIUsageLog'`.

- [ ] **Step 3: Implement**

In `ps1/psdb/models.py`, add (this one is intentionally **not** `managed = False`):
```python
from django.core.serializers.json import DjangoJSONEncoder

class TcsAPIUsageLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.CharField(db_index=True, max_length=64)
    endpoint = models.CharField(max_length=256)
    validated_data = models.JSONField(encoder=DjangoJSONEncoder)

    class Meta:
        db_table = 'tcs_api_usage_log'
```

In `ps1/psdbapi/views.py`, add near the top (after the existing imports) and change every view class's base from `APIView` to `LoggingAPIView`, adding a `self.log_request(serializer.validated_data)` call after each successful `.save()` — mirroring exactly where ATLAS calls it in each of its view methods:
```python
from psdb.models import TcsAPIUsageLog

class LoggingAPIView(APIView):
    def log_request(self, validated_data):
        summary_dict = {}
        for key in validated_data.keys():
            if not isinstance(validated_data[key], str):
                summary_dict[key] = validated_data[key]
                continue
            if len(validated_data[key]) <= 1280:
                summary_dict[key] = validated_data[key]
                continue
            summary_dict[key + "_count"] = len(validated_data[key].split(','))

        TcsAPIUsageLog.objects.create(
            user=str(self.request.user),
            endpoint=self.request.path,
            validated_data=summary_dict,
        )
```
For each of `ConeView`, `ObjectListView`, `TcsObjectGroupsView`, `TcsObjectGroupsDeleteView`, `TcsObjectGroupsListView`, `ExternalCrossmatchesListView`, `ObjectDetectionListView`, `ObjectsView`: change `class Foo(APIView):` to `class Foo(LoggingAPIView):`, and add `self.log_request(serializer.validated_data)` immediately after each `message = serializer.save()` line, before the `return Response(...)`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ps1 && python manage.py makemigrations psdb --noinput && python manage.py test tests.psdbapi --keepdb --noinput`
Expected: `OK` for the full `psdbapi` test package (all 9 tasks' tests together).

- [ ] **Step 5: Commit**

```bash
git add ps1/psdb/models.py ps1/psdbapi/views.py ps1/tests/psdbapi/test_usage_logging.py ps1/psdb/migrations
git commit -m "$(cat <<'EOF'
feat: log ps1 API requests via TcsAPIUsageLog, matching ATLAS's LoggingAPIView

Oversight-Mode: collab
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: <session URL>
EOF
)"
```

---

## Self-Review

**Spec coverage** (against `docs/atlas-ps1-api-reference.md`'s gap table): `api/objectlist/` → Task 2. `api/objectgroups/` → Task 3. `api/objectgroupsdelete/` → Task 4. `api/objectgroupslist/` → Task 5. `api/externalxmlist/` → Task 6. `api/objectdetectionlist/` → Task 7. `api/objects/` → Task 8. `TcsAPIUsageLog`/`LoggingAPIView` → Task 9. VRA endpoints: explicitly excluded throughout, per Global Constraints. `api/cone/` and `api/auth-token/`: already at parity, no task needed.

**Placeholder scan:** one deliberate, flagged placeholder remains — Task 7's `VALID_TARGET_LISTS = (3, 4, 12)`, called out in its own step, task description, and commit message as needing confirmation against ps1's actual `tcs_detection_lists` rows before merge. This is a genuine open question for Heloise/Ken, not a plan-writing shortcut — no other task has a `TODO`/placeholder.

**Type consistency:** `getObjectList`/`buildObjectListQueryFilter` (Task 2) are consumed with matching signatures in Task 5's `getCustomListObjects`. `transientObjectApi`'s return dict keys (Task 8) match what Task 9's logging wraps around (it logs `validated_data`, not the return value, so no coupling there). All FK-insert calls needing `_id` suffixes (Tasks 3, 4, 5) are consistent with the trap documented in `docs/atlas-ps1-api-reference.md`.
