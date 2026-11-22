# Proposed words, materials and recorded findspots

The [other inscriptions on the same object types at those locations](SAME_CONTEXT_READINGS.md) supply complete local comparison groups, including all 22 stamped F Trench 43 pots and eight MN bangles. They distinguish actual proposed rice-sign presence from older English “rice measure” wording, expose the latter on a bangle, and retain all 678 bangle/pot object records rather than only matching examples.

The [six screenshot contrasts, full readings and actual locations](SCREENSHOT_READINGS.md) now have a [complete HTML table](results/screenshot_followup/readings_and_locations.html). It corrects one ambiguous bangle counted under two signs, distinguishes faces from objects, and shows local denominators. This is descriptive source collation, not another association test. The corrected [physical-data assessment](PHYSICAL_NEXT_TESTS.md) withdraws cross-city size/rank testing as a new direction: `size_3_titles.py` and `size_3b_redesign.py` already investigate it. Other extensions require additional source/image or vessel-measurement data.

**The descriptive patterns are real, but the stricter comparisons are less decisive.** The proposed tax/levy sign is concentrated on copper objects, and the proposed measure sign is concentrated at Harappa. Those patterns overlap object-type and material differences. Two contrasts pass the primary whole-screen cutoff; neither remains below 0.05 when repeated complete inscription formulas are downweighted.

The screen uses **4,476 Lipi physical-object / known-copy-batch representatives**, combines all faces of each object, and tests **81 proposed word/allograph groups**. It evaluates **7,773 contrasts**, using **49,999 conditional permutations** per axis and maximum-statistic correction within each axis plus correction across all six axes. These are retrospective associations, not independently established translations.

## Concrete descriptive examples

