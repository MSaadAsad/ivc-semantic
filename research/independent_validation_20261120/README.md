# Independent semantic validation — 20 November 2026

This continuation starts from work-branch commit **`727dfd411a4faa44d193d204757540d45c7b139b`**, after Key #6, and preserves the earlier Key #4 audit separately. The latest **163-sign proposal is frozen without changing a root**.

**Verdict:** the project has real structural and archaeological patterns, but its exact meanings and sounds remain unestablished. The expanded semantic grouping beats its constrained rivals (exploratory p=0.005), yet predicts artifact type worse than sign identities or positional roles and adds no clear predictive gain beyond identities. There is no genuinely independent semantic holdout in the evaluated evidence.

## Deliverables

1. [Executive verdict and all nine assessment questions](reports/assessment.md).
2. [Literature and novelty review through 20 November 2026](reports/literature_review.md).
3. [Reproducibility audit and reconciliation of positive/negative findings](reports/reproducibility_audit.md).
4. [45-sign evidence table](reports/sign_evidence.md), with [machine-readable evidence and alternatives](results/sign_evidence_45.csv).
5. [60 additional real inscriptions](reports/inscription_tests.md), with [exact IDs, contexts, unchanged readings, predictions and controls](results/inscription_tests_60.csv).
6. [Statistical report](reports/statistical_report.md), including [nested predictive results](results/nested_prediction.json), [matched-rival sensitivity](results/semantic_sensitivity.json), [all 540 contrasts](results/all_sign_artifact_contrasts.csv), [site-corrected max-T results](results/site_maxT_all540.csv) and compressed null distributions.
7. [Frozen 163-sign proposal](frozen/proposals.json), [design and input hashes](frozen/design.json), [code](code), complete derived results and unscored blinded materials.
8. [Three-experiment roadmap and prospective independent-semantic protocol](reports/prospective_protocol.md).
9. [Which Dravidian language?](language_affinity/README.md): a 21-language dictionary comparison, 35 fixed claimed etymon-pair checks, explicit Tamil source preference, and Brahui coverage limits. This retrospective extension does not identify the ancient language.
10. [Meaning-matched northern/southern overlap](language_overlap/README.md): additional DravLex source, fixed-sense cognate comparison (11 scorable concepts), 73 fixed dictionary entries and two documentation controls. Brahui, Kurukh and Malto each match 5/11; Tamil 10/11 and Malayalam 8/11. All northern overlaps, missing data, loan flags and unresolved contrasts are released.
11. [Full dictionary overlap and synonyms](full_dictionary_overlap/README.md): all 5,558 recoverable groups, 274 containing Brahui, 21 languages, exact documentation-breadth adjustment, full Brahui catalogue and lexical case review. Recovers synonyms such as *xaning* “see,” distinguishes changed senses and alternative roots, and corrects earlier extraction coverage.
12. [IVC-specific large-vocabulary portability](ivc_language_test/README.md): 67 representative sign claims, 48 fixed meaning pairs, 22 varieties, full northern glossary searches and a separate full Kurukh dictionary screen. Includes 1,474 claim/language cells, witnesses, 107-etymon northern controls and loan/source corrections. [Corrected graphics and historical grouping](ivc_language_test/diagram_correction.md) replace the old Kannada/Telugu Venn set; both graphics now spell out English meanings and the full atlas displays all 22 varieties. The source lexical matrix is unchanged. [Plain-English semantic catalogue](ivc_language_test/semantics.md).
13. [Known-rebus positive control and comparative-filter diagnostics](rebus_positive_control/README.md): three independent Sumerian sign groups, separate answer key, seven-family engine, exact six-permutation controls, reading witnesses and post-pilot sensitivities. Sumerian ranks first in original order; the strict channel blocks two known cases and its sole positive disappears when identical records are reversed. Zero eligible exact-phonetic edges for Akkadian/Burushaski expose a concrete limitation in rival-language exclusion.
14. [Expanded six-panel comparative filter test](expanded_rebus_test/README.md): 48 fixed reading pairs, 51 automatic pairs, all 30/13/24 later candidates and the original 12; seven pools, 504 cells, 9,999 controls for each of three null schemes, shared-permutation rival tests, coverage and order sensitivities. Uniform exact-plus-polysemy counts favor Dravidian 38–11 on selected readings (primary Holm p=0.0007), but give 13–14 on the automatic panel with neither exceeding both nulls. The twelve-pair tie does not generalize to the selected 48. All witnesses, null arrays, original-root provenance and the 163-row master scope are retained.
15. [Selection-aware rebus search](selection_aware_rebus/README.md): source-variant and normalizer choice reoptimized in each of 9,999 randomized dictionaries under two null schemes, seven pools, all 178 source rows and 93 candidate IDs. Optimized Dravidian reaches 48/48 versus no fake at 48 (primary Holm p=0.0007); 75.6% of fakes nevertheless reach the old 38 count. Choosing which 48 successes to retain yields 48/48 for every sampled fake; uncapped real yield 78/93 exceeds the null mean 64.98 (p=0.0004). Existing selection-aware Sanskrit/structural tests are credited; this bounded lexical replay is new to the inspected implementation. Every chosen recipe, word witness, failure and null score is retained.

