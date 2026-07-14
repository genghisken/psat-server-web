# Eyeball List Filtering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let `ObjectListView` clients constrain a followup-list query by VRA score, RBPix, RA, Dec, Sherlock class, and spec type, instead of always returning the whole list.

**Architecture:** Ten new optional fields on `ObjectListSerializer` (`atlasapi/serializers.py`) map to Django ORM filter lookups via a new pure helper `buildObjectListQueryFilter()` in `atlas/apiutils.py`. `getObjectList()` applies the resulting dict via `.filter(**queryFilter)` on top of its existing `listId`/`dateThreshold` filtering, for both the numbered-list and custom-list branches.

**Tech Stack:** Django, Django REST Framework, MySQL (via managed=False model views), Django `TestCase`/`unittest.TestCase`.

## Global Constraints

- Numeric fields (`vra`, `rb_pix`, `ra`, `dec`) support `gte`/`lte` bounds only — no `lt`/`gt` variants (spec: `docs/superpowers/specs/2026-07-14-eyeball-list-filtering-design.md`).
- String fields (`sherlock_class`, `spec_type`) are exact-match only.
- All ten fields are optional (`required=False, default=None`); omitting all of them must reproduce today's "return the whole list" behaviour exactly.
- No changes to `log_request()` — the new fields flow through `serializer.validated_data` automatically.
- Only `atlasapi/serializers.py`, `atlas/apiutils.py`, and their tests are in scope. No other endpoint changes.

---

### Task 1: Add filter fields to `ObjectListSerializer`

**Files:**
- Modify: `psat_server_web/atlas/atlasapi/serializers.py:120-137` (`ObjectListSerializer`)
- Test: `psat_server_web/atlas/tests/atlasapi/test_object_list_filters.py` (create)

**Interfaces:**
- Produces: `ObjectListSerializer` gains fields `vra_gte`, `vra_lte`, `rb_pix_gte`, `rb_pix_lte`, `ra_gte`, `ra_lte`, `dec_gte`, `dec_lte` (all `serializers.FloatField(required=False, default=None)`) and `sherlock_class`, `spec_type` (both `serializers.CharField(required=False, default=None)`). Task 2 reads these ten keys out of `validated_data`.

- [ ] **Step 1: Write the failing test**

Create `psat_server_web/atlas/tests/atlasapi/test_object_list_filters.py`:

```python
from django.test import TestCase

from atlasapi.serializers import ObjectListSerializer


NEW_FILTER_FIELDS = [
    'vra_gte', 'vra_lte',
    'rb_pix_gte', 'rb_pix_lte',
    'ra_gte', 'ra_lte',
    'dec_gte', 'dec_lte',
    'sherlock_class', 'spec_type',
]


class TestObjectListSerializerFilters(TestCase):
    def test_filters_default_to_none_when_absent(self):
        serializer = ObjectListSerializer(data={'objectlistid': 4})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        for field in NEW_FILTER_FIELDS:
            self.assertIsNone(serializer.validated_data[field])

    def test_numeric_filters_accept_valid_floats(self):
        data = {
            'objectlistid': 4,
            'vra_gte': 0.8, 'vra_lte': 1.0,
            'rb_pix_gte': 0.5, 'rb_pix_lte': 0.9,
            'ra_gte': 10.0, 'ra_lte': 20.0,
            'dec_gte': -5.0, 'dec_lte': 5.0,
        }
        serializer = ObjectListSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['vra_gte'], 0.8)
        self.assertEqual(serializer.validated_data['dec_lte'], 5.0)

    def test_numeric_filter_rejects_non_numeric_value(self):
        serializer = ObjectListSerializer(data={'objectlistid': 4, 'vra_gte': 'not-a-number'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('vra_gte', serializer.errors)

    def test_string_filters_accept_values(self):
        data = {'objectlistid': 4, 'sherlock_class': 'SN', 'spec_type': 'confirmed'}
        serializer = ObjectListSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['sherlock_class'], 'SN')
        self.assertEqual(serializer.validated_data['spec_type'], 'confirmed')
```

- [ ] **Step 2: Run test to verify it fails**

Run (from `psat_server_web/atlas/`): `python manage.py test tests.atlasapi.test_object_list_filters -v 2`
Expected: FAIL — `KeyError: 'vra_gte'` (or similar) since the field doesn't exist on the serializer yet.

- [ ] **Step 3: Add the fields**

