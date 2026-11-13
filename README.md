# Mechanical engineering roles around Lexington, KY

Static listing of mechanical engineering roles within about a 45-minute drive of
Lexington, KY, built with the [Astryx design system](https://astryx.atmeta.com)
and published on GitHub Pages.

Live: https://jacoblbagent.github.io/lexington-jobs/

## Page

| File | Contents |
|------|----------|
| `docs/index.html` | Mechanical engineering roles (63) |

The file is self-contained: inlined CSS, no network requests. One inline script
is added after render (see `scripts/table-sort.js`) so the column headers sort:
click a header for ascending, again for descending, a third time to return to
the rendered "newest first" order.

The page also carries a Location filter, added after render from
`scripts/location-filter.{js,css}`: a multi-select built from the Location cells,
sorted by number of roles, with Lexington and Georgetown checked on first paint.
Checkbox changes apply instantly; Default restores that opening set and All
clears the filter, and an empty selection reads as unfiltered.

Each listing carries its requirements as a sub-row underneath it, added after
render by `scripts/inject-requirements.py` from `src/requirements.json`, and
folds away on a row click (`scripts/collapse-requirements.js`).

## Rebuilding

```bash
python3 scripts/collect-jobs.py       # LinkedIn guest search -> jobs.json
python3 scripts/scope-filter.py       # mechanical engineering scope -> jobs.me.json
python3 scripts/collect-requirements.py  # posting pages -> requirements + level cache
python3 scripts/build-data.py         # -> src/jobsData.ts
bash scripts/build-docs.sh            # -> docs/index.html
git add -A && git commit -m "Rebuild pages" && git push
```

`scripts/collect-requirements.py` copies the cache into `src/requirements.json`;
run `cp ~/.hermes/cache/scratch/lexington/requirements.json src/requirements.json`
after it finishes if you only need the page rebuilt.

## Data

`src/jobsData.ts` holds the listings the page renders. Level is LinkedIn's own
seniority field, read from the posting page; postings that report nothing show
`Not listed`. Listings were collected on November 13, 2026.

`jobs.json` is the raw collected dump: 353 unique postings from LinkedIn's guest
search, 322 of them inside the city whitelist (Lexington, Georgetown,
Nicholasville, Versailles, Frankfort, Winchester, Paris, Richmond, Wilmore,
Midway, Lawrenceburg, Mt. Sterling, Berea, Danville, Cynthiana, Harrodsburg,
Stanford, Shelbyville and the I-64 / I-75 towns around them).

`jobs.me.json` is that dump narrowed to mechanical engineering roles: titles
containing mechanical or a mechanical-function engineering title (manufacturing,
process, product, production, design, tooling, test, NDT, reliability, HVAC,
piping, project, applications), with other disciplines dropped (civil,
structural, water, transportation, electrical, controls, software, ML,
healthcare) and technician titles kept only when the title also says engineer.

`src/requirements.json` holds each listing's requirements, keyed by job id, with
`req` (up to eight items) and `total` (how many the posting carried, so a list cut
at the cap says so).

## Sources

LinkedIn guest postings only. Indeed and employer career pages are not included;
they would add roles LinkedIn does not index.