The inscription set excludes 469 dedicated upstream showcase sequences, uses 60 unique sequences on 60 distinct catalogue objects across eight sites, and includes both transcriptions. It is additional to showcases, **not untouched by the project's research**. All 60 translations remain unvalidated. The 45 evidence cards and 120 blinded reading tasks are prepared but have no human ratings; fourteen identical constrained-decoy controls must not be treated as evidence of semantic identification.

## Reproduce

Python 3.9+; the initial semantic calculations were run with Python 3.9.6, NumPy 1.26.4, SciPy 1.13.1 and scikit-learn 1.5.2. Those initial calculations use no upstream analysis modules, external services or shared lexical cache. Later substudies document their own dependencies and source reuse; the rebus tests deliberately reuse upstream normalizers and candidate dictionaries in an isolated cache. Core code resolves paths from this directory; follow each substudy's reproduction instructions.

```sh
python3 -m venv /path/to/task-venv
/path/to/task-venv/bin/python -m pip install -r /path/to/ivc/research/independent_validation_20261120/requirements.txt
/path/to/task-venv/bin/python /path/to/ivc/research/independent_validation_20261120/code/run.py
```

The frozen source hashes must match. Do not regenerate the freeze to bypass an input mismatch. `freeze.py` records how the original inventory was extracted; it is not part of the default rerun. All new outputs remain inside this continuation directory. The Markdown analysis reports are authored interpretations of the released outputs, rather than a claim that a script proved a decipherment.

A minimal sparse checkout needs `work_scripts`, `work_data/reader_v3`, `work_data/sem`, `work_data/key6a`, `work_data/key6c`, `work_data/key4b`, `work_data/decoy`, `work_data/fv3`, and this continuation directory, plus the top-level files automatically retained by cone-mode sparse checkout. No archaeological scan archive or raw multilingual dictionary is needed for these new checks. Full historical dictionary campaigns and the prior audit have separate input requirements.

## Scope

The models use 4,476 Lipi and 990 Mahadevan deduplicated events. Whole-object exact formulas stay together across predictive folds. Some excavation, workshop, partial-formula and unidentified copy dependencies remain; the results are retrospective. Source sequences are checked against committed corpus rows, with a limited external documentation spot-check, rather than claiming authentication of every original object.

The prior audit is in [prior_audit](prior_audit/README.md). Its outputs are preserved historical runs against `8259c47`; they are not presented as newly rerun calculations. The source project and corpus authors retain credit for their data and hypotheses. New analysis and code were prepared by Codex at the user's request; no independent human archaeological or linguistic review has been represented as completed.