In `atlasapi/serializers.py`, replace the current `ObjectListSerializer` field block (keep `save()` unchanged for now — Task 2 modifies it):

```python
class ObjectListSerializer(serializers.Serializer):
    objectlistid = serializers.IntegerField(required=True)
    getcustomlist = serializers.BooleanField(required=False, default = False)
    datethreshold = serializers.DateTimeField(required=False, default=None)
    vra_gte = serializers.FloatField(required=False, default=None)
    vra_lte = serializers.FloatField(required=False, default=None)
    rb_pix_gte = serializers.FloatField(required=False, default=None)
    rb_pix_lte = serializers.FloatField(required=False, default=None)
    ra_gte = serializers.FloatField(required=False, default=None)
    ra_lte = serializers.FloatField(required=False, default=None)
    dec_gte = serializers.FloatField(required=False, default=None)
    dec_lte = serializers.FloatField(required=False, default=None)
    sherlock_class = serializers.CharField(required=False, default=None)
    spec_type = serializers.CharField(required=False, default=None)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python manage.py test tests.atlasapi.test_object_list_filters -v 2`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add psat_server_web/atlas/atlasapi/serializers.py psat_server_web/atlas/tests/atlasapi/test_object_list_filters.py
git commit -m "Add VRA/RBPix/RA/Dec/Sherlock/spec-type filter fields to ObjectListSerializer"
```

---

### Task 2: Build the ORM filter dict and wire it into `getObjectList()`

**Files:**
- Modify: `psat_server_web/atlas/atlas/apiutils.py:121-143` (`getObjectList`, add `buildObjectListQueryFilter`)
- Modify: `psat_server_web/atlas/atlasapi/serializers.py:125-137` (`ObjectListSerializer.save()`)
- Test: `psat_server_web/atlas/tests/atlasapi/test_object_list_filters.py` (append)

**Interfaces:**
- Consumes: the ten fields produced in Task 1, read from `validated_data` (a plain `dict`-like mapping, e.g. `serializer.validated_data`).
- Produces: `buildObjectListQueryFilter(validated_data: dict) -> dict` in `atlas/apiutils.py` — maps only the ten known filter keys to their ORM lookup keys, skipping any whose value is `None`, ignoring unrelated keys. `getObjectList(request, listId, getCustomList=False, dateThreshold=None, queryFilter=None)` — `queryFilter` is an optional dict of extra ORM lookups applied via `.filter(**queryFilter)` on top of the existing filtering, on both branches.

- [ ] **Step 1: Write the failing test**

Append to `psat_server_web/atlas/tests/atlasapi/test_object_list_filters.py`:

```python
import unittest

from atlas.apiutils import buildObjectListQueryFilter


EMPTY_VALIDATED_DATA = {
    'vra_gte': None, 'vra_lte': None,
    'rb_pix_gte': None, 'rb_pix_lte': None,
    'ra_gte': None, 'ra_lte': None,
    'dec_gte': None, 'dec_lte': None,
    'sherlock_class': None, 'spec_type': None,
}


