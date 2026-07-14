# Eyeball list filtering (Issue 2) — design

## Problem

`ObjectListView` (`atlasapi/views.py`) lets a client fetch every object on a
given followup list (e.g. the eyeball list, id 4) via `objectlistid`, with
only `getcustomlist` and `datethreshold` as constraints. There is no way to
constrain by VRA score, RB score (RBPix), spec type, RA, Dec, or Sherlock
classification server-side — clients must pull the entire list and filter
client-side, which wastes bandwidth and DB read load for large lists.

## Scope

Only `ObjectListView` / `ObjectListSerializer` / `getObjectList()`
(`atlas/apiutils.py`). No other endpoint is in scope for this pass.

## Fields and semantics

| API field | Type | Maps to (ORM lookup) | Semantics |
|---|---|---|---|
| `vra_gte` | FloatField, optional | `vra__gte` | VRA score lower bound (inclusive) |
| `vra_lte` | FloatField, optional | `vra__lte` | VRA score upper bound (inclusive) |
| `rb_pix_gte` | FloatField, optional | `rb_pix__gte` | RBPix lower bound (inclusive) |
| `rb_pix_lte` | FloatField, optional | `rb_pix__lte` | RBPix upper bound (inclusive) |
| `ra_gte` | FloatField, optional | `ra__gte` | RA lower bound (inclusive) |
| `ra_lte` | FloatField, optional | `ra__lte` | RA upper bound (inclusive) |
| `dec_gte` | FloatField, optional | `dec__gte` | Dec lower bound (inclusive) |
| `dec_lte` | FloatField, optional | `dec__lte` | Dec upper bound (inclusive) |
| `sherlock_class` | CharField, optional | `sherlockClassification` | exact match |
| `spec_type` | CharField, optional | `observation_status` | exact match |

Only `gte`/`lte` are supported for the numeric fields (min/max band), not the
full `lt/lte/gt/gte` set the website's `filterGetParameters()` supports —
covers the realistic "above X" / "below Y" use case with half the fields.

String fields are exact match only, mirroring the website's existing
behaviour for these same two columns.

All ten fields are optional and default to `None`/absent — omitting all of
them preserves today's "return the whole list" behaviour exactly.

Confirmed via `atlas/dbviews.py`: all six underlying columns (`vra`,
`rb_pix`, `ra`, `dec`, `sherlockClassification`, `observation_status`) exist
on both `WebViewAbstractFollowup` (backs the regular numbered lists, e.g.
`WebViewFollowupTransients4` for the eyeball list) and the user-defined-list
model, so the same filter dict applies to both branches of `getObjectList()`.

## Implementation approach

New fields are added directly to `ObjectListSerializer`, not implemented by
reusing the website's `filterGetParameters()` (which reads only
`request.GET` — `ObjectListView` accepts both GET and POST, and Issue 1
already established that GET-only param handling silently misses POST
calls). Building the filter from `serializer.validated_data` keeps this
endpoint consistent with the Issue 1 logging design, which already treats
`validated_data` as the single source of truth for "what was requested" —
`log_request()` needs no changes, since these new fields are logged for
free.

In `ObjectListSerializer.save()`: build a `queryFilter` dict by mapping each
non-`None` validated field to its ORM lookup key (per the table above), then
pass it down to `getObjectList()` as a new optional parameter.

In `getObjectList()`: apply `.filter(**queryFilter)` (if non-empty) on top
of the existing `listId`/`dateThreshold` filtering, on both the
`followupClassList[...]` branch and the `WebViewUserDefined` (custom list)
branch.

## Error handling

Standard DRF validation: malformed values (e.g. non-numeric `vra_gte`) fail
`serializer.is_valid()` and return the existing 400 + `serializer.errors`
response, same as every other endpoint in this codebase. No new error
handling needed.

## Testing

Manual smoke test during pairing: request the eyeball list with no filters
(confirm unchanged behaviour), then with each of the three filter types
(numeric range, sherlock_class, spec_type) individually and combined,
confirming the returned object count narrows as expected and matches a
manual DB check.