| Proposed word | Material or recorded location | Among word-bearing objects | Among other eligible objects | Controlled comparison |
|---|---|---|---|---|
| tax/levy (*vari (hatched 840)) | Copper | 29/38 (76.3%) | 148/3662 (4.0%) | Cannot separate material from object type/site |
| bangle (*vaḷai) | Copper | 9/40 (22.5%) | 168/3660 (4.6%) | Whole-screen p=0.039; formula-weighted p=0.063 |
| measure (*aḷa / *akal) | Harappa | 486/523 (92.9%) | 1292/3926 (32.9%) | Whole-screen p=0.1711; formula-weighted p=0.3455 |
| measure (*aḷa / *akal) | Faience | 182/435 (41.8%) | 174/3265 (5.3%) | Whole-screen p=1; formula-weighted p=1 |
| tax/tribute (*iṟai/*iru) | Harappa / area FTrench I | 20/154 (13.0%) | 118/3120 (3.8%) | Whole-screen p=1; formula-weighted p=1 |

A large raw percentage is not an independent material or city effect. For example, all 29 copper occurrences of the tax/levy group are already expected after matching on site, object kind and inscription-length band. The present data cannot separate that material association from those factors.

## The two primary corrected contrasts

| Proposed reading | Recorded pattern | Whole-screen p | Formula-weighted whole-screen p |
|---|---|---|---|
| bangle | 9/40 are Copper; matched expectation 4.13 | 0.039 | 0.063 |
| 7 | Mean within-area depth percentile 30.7%, versus 50.5% for other objects; lower is shallower | 0.03972 | 0.05712 |

No city, excavation-area, room/building or recorded-layer contrast passes the stated primary whole-screen correction. That is not proof that those associations are absent. Sparse contexts and correction across thousands of contrasts limit sensitivity.

The numeral-seven depth pattern is a relationship with **recorded excavation depth**, not a dated language change. Depths are ranked only within the same Mohenjo-daro excavation area; the calculation does not equate depth with a calendar date or compare metres across unrelated areas.

## Actual findspots behind the primary findings

All matching analysed objects and faces are released in `all_finding_occurrences.csv`. For example:

- **H-2251**: Harappa — Excavation area: FTrench 43; Excavation number: H2000-4498Figure 35.05. Phase / stratum: C; Period: 3; Catalogue chronology: Period 3C. Material: Copper.
- **H-2254**: Harappa — Excavation area: E-; Excavation number: H2001-5080Figure 37.14. Phase / stratum: B/C; Period: 3; Catalogue chronology: Period 3B/C. Material: Copper.
- **H-2249**: Harappa — Recorded depth: -0.0 m; Excavation number: H94-2197Figure 17.02. Stratum / phase not recorded. Material: Copper.
- **H-2250**: Harappa — Recorded depth: -0.0 m; Excavation number: H94-2198Figure 17.01. Stratum / phase not recorded. Material: Copper.
- **M-543**: Mohenjo-daro — Excavation area: DK-; Excavation number: DK1838. Stratum / phase not recorded. Material: Copper.

## What was controlled

| Outcome | Comparison holds fixed | Eligible events | Tested contrasts |
|---|---|---:|---:|
| material | site, object kind, length band | 3700 | 473 |
| city | object kind, material, length band | 4449 | 646 |
| excavation_area | site, object kind, material, length band | 3274 | 2292 |
| room_or_building | site, excavation area, object kind, material, length band | 2175 | 2763 |
| recorded_layer | site, excavation area, object kind, material, length band | 2366 | 1522 |
| depth | site, excavation area, object kind, material, length band | 1212 | 77 |

Length bands are 1, 2–3, 4–6 and 7+ recorded sign tokens. Word groups must occur on at least ten representative objects overall and on at least five objects in the axis being tested. Material/site/area/layer targets need at least twenty objects; exact room/building labels need eight. Missing material, site and layer values are not filled. Layer labels are site-specific recorded phase/period strings, not pooled “early/middle/late” bins. Catalogue-mapped chronology is displayed to the reader but is not substituted for the raw layer labels in the test.

The formula-weighted check gives each exact whole-object inscription formula a total weight of one across the corpus, regardless of how many objects repeat it. It keeps every findspot rather than choosing an arbitrary representative room for a repeated formula. This is a repetition sensitivity, not complete elimination of every workshop or excavation dependence.

Finite-permutation resolution is 1/50,000 before correction. Primary p-values are two-sided. Maximum statistics preserve dependencies among the word groups and target labels by using shared conditional permutations. The second weighting is a stricter sensitivity, not an alternative route for promoting whichever result looks better.

## What was already in the repo

This does not claim to discover the tax/copper-tablet association for the first time. Earlier work already tested city/object functions and broad chronological bins (`jobs/out/key6b_readings_key5_atlas.md`); the independent continuation already ran site-controlled sign/artifact contrasts (`reports/statistical_report.md`). The additional work here is the full 81-group, six-axis comparison of recorded material and local context, the whole-screen correction, whole-formula weighting, complete contrast export and links to actual findspots.

## Files

- `associations.html`: searchable counts, adjusted results and links to matching catalogue records.
- `all_descriptive_and_adjusted_associations.csv`: every descriptive contrast, including comparisons that cannot be separated from the control variables.
- `all_associations.csv`: all 7,773 estimable adjusted tests.
- `all_finding_occurrences.csv`: every analysed object/face behind the two primary findings.
- `events.csv`, `word_groups.csv`, `summary_by_axis.csv`, `summary.json`: units, labels, sample sizes and results.
- `*_nulls.npz`: all primary and formula-weighted maximum-statistic null arrays.

Labels remain frozen hypotheses from the existing key. A bijective renaming of a sign would retain the same archaeological association, so these patterns alone cannot identify its spoken word or exact meaning.

Reproduce with the pinned Lipi metadata and the continuation virtual environment:

```sh
python research/independent_validation_20261120/context_associations/run.py --lipi-metadata /path/to/metadata_filtered.csv --permutations 49999
python research/independent_validation_20261120/context_associations/present.py
python research/independent_validation_20261120/context_associations/check.py
```

The calculation took about 96 seconds with one BLAS thread. No Colab units were used.

## Narrow copper-tablet comparison

[All 29 sign-845 copper specimens and the within-copper controls](results/COPPER_845.md) are released separately, with a [readable HTML table](results/copper845.html). All 29 contain 407. There is no exact 845-removed inscription family with both positive and negative specimens, so the fully matched semantic effect cannot be estimated. No independent archaeological function is assigned from a room code or a proposed translation. Reproduce with `python research/independent_validation_20261120/context_associations/copper845.py`, then `check_copper845.py`.

## Additional archaeological source evidence

[Which clues were already considered?](CLUE_FOLLOWUP.md) distinguishes old tests from remaining source work. The [accession-linked production table](results/archaeology.html) adds published context for 16 existing Harappa objects, including a four-tablet partial-production group and a proposed mould/product pair. The gold-hoard study identifies bead-cap inscriptions not yet joined to catalogue rows. These are retrospective source annotations and recovery leads, not new accepted meanings. Reproduce the inventories with `clue_followup.py` and `archaeology_followup.py`.
