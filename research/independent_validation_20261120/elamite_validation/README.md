# Elamite–Indus: open rebus discovery and earlier checks

**New: [unrestricted Elamite rebus discovery](OPEN_REBUS.md)** extends beyond Cúper’s target meanings. It inventories 417 drawings and searches all available lexical targets, with anchors for 24/73 picture nouns. Two priority leads are **roof ku-uk → protection** (recorded polysemy) and **jar pi-ti → enemy piti-r** (same stem after a documented noun-class ending, not identical whole words). Both directions are absent from the inspected older Elamite candidate table. Six weaker directions, all 680 raw witnesses, source traps and dating limits remain visible. These are candidates to validate, not translated inscriptions or evidence identifying the Indus language. [Open the sign illustrations and audit](results/open_rebus.html).

The earlier experiments below answer narrower or different questions and are retained with their limitations.

[How close are the one-edit candidates, and do they beat other languages?](NEAR_MATCHES.md) The 496 witnesses reduce to 185 distinct written pairs; 111 are one conservative character apart, 66 are two and eight are three. The “one-edit” rule applies after permissive spelling simplification. The unrestricted search has not been run across the other languages under matched conditions, so it establishes no Elamite advantage.

**A direct sequence experiment has now been run:** the [Elamite-style written-agreement check](CONCORDANCE.md) fits1,373 distinct Lipi formulas and evaluates183 New formulas absent from Lipi, without any proposed words or meanings. Internal validation selects zero weight for repeating earlier candidate grammatical markers; the selected model adds no gain over its word-free baseline. The graphical-cage representation lacks marked test pairs. This checks two conditional written representations, not all possible Elamite grammar or a full reading model. [Open its results](results/concordance.html).

**The user's question is whether Elamite can explain the Indus inscriptions. The dictionary comparison below does not provide a full test of that hypothesis.** An Elamite reading must be allowed to use Elamite words and pronunciations; it need not resemble Cúper's proposed Dravidian sounds. Likewise, Cúper's individual semantic assignments are hypotheses, not independently known translations that every candidate language must reproduce.

The relevant completed component asks whether Elamite reproduces the particular picture-to-meaning rebuses proposed in the existing work. Only12/48 principal pairs have both meanings covered, and none provides the specified equal-form bridge. That is a restricted, low-coverage result about those rebuses, not an exclusion of Elamite as an Indus language. The additional 67-claim form-affinity comparison addresses a different question and is retained below as an **off-target analysis**, not evidence for or against Elamite–IVC.

**Correction:** the earlier headline foregrounding “no Elamite affinity” and the suggested next step of Elamite–Dravidian historical sound correspondences did not address the user's research objective. Such cross-family correspondences are not required to test Elamite as an Indus candidate. A direct test instead needs an explicit Indus-sign-to-Elamite model with stable values, Elamite linguistic predictions, and evaluation on inscriptions excluded from fitting, while controlling the flexibility of competing mappings.

[Open the illustrated results](results/elamite.html). [Primary summary](results/summary.json). [Design fixed before scoring](PLAN.md).

## What data were actually available?

