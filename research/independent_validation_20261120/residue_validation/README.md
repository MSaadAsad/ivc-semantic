# Can proposed food words predict independently measured vessel contents?

**No verified inscription–residue pairs were recovered. We therefore ran no semantic validation test.** This finding neither strengthens nor weakens the decipherment. It identifies the missing object-level evidence needed to test it.

The proposed experiment is concrete: if a pot inscription is claimed to label **millet**, does an independent analysis of that same pot find millet? A valid comparison needs both records to identify the **same physical vessel**, a prior interpretation that actually predicts its contents, and an analytical method capable of distinguishing that food. Being from the same city or trench is insufficient.

## What this continuation adds

Earlier continuation notes proposed residue/contents validation. In the inspected upstream reports and scripts we found no implemented join of chemical sample records to inscribed pots, nor scored results from such a join. This is a bounded prior-work finding, not a claim to have read every archived source: a full upstream `git grep` encountered unmaterialized objects in the partial clone. Filename inventory and materialized-source searches were also checked. Existing files calling statistical leftovers “residue” are not food-residue analyses.

The addition here is a reproducible source inventory, actual object-identity search, and a six-vessel target list. It is **not a completed new test of a reading**, and the general idea of using residues is not claimed as novel.

## What was recovered

| Source | Reported pottery samples | Archaeological rows in recovered main data | Relevant catalogue overlap |
|---|---:|---:|---|
| Chakraborty et al. 2020, Kotada Bhadli | 59 | 59 | No inscribed pottery from this exact site in the current catalogue |
| Suryanarayan et al. 2021, seven northwest Indian sites | 172 | 122 | Alamgirpur: 3 inscribed pots; Farmana: 2; Rakhigarhi: 1 |
| García-Granero et al. 2022, Datrana/Loteshwar/Shikarpur | 28 | 28 | Shikarpur: 7 inscribed pots |
| **Three core studies** | **259** | **209** | **13 same-site pots; zero verified same-object pairs** |

These are source sample counts, not 259 independent inscriptions or necessarily 259 distinct complete vessels. The Cambridge CSV contains two additional **modern references**, excluded from the archaeological count. Its 42-page SI3 vessel-image supplement supplies **49 low-yield sample IDs**. The published total minus the CSV count is 50; one entry remains unreconciled. We preserve the discrepancy rather than inventing a missing record. Low lipid yield is not evidence that a vessel never held plants.

**Additional route checked:** Suryanarayan's 2019 doctoral thesis lists five sherds labelled Mohenjo-daro and five labelled Kalibangan, from an old teaching collection. The author explicitly describes uncertain provenance and missing excavation context. Those labels give 159 additional inscribed-pottery candidates in our catalogue, including three with proposed food signs, but no verified same-object pair. They are kept in a separate ten-row input and are not pooled with securely excavated samples. Other thesis material overlaps later publications and is not counted again. Kalibangan yield assignments conflict between thesis tables; no quantitative correction is guessed.

## Meanings and target vessels

The original 163-reading key was frozen before this work. For this feasibility check we selected its direct rice, millet/grain, paddy and sesame proposals: **215/216, 803/804/806/807, 831/833, 854**. Selection of this nine-sign contents group was retrospective, not a preregistration or blind test. We did not change any proposed reading to fit chemistry.

Across **635 Lipi pottery faces on 629 catalogue objects**, just six objects contain these signs:

| Reference | Site | Proposed food meaning | Recorded excavation number |
|---|---|---|---|
| H-1417 | Harappa | Millet/grain, sign 803 | -786 |
| H-2568 | Harappa | Millet/grain, sign 806 | H95-2476Figure 39.05 |
| H-1731 | Harappa | Millet/grain, sign 806 | H96-3165Figure 16.08 |
| M-2003 | Mohenjo-daro | Paddy/ear of paddy, sign 831 | Channel 82-1535798 |
| M-1576 | Mohenjo-daro | Millet/grain, sign 803 | Not recorded (`-`) |
| M-1599 | Mohenjo-daro | Rice, sign 215 | SD 2976 |

