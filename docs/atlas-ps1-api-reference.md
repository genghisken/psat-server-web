# ATLAS ↔ Pan-STARRS (ps1) REST API reference

**Purpose:** working notes for porting `ps1/psdbapi` up to parity with `atlas/atlasapi`, **excluding all VRA endpoints/models** (VRA — Virtual Research Assistant — is ATLAS-only; Pan-STARRS has no equivalent and none should be added). Written 2026-09-08 after reading both API apps; re-verify against the code before trusting specifics, this will drift.

## Where things live

| | ATLAS | Pan-STARRS (ps1) |
|---|---|---|
| API app | `atlas/atlasapi/` | `ps1/psdbapi/` |
| API urls | `atlasapi/urls.py` | `psdbapi/urls.py` |
| API views | `atlasapi/views.py` (389 lines) | `psdbapi/views.py` (72 lines — only `ConeView` + token auth live) |
| API serializers | `atlasapi/serializers.py` (620 lines) | `psdbapi/serializers.py` (512 lines, **but everything past `ConeSerializer` — line 90 — is commented out**, not deleted) |
| DB-query helpers used by the API | `atlas/atlas/apiutils.py` | **does not exist yet** — needs creating |
| Models | `atlas/atlas/models.py` | `ps1/psdb/models.py` |
| Object table | `AtlasDiffObjects` (`atlas_diff_objects`) | `TcsTransientObjects` (`tcs_transient_objects`) |

## What's already effectively ported (near-identical)

`authentication.py` and `permissions.py` diff as whitespace-only between the two apps — `ExpiringTokenAuthentication`/`QueryAuthentication` and `HasReadAccess`/`HasWriteAccess` are already in parity. `throttling.py` likewise. `ConeView`/`ConeSerializer`/`ObtainExpiringAuthToken` are live and working on ps1, adapted for field-name differences (see table below).

**On the commented-out block in `psdbapi/serializers.py`:** this was a deliberate straight copy-paste from `atlasapi/serializers.py`, kept commented as a reference for shape/fields — it is **not** meant to be uncommented and lightly adapted. When each serializer gets ported, that commented copy gets **replaced completely** with a fresh implementation (then deleted from the file, not left commented alongside the new code). The main model difference driving the rewrite: `AtlasDiffObjects` → `TcsTransientObjects` (see traps below for the rest).

## Endpoint parity — what's missing on ps1 (VRA rows excluded on purpose)

| ATLAS endpoint | ps1 status | Notes |
|---|---|---|
| `api/cone/` | ✅ done | |
| `api/auth-token/` | ✅ done | |
| `api/objects/` | ❌ commented stub only | `ObjectsSerializer` in `psdbapi/serializers.py` line ~90, calls `candidateddcApi` — needs a ps1 equivalent in a new `psdb/apiutils.py` |
| `api/objectlist/` | ❌ commented stub only | `ObjectListSerializer`, needs `getObjectList`/`buildObjectListQueryFilter` ported |
| `api/objectgroups/` (POST, write) | ❌ commented stub only | `TcsObjectGroupsSerializer` — **see FK gotcha below** |
| `api/objectgroupslist/` | ❌ commented stub only | `TcsObjectGroupsListSerializer` |
| `api/objectgroupsdelete/` | ❌ commented stub only | `TcsObjectGroupsDeleteSerializer` — same FK gotcha |
| `api/externalxmlist/` | ❌ **no stub at all** | `ExternalCrossmatchesListSerializer` was added to ATLAS 2024-09-24, after the ps1 scaffold copy was made — needs writing fresh, not just uncommenting. Needs `getExternalCrossmatchesList` in apiutils. ps1's `TcsCrossMatchesExternal` model already exists though. |
| `api/objectdetectionlist/` | ❌ **no stub at all** | Same 2024-09-24 gap as above. `ObjectDetectionListSerializer` — despite the name, just updates `detection_list_id`/`date_modified` directly on the object row (snooze/unsnooze), no separate detections table. ps1's `TcsTransientObjects.detection_list_id` FK already exists. |
| `api/vrascores/`, `api/vrascoreslist/`, `api/vratodo/`, `api/vratodolist/`, `api/vrarank/`, `api/vraranklist/` | **out of scope** | Do not port — ATLAS-only concept, no `TcsVra*` models on ps1 |

## Cross-cutting piece that doesn't exist on ps1 at all: request logging

