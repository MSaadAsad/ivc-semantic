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

The inscription set excludes 469 dedicated upstream showcase sequences, uses 60 unique sequences on 60 distinct catalogue objects across eight sites, and includes both transcriptions. It is additional to showcases, **not untouched by the project's research**. All 60 translations remain unvalidated. The 45 evidence cards and 120 blinded reading tasks are prepared but have no human ratings; fourteen identical constrained-decoy controls must not be treated as evidence of semantic identification.

## Reproduce

Python 3.9+; the actual new calculations were run with Python 3.9.6, NumPy 1.26.4, SciPy 1.13.1 and scikit-learn 1.5.2. No upstream analysis modules, external services or shared lexical cache are used. Code resolves paths from this directory; run from any working directory.

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
