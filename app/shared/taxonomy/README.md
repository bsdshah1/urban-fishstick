# Taxonomy — TypeScript SDK

This directory contains TypeScript definitions and a resolver for the canonical
curriculum taxonomy used across the project.

## What is here

| File | Purpose |
|---|---|
| `year-groups.ts` | `YearGroupId` type + canonical year group definitions (EYFS – Year 6) |
| `strands.ts` | `StrandId` type + canonical maths strand definitions |
| `white-rose.ts` | White Rose block/term canonical IDs and display names |
| `resolver.ts` | `resolveYearGroupId`, `resolveStrandId`, etc. — normalise free-text labels to canonical IDs |
| `index.ts` | Re-exports everything for consumers |

## Who calls this

These files are **not imported by the Python backend**.  They are intended as a
frontend/client SDK — for example a React or plain-JS UI that needs to resolve
a user-typed year group label (e.g. `"year 4"`, `"Y4"`, `"Year Four"`) to the
canonical ID `"y4"` before sending it to the API.

The Python backend performs equivalent resolution in
`app/domain/curriculum/linker.py` via `_normalize_year()` and
`_normalize_token()`.

## ID convention

TypeScript canonical IDs use **hyphen-separated lowercase** (e.g. `y4`,
`number-multiplication-division`).  The Python backend currently uses
underscore-separated lowercase for internal token normalisation.  When
building API contracts that cross the Python/TypeScript boundary, prefer
the TypeScript hyphen convention in JSON payloads and translate on the
Python side.