ATLAS's `atlasapi/views.py` has a `LoggingAPIView(APIView)` base class (search "HELOISE SHENANIGANS" in that file) that every view subclasses — it writes a `TcsAPIUsageLog` row per request via `self.log_request(validated_data)`. **ps1 has neither `LoggingAPIView` nor a `TcsAPIUsageLog` model.** Decide up front whether the port should bring this along (probably yes, for consistency) — if so it needs a `TcsAPIUsageLog` model added to `ps1/psdb/models.py` (check whether the `tcs_api_usage_log` table already exists in the ps1 DB schema or needs a migration) before wiring it into views.

## Model/field-name traps when porting serializers

These are the concrete places a naive copy-paste from `atlasapi` breaks against ps1's schema:

- **Object model & PK**: `AtlasDiffObjects` → `TcsTransientObjects`, table `atlas_diff_objects` → `tcs_transient_objects`.
- **Designation field**: `atlas_designation` → `ps1_designation`.
- **Coords**: ATLAS cone search returns bare `ra`/`dec`-like fields; ps1's `ConeSerializer` already adds explicit `ra`/`dec` from `ra_psf`/`dec_psf` — carry that pattern into any new serializer that returns object coordinates.
- **Cone search radius cap**: ATLAS caps at 300 arcsec, ps1 already diverges to 1000 arcsec in the existing `ConeSerializer` — intentional, not a bug, don't "fix" it back to 300 when porting other endpoints that reuse radius logic.
- **`TcsObjectGroups.object_group_id`**: on ATLAS this is a plain `IntegerField`, so `TcsObjectGroups(object_group_id=<int>)` works directly. On **ps1 it's a `ForeignKey` to `TcsObjectGroupDefinitions`** — constructing with a bare int against the field named `object_group_id` will fail; you need `object_group_id_id=<int>` (or fetch/pass the model instance) instead. This bites both `TcsObjectGroupsSerializer` (insert) and `TcsObjectGroupsDeleteSerializer` (lookup filter) when ported verbatim.
- **`TcsObjectGroups.id`**: ATLAS uses `BigIntegerField(primary_key=True)` (manually assigned), ps1 uses `AutoField(primary_key=True)` (auto-increment) — there's a commented-out note in ps1's own model ("can't be used as an auto increment by Django!") flagging this was a deliberate fix. Don't copy ATLAS's manual-PK insert pattern if one exists in `apiutils.py`.

## Building `ps1/psdb/apiutils.py`

Doesn't exist yet. ATLAS's `atlas/atlas/apiutils.py` has these top-level functions (module docstring-free, so read the function bodies, not just signatures):

- `candidateddcApi(request, atlas_diff_objects_id, mjdThreshold=None)` — single-object detail lookup, needs a ps1 rename/adapt (object id param, model, designation field).
- `buildObjectListQueryFilter(validated_data)` + `getObjectList(request, listId, getCustomList=False, dateThreshold=None, queryFilter=None)` — list-by-detection-list-id.
- `getCustomListObjects(request, objectid=None, objectgroupid=None, queryFilter=None)`.
- `getExternalCrossmatchesList(request, externalObjects=[])`.
- Skip porting: `getVRAScoresList`, `getVRATodoList`, `getVRARankList` — VRA-only, out of scope.

ps1 already has reusable query building blocks in `ps1/psdb/commonqueries.py` and cone/crossmatch display logic in `ps1/psdb/views.py` (e.g. `displayExternalCrossmatches` around line 2614) that predate the API and may be worth reusing rather than re-deriving from ATLAS's version.

## Suggested porting order

1. `apiutils.py` for ps1 (no VRA functions) — needed by everything else.
2. Rewrite `ObjectsSerializer`, `ObjectListSerializer` in `psdbapi/serializers.py` (using the commented block only as a reference, then deleting it), wire into `views.py` + `urls.py`.
3. `TcsObjectGroups*` serializers — mind the FK gotcha above. Same rewrite-then-delete-the-comment approach.
4. `ExternalCrossmatchesListSerializer` + `ObjectDetectionListSerializer` — write fresh, no existing commented reference for these two.
5. Decide on `TcsAPIUsageLog`/`LoggingAPIView` and add if wanted, last (cross-cutting, easy to retrofit once endpoints exist).

## Non-goals

Do not add `api/vrascores/`, `api/vrascoreslist/`, `api/vratodo/`, `api/vratodolist/`, `api/vrarank/`, `api/vraranklist/`, or any `TcsVra*` model/serializer/view to ps1. If a future task changes this, update this doc.