class TestBuildObjectListQueryFilter(unittest.TestCase):
    def test_empty_validated_data_returns_empty_filter(self):
        self.assertEqual(buildObjectListQueryFilter(EMPTY_VALIDATED_DATA), {})

    def test_numeric_bounds_map_to_orm_lookups(self):
        data = dict(EMPTY_VALIDATED_DATA, vra_gte=0.8, rb_pix_lte=0.9)
        self.assertEqual(
            buildObjectListQueryFilter(data),
            {'vra__gte': 0.8, 'rb_pix__lte': 0.9},
        )

    def test_string_fields_map_to_exact_match_lookups(self):
        data = dict(EMPTY_VALIDATED_DATA, sherlock_class='SN', spec_type='confirmed')
        self.assertEqual(
            buildObjectListQueryFilter(data),
            {'sherlockClassification': 'SN', 'observation_status': 'confirmed'},
        )

    def test_unrelated_keys_are_ignored(self):
        data = {'objectlistid': 4, 'getcustomlist': False, 'datethreshold': None}
        self.assertEqual(buildObjectListQueryFilter(data), {})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test tests.atlasapi.test_object_list_filters.TestBuildObjectListQueryFilter -v 2`
Expected: FAIL — `ImportError: cannot import name 'buildObjectListQueryFilter'`

- [ ] **Step 3: Add `buildObjectListQueryFilter()` and wire it in**

In `atlas/apiutils.py`, add this above `getObjectList` (around line 121):

```python
OBJECT_LIST_FIELD_TO_LOOKUP = {
    'vra_gte': 'vra__gte',
    'vra_lte': 'vra__lte',
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
```

Replace `getObjectList` (currently lines 121-143) with:

```python
def getObjectList(request, listId, getCustomList = False, dateThreshold = None, queryFilter = None):

    querySet = None

    if queryFilter is None:
        queryFilter = {}

    if getCustomList:
        filters = {'object_group_id': listId}
        if dateThreshold is not None:
            filters['followup_flag_date__gt'] = dateThreshold
        filters.update(queryFilter)
        querySet = WebViewUserDefined.objects.filter(**filters)
    else:
        # There are currently 11 valid lists.
        filters = {}
        if dateThreshold is not None:
            filters['followup_flag_date__gt'] = dateThreshold
        filters.update(queryFilter)
        querySet = followupClassList[int(listId)].objects.filter(**filters)

    objectList = []

    if querySet is not None:
        for row in querySet:
            objectList.append(model_to_dict(row))

    return objectList
```

In `atlasapi/serializers.py`, update the import and `ObjectListSerializer.save()`:

```python
from atlas.apiutils import candidateddcApi, getObjectList, buildObjectListQueryFilter
```

```python
    def save(self):
        objectlistid = self.validated_data['objectlistid']
        getcustomlist = self.validated_data['getcustomlist']
        datethreshold = self.validated_data['datethreshold']

        request = self.context.get("request")

        dateThreshold = None
        if datethreshold is not None:
            dateThreshold = self.validated_data['datethreshold']

        queryFilter = buildObjectListQueryFilter(self.validated_data)

        objectList = getObjectList(request, objectlistid, getCustomList = getcustomlist, dateThreshold = dateThreshold, queryFilter = queryFilter)
        return objectList
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python manage.py test tests.atlasapi.test_object_list_filters -v 2`
Expected: PASS (8 tests total)

- [ ] **Step 5: Commit**

```bash
git add psat_server_web/atlas/atlas/apiutils.py psat_server_web/atlas/atlasapi/serializers.py psat_server_web/atlas/tests/atlasapi/test_object_list_filters.py
git commit -m "Apply VRA/RBPix/RA/Dec/Sherlock/spec-type filters in getObjectList"
```

---

### Task 3: Manual smoke test against a real list

Automated tests stop at Task 2 deliberately — `WebViewFollowupTransients4`/`WebViewUserDefined` are `managed=False` DB views with no fixture-loading infrastructure in this test suite (confirmed: no `conftest.py`, no schema-loading helper), so asserting actual filtered row counts needs real data, per the design spec's testing section.

**Files:** none (verification only)

- [ ] **Step 1: Baseline request — no filters**

Using an authenticated token against a dev/staging server:

```bash
curl -s -H "Authorization: Token <token>" "https://<host>/api/objectlist/?objectlistid=4" | python -m json.tool | head -5
```

Note the object count. Expected: identical to today's behaviour (this is a no-op change when no filter fields are supplied).

- [ ] **Step 2: Apply one numeric filter**

```bash
curl -s -H "Authorization: Token <token>" "https://<host>/api/objectlist/?objectlistid=4&vra_gte=0.8" | python -m json.tool
```

Expected: returned object count is less than or equal to the baseline, and every returned object's `vra` (or `realbogus_factor` in raw DB terms) is `>= 0.8`. Cross-check one returned object ID against the DB directly if anything looks off.

- [ ] **Step 3: Apply one string filter**

```bash
curl -s -H "Authorization: Token <token>" "https://<host>/api/objectlist/?objectlistid=4&sherlock_class=SN" | python -m json.tool
```

Expected: every returned object's `sherlockClassification` is exactly `"SN"`.

- [ ] **Step 4: Combine filters**

```bash
curl -s -H "Authorization: Token <token>" "https://<host>/api/objectlist/?objectlistid=4&vra_gte=0.8&sherlock_class=SN" | python -m json.tool
```

Expected: intersection of Steps 2 and 3's results.

- [ ] **Step 5: Confirm invalid input still 400s**

```bash
curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Token <token>" "https://<host>/api/objectlist/?objectlistid=4&vra_gte=not-a-number"
```

Expected: `400`.

- [ ] **Step 6: Commit** (only if Step 1-5 surfaced fixes)

If everything passed with no code changes, there is nothing to commit for this task — it's verification-only.