The [DigitalPasts CSV release](https://github.com/DigitalPasts/ALP-MEGA2024/tree/3160b20f5cd84b387343d071749bb90419148743/Elamite_materials/EWB-EJSmithFiles), cited by the [DH2026 dictionary abstract](https://dh-daejeon.vercel.app/abs/358?full=1&q=XML), is real and downloadable. This check pins its October 2025 repository snapshot rather than assuming that every feature discussed in the 2026 abstract is already published there.

- Retrieved ten files with **10,438 rows**, including noun, verb, adjective, other/unclassified, divine-name and place-name categories. The separate personal-name file exceeds the connector's file limit and was deliberately excluded; proper names are not common-vocabulary evidence here.
- The five admitted common-vocabulary categories contain **8,184 rows**. There are **4,190 noun rows and 1,700 verb rows**, not that many independently reconstructed roots.
- Readable-form/head filtering leaves **4,158 source rows**. Removing nonempty source `cognate` flags leaves **3,649 rows**, collapsing to **3,536 distinct normalized form/head pairs** and **1,248 distinct lexical-head sets**. Neither count is a count of independent roots.
- The release's English lexical hints occur mainly in **`morphology`**. The `semantics` column is largely blank for nouns/verbs and often contains categories such as a month-name classification. We do not mistake a named month for the ordinary word “month.”

All retrieved bytes match the repository's Git blob identifiers. Raw files stay outside this repository; the pinned downloader reproduces them. Full exclusions and counts are released in [source_inventory.csv](results/source_inventory.csv) and [entry_eligibility.csv](results/entry_eligibility.csv).

## Two different questions

**Does Elamite reproduce the proposed picture-to-meaning wordplay?** All 178 previously frozen formulations across six overlapping panels were screened. In the principal 48-pair panel, only **12 have both meanings covered** under the specified whole-head rule, and **none supplies the required equal-form pair**. The reassigned-target baseline also produces zero hits; the sound-reassignment baseline produces almost none. This is a low-information negative result, not a decisive rejection of Elamite wordplay. The other 36 pairs are not scored as linguistic failures.

**Off-target comparison: do the proposed Dravidian forms resemble Elamite words for the same meanings?** Of 67 frozen claims (48 paired, nine literal, ten numeral), **34 have a covered target meaning**. None has an exact normalized form match. Their edit similarities are unexceptional against 9,999 reassignments of those target meanings; numeral targets are kept in their own permutation group. For example, the release records **a-a-in “house”**, **da-la “tax”** and **su-un-ki-ir “king-SG”**, whereas the corresponding proposed forms include **kuṭi/kuṭam**, **vari** and **kō**. An Elamite hypothesis does not require these two languages' forms to resemble each other. These statistics therefore do not answer which language the Indus inscriptions encode. All candidates remain in the downloadable rows so the work can be inspected rather than silently removed.

Similarity counts character insertions/deletions/replacements after declared transliteration normalization, takes the closest admissible same-meaning entry, and averages over covered claims. It is **not** a percentage of correctly translated words, a sound law or a probability of common ancestry. The source distinguishes consonant diacritics in the primary calculation; an ASCII-folded sensitivity also fails to show exceptional affinity.

## Earlier evidence and borrowing flags

| Pool | Distinct form/head pairs | Covered direct claims | Exact hits | Similarity permutation p, unadjusted |
|---|---:|---:|---:|---:|
| All eligible periods, excluding source cognate flags |3,536|34/67|0|0.3647|
| Non-Achaemenid-attested, unflagged |2,175|33/67|0|0.2914|
| Old-Elamite-labelled, unflagged |312|20/67|0|0.5204|

“Old Elamite” is broader than the mature Indus period. These labels do not establish a third-millennium date for each word. A nonempty `cognate` column is a source warning, not a complete loanword classification; unflagged entries are not certified native vocabulary. Reconstructed pronunciations and systematic historical sound correspondences were not supplied by this CSV release.

## Unrelated-language controls

Existing Sumerian and Akkadian Wiktionary-derived pools were also screened descriptively with the same fixed claims and whole-head criterion. On the **24 claims covered by all three**, raw mean similarities are **Elamite 0.214, Sumerian 0.108, Akkadian 0.143**; exact hits are zero in every pool. The dictionaries differ markedly in size (3,536 versus 974 and 720 form/head pairs), provenance and coverage. A larger pool gives more opportunities for a close spelling. Elamite's raw advantage over those lists does not overcome its own within-dictionary chance baseline. No language-ranking probability or family identification is inferred. [Full controls](results/rival_dictionary_summary.csv).

## What is additional to the repo?

Cúper already included Elamite in `key2a_rebus_lock.py` and later seven-family dictionary comparisons. `key2c_elamite_bridge.py` also tests proposed Linear-Elamite sound transfer on Iranian finds. Our earlier expanded rebus experiment already reports an Elamite result using the old Hinz–Koch-derived pool. Those are not new tests here.

This extension imports the structured DigitalPasts release, checks its actual usable coverage, runs fixed-form/same-meaning affinity controls, separates source period/borrowing flags and publishes every old pair formulation's result with that input. A targeted materialized-script/report search found no existing DigitalPasts/EJSmith implementation. The new release itself draws on Hinz–Koch, so it is not an independent set of lexical attestations or a newly discovered ancient corpus.

The 163 current signs are retained in a [scope inventory](results/all_163_sign_scope.csv). Only the 67 frozen direct claims and signs with existing pair recipes are tested; allographs, compounds and other signs are not silently converted into additional independent words. Nothing here reassigns an Indus sign's meaning. [McAlpin's 1974 Elamo-Dravidian proposal](https://www.cambridge.org/core/journals/language/article/abs/toward-protoelamodravidian/2687ABD92C4524F4553D244C8AC57DBF) predates this project; a source-verified historical correspondence test remains separate from this spelling screen.

## Reproduce

From the repository, with Python and NumPy:

```sh
python3 research/independent_validation_20261120/elamite_validation/fetch_inputs.py --destination /tmp/ivc-elamite-inputs
python3 research/independent_validation_20261120/elamite_validation/run.py --source-dir /tmp/ivc-elamite-inputs
python3 research/independent_validation_20261120/elamite_validation/check.py
python3 research/independent_validation_20261120/elamite_validation/rival_controls.py
python3 research/independent_validation_20261120/elamite_validation/report.py
```

The optional scientific figure in `report.py` needs Matplotlib. Reproduction uses the repository's frozen claims and earlier lexical pools; the standalone export is a viewing/data bundle. Source-word/period annotations preserve the raw row IDs when equivalent spellings are grouped. Synthetic recovery, semantic false-positive exclusions, missingness and entry-order checks passed. Actual run time and zero Colab usage are recorded in [summary.json](results/summary.json).

The main run completed in39.05 seconds locally. All1,424 pair rows,536 direct rows,48 rebus sensitivity cells,163 scope rows and9,999 primary control draws were checked against the specified inventory. Browser verification loaded the scientific figure and all four tables (4/67/48/3 rows), resolved every local report link and found no script errors or page overflow at desktop/mobile sizes. The figure and desktop report were visually inspected.
