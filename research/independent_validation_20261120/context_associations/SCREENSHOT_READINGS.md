# What do the matching inscriptions say, and do they cluster by location?

**Yes, there are descriptive location patterns, especially repeated Harappa pot marks. Most matches are short labels rather than full sentences.** All readings below remain proposals.

The [full table](results/screenshot_followup/readings_and_locations.html) lists every record with its existing proposed English reading, raw and normalized signs, material, actual findspot and recorded strata. [CSV](results/screenshot_followup/all_matching_readings_and_locations.csv), [site denominators](results/screenshot_followup/within_site_frequencies.csv), [formula groups](results/screenshot_followup/repeated_formulas.csv).

| Screenshot label | What the actual inscriptions say in the existing reading files | Where the matching objects occur |
|---|---|---|
| **790: bangle** | Three have only “Bangle.” H-1010 has “[lost sign], gem.” M-1630: “Matron/Lady Twin-House Bangle.” M-1631: “First-ward house, [290]; Two gems.” The gem/bangle difference is a retained reading-version difference. | Two certain examples at Harappa; four at Mohenjo-daro. Harappa's H-2578 is recorded in area E. Mohenjo-daro examples include MN and HR areas, rather than one recorded room. |
| **840: pair/pact** | Seven have only “Pair/Pact.” M-2080: “Ship/Kalam-Measure Pair/Pact.” M-1634: “[264], pair, [lost sign].” Nothing here independently establishes a physical pair of bangles or a legal pact. | Two certain examples at Harappa; seven at Mohenjo-daro, spread across DK/DKG, SD, HR and MN records. M-2081: DKG (S), 7VIII, room 20, depth -14.6 ft; M-2083: DKG (S), 7III, room 51, depth -16.3 ft. These are different recorded contexts. |
| **838: bone** | M-2106 and M-1651 share `240-838-585-740-400`: existing English “Junior of the High-star-Produce-Maiden house.” M-2086 and M-2102 share `838-482-740`: “Of the Produce-Hill-share house.” The screenshot's “bone” belongs to an older proposal; later Cuuper files use **produce**. These two sentences therefore do not support a single, stable bone translation. | All four at Mohenjo-daro, DK/DKG. M-2106: DKG, First Street, room/grid 22, depth -21.4 ft, phase I / Early. The other three have less complete context. Four rods, but only two distinct formulas. |
| **540: capacity measure** | H-1740 and H-1742 have `540-540`, earlier English “Two rice measures.” Four other pots have `540` alone, “Rice measure.” M-1379 has `920-540-740`, “Of the Month-Drum house.” “Rice” is part of an earlier proposed interpretation, not an additional rice sign or a residue finding. | Four at Harappa, two at Mohenjo-daro, one at Chanhu-daro. The two repeated marks are both Harappa F Trench 43, phase C / period 3. C-36 is recorded at locus 480, square 10/G. |
| **440: earthen vessel** | All twelve Harappa examples have only `440`, “Goblet/Corner.” M-1597 has a longer inscription, earlier English “Of the Received-Seven-First-ward-[999]-Three-Moon house.” “Received” and “goblet/corner” are different historical proposals for the sign. | Twelve at Harappa, one at Mohenjo-daro. Seven Harappa records explicitly give F Trench 43; one gives AB Trench 39N; those eight record phase C / period 3. Four lack detailed areas. |
| **645: gold weight** | Only M-2129 contributes: `817-002-645-017-898`, “two shares: Gold weight; Seven [898].” Sign 898 is unresolved; the grammar does not establish that seven is the object's own mass. | Mohenjo-daro, DK-E, Trench E1, room/grid `1-`, excavation `DK-E 2044bCLI:b`. No recorded stratum. |

## Corrections to the screenshot

**M-1644 is recorded as `840/790`, meaning an alternative identification.** It was included under both rows of the screenshot. It cannot confirm both readings. Excluding it gives **six certain 790 bangle faces and nine certain 840 bangle faces**, not seven and ten. Cuuper's `jobs/out/goods.md` already gives six/nine.

The screenshot also counts **faces**, not consistently physical objects. Its 50 bangle faces represent 49 object IDs: M-1639 has two faces, neither a target hit. Similarly 635 pottery faces represent 629 object IDs, and 42 rod faces represent 41 object IDs. The full table has 42 sign–record rows, representing 40 certain matching faces and the one ambiguous bangle shown in both possible sign groups. The screenshot's p-values are not retained as corrected statistics here.

## Does frequency relate to location?

It depends on the sign and on how many relevant objects each site contributes. Merging multiple faces by catalogue object ID:

| Proposed mark | Harappa: matching / local objects | Mohenjo-daro: matching / local objects |
|---|---:|---:|
| Bangle 790 | 2/7 bangles | 4/40 bangles |
| Pair/pact 840 | 2/7 bangles | 7/40 bangles |
| Rod sign 838 | 0/7 rods | 4/32 rods |
| Capacity mark 540 | 4/347 pots | 2/70 pots |
| Goblet/corner 440 | 12/347 pots | 1/70 pots |

Chanhu-daro supplies the remaining 540 example, 1/4 pots. Samples such as four pots or seven bangles are too small to establish a reliable site ranking from the percentages alone.

The strongest concrete observation is more specific than “Harappa has more 440”: **12/50 Harappa stamped pots carry the same standalone 440 mark, versus 0/22 Mohenjo-daro stamped pots**. Seven marked examples are at F Trench 43; that trench contains 22 catalogued stamped pots overall. This suggests a local practice of marking this vessel category. It does not by itself choose between a vessel/unit label, maker's mark, institution mark or another meaning. Same-text pots from a trench are not automatically products of one die, one workshop or one deposition.

For the bangles, the raw majority at Mohenjo-daro largely reflects its larger bangle sample. For rods, Mohenjo-daro already supplies most recorded rods. For gold, a single positive object cannot establish a geographical pattern. No new adjusted significance test was run for this descriptive reconciliation.

## What was already done, and what this adds

Cuuper's `jobs/out/goods.md` already describes the bangle concentrations, four rod examples and twelve Harappa pot marks. `jobs/out/metrology_ledger.md` compares vessel marks, and this continuation's earlier six-axis screen already tests many word/site/layer associations. These are credited rather than claimed as new discoveries.

The addition is the complete record-by-record linkage of these six screenshot contrasts to full existing readings, exact recorded locations, local denominators and ambiguous-sign/version corrections. No new translation is created.

Reproduce with Python 3.9+:

```sh
python research/independent_validation_20261120/context_associations/screenshot_followup.py --lipi-metadata /path/to/metadata_filtered.csv
```

The input hash is recorded in the summary. Source catalogue: `translation_catalogue/results/all_inscriptions.csv`; alternative-sign provenance: Lipi `metadata_filtered.csv`; earlier 838 alternatives: `sound_v3_values.py`, `sound_v5_values.py`, `jobs/out/goods.md` and `jobs/out/sound_list_v5.md`.