These are **future source/laboratory targets**, not six successful residue matches. None of the 13 pots from the core studies' shared sites carries a target sign. Older English translations are retained separately: for example H-1417 previously called sign 803 “house,” whereas the frozen current key says “millet/grain.” That version difference is not hidden or counted as validation.

Sign 413 is currently **grain-tax/cut**, which does not directly predict the contents of its carrier. A fish-shaped sign read as **star** does not predict fish remains. No current dairy reading is introduced simply because dairy chemistry is available.

## Identity search and its limits

`run.py` merges faces of the same catalogue object, preserves each face's sign sequence, and compares laboratory IDs to catalogue references/excavation numbers within the same site. Exact normalized identifier equality would only be a candidate for source confirmation; there were no such hits. This automated search cannot resolve an undocumented change of numbering.

A separate manual contextual check found catalogue grid `ID5` at Farmana and residue contexts `1D5-8007` for FRN15/16/17. These may share an I/1 reading of a grid label. They do **not** share a vessel accession number, and three nearby samples cannot each be assumed to be the inscription-bearing pot. The possible inscription counterpart has proposed **house** sign 740, not a target food sign. SI3 photographs for these three samples and the thesis's five Mohenjo-daro specimens were inspected without a positive identification. We do not claim every photographed pot is uninscribed.

This search covers the three recovered datasets plus the separately identified teaching-collection group. It is not an exhaustive survey of every residue study. The 2022 detailed vessel-description supplement, full 1995 Nausharo article and 2025 Karanpura/Ropar sample tables remain unrecovered. See [source URLs, access limits and licences](SOURCES.md).

## What would make the test possible?

1. Recover an accession-number crosswalk or a diagnostic photograph connecting an inscribed vessel to an existing residue sample. The six listed food-sign vessels supply exact catalogue targets to pursue.
2. If no existing analysis matches, obtain permission for suitable residue/starch analysis of inscribed targets and comparable control vessels. One pot would be a case study; an adequately sized series is needed to compare predictions.
3. Before scoring, state whether the reading predicts contents, an owner/name, or a transaction. A millet name does not automatically mean millet was stored in that pot.
4. Use measurements that distinguish the prediction. Starch can sometimes distinguish cereal categories; a broad animal-fat or plant-oil signal cannot establish sesame, and non-detection alone cannot falsify a food label. Define controls, handling of uncertainty and success criteria before viewing fresh results.

No p-value, accuracy score, or “failed reading” is reported from a dataset with zero verified test pairs.

## Files and reproduction

- [Readable HTML](results/feasibility.html), [summary](results/summary.json), [209 source sample rows](results/residue_sample_inventory.csv).
- [13 core same-site pots](results/same_site_inscribed_pots.csv), [159 additional site-label candidates](results/additional_legacy_collection_candidates.csv), [three unverified grid candidates](results/weak_context_candidates.csv).
- [Six target pots with meanings and full recorded locations](results/food_sign_pottery_shortlist.csv), [nine original sign readings](results/frozen_food_targets.csv).
- `inputs/` preserves the attributed original Cambridge CSV, source-table extracts, 49 low-yield IDs, and the separate ten-row teaching-collection inventory. The raw research PDFs are not republished.

With Python 3.9+ and the existing translation catalogue/frozen key:

```sh
python research/independent_validation_20261120/residue_validation/run.py
python research/independent_validation_20261120/residue_validation/check.py
```

To recreate published table extracts, install PyMuPDF and download the files named in [SOURCES.md](SOURCES.md), then run `prepare_inputs.py --source-dir /path/to/downloads`. The ten thesis rows are an attributed manual transcription. Checks verify source-row retention, object/face counting, sign coverage and the absence of falsely accepted matches; they do not independently authenticate the catalogue or establish a reading.
