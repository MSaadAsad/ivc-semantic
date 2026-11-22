# Existing proposed readings and archaeological findspots

Prepared 21 November 2026, before the reconstruction-table comparison requested in the same task.

The catalogue covers **all 9,252 face/line records** in the repository's combined corpus: 5,679 Lipi faces and 3,573 Mahadevan lines. These are catalogue observations, **not 9,252 independent artifacts or established translations**. The same object can have several faces and occur in both catalogues. Paired records and repeated texts remain visible.

- `results/all_inscriptions.csv`: one row per corpus observation, with an existing proposed reading, its source, every available recorded excavation field, current 163-key literal meanings, unknown tokens and catalogue identifiers.
- `results/all_existing_reading_versions.csv.gz`: 50,340 preserved reading-version records from 31 structured sources. Includes earlier English renderings, structural labels, formula-root readings and object-level readings that may span several faces. This is an archive of proposals, not independent linguistic evidence. The build emits the uncompressed CSV; the release compresses it for Git.
- `results/reading_records_outside_main_corpus.csv`: 17 additional frontier source reading records not safely joinable to the combined corpus, with whatever site/reference the source supplies. No inferred join is silently forced. Sixteen older star readings were recovered through the source script's explicit `M{textnum}` convention, not a guessed CISI identity.
- `results/all_163_sign_readings.csv`: every current sign value, English meaning, original evidence note and occurrence-site list.
- `results/catalogue.html`: standalone searchable catalogue; search English meanings, references, signs, cities or excavation context.
- `results/by_city.csv` and `results/summary.json`: record counts by the source's site labels and catalogue totals.

The downloadable Excel workbook contains the main catalogue and sign meanings. The download bundle also includes the full reading-version CSV and copies of the existing root-level reading books (`READINGS*.md`, `CORPUS.md`), preserving prose examples not represented as their own structured CSV rows. Original books are archival source material, not newly authenticated translations.

The HTML now puts a **Found at** description immediately beside each proposed translation: city, recorded excavation area, block/house, room/grid, depth and excavation number. A separate **Recorded strata** column displays phase, period and catalogue chronology. It has material and meaning filters, context-specific links, and an example button for M-1954. The [word-pair HTML](../proto_reconstruction/results/word_pairs.html) also shows five actual findspot examples per sign and links to every occurrence. The [context-association table](../context_associations/results/associations.html) links word/material/layer/location comparisons to the matching catalogue records. Catalogue counts include separate faces and paired catalogues; correlation counts use representative Lipi objects.

`verify_html.mjs` runs an isolated headless Chrome check of the visible findspot, meaning/material filters, grouped-allograph links, word-pair examples, and association-to-findspot links. M-1954 is checked against the actual fields: Mohenjo-daro, DKE, Trench E-, room/grid -1090/1980, depth -9.0 ft. These raw excavation codes are not interpreted as geographic coordinates or building functions.

## What the fields mean

`existing_proposed_translation` preferentially preserves the Key6B English reading, then Key5B, then the latest full English corpus export. Where those do not supply a reading, an existing literal/formula or structural reading is retained. Every record identifies its source. Older alternatives remain in the version archive. The fluent reading and the 163-key literal columns can differ because they come from different versions; the latest literal mapping does not silently rewrite the earlier prose.

`current_163_key_literal_meanings` and `current_163_key_roots` apply the already-frozen 163-sign proposal mechanically, without inventing missing words, grammatical relations or English sentences. “Full proposed sign assignment” means every token has a proposed label; this is not a decipherment success. Broken inscriptions can have all their surviving tokens assigned.

The raw excavation area, block/house, room/grid, depth, period, phase, chronology and excavation number come from the committed Lipi metadata. For Mahadevan entries, `locus` and `level` are retained **as catalogue codes**, not expanded into unsupported buildings or archaeological interpretations. Missing fields stay missing. A site label is not a building context, and a manufacturing function inferred from a proposed reading is not a findspot.

Calculated “early/middle/late” depth-band categories in earlier analysis are not substituted for the raw chronology. `reading_validated` is false for every entry. No independent human reading or excavation-report authentication of every object has been represented as completed.

## Reproduce

Python 3.9+, standard library. Extract the already-committed metadata into a scratch location if using a sparse checkout:

```sh
git show d16d038d2287bf3f054f113efb967dcc1a6fda5c:research/data/open_prototype/lipi/metadata_filtered.csv > /tmp/ivc-lipi-metadata.csv
python research/independent_validation_20261120/translation_catalogue/build.py --lipi-metadata /tmp/ivc-lipi-metadata.csv
python research/independent_validation_20261120/translation_catalogue/check.py --lipi-metadata /tmp/ivc-lipi-metadata.csv
```

The optional `workbook.mjs` uses the desktop's bundled `@oai/artifact-tool` to export the user-facing workbook; CSV/HTML analysis does not require it. Raw authoring JSON, uncompressed version CSV and the runtime dependency symlink are not committed.
