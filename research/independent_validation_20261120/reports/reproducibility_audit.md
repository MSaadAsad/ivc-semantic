# Reproducibility audit and reconciliation

## Starting point

The November 19 prior audit examined `8259c47fdf4a076f04029254f97c83f04abb139e` through Key #4. Its report, scripts and actual outputs are preserved unchanged under `../prior_audit`. They are historical evidence, **not newly rerun results**. This continuation starts at current work-branch commit **`727dfd411a4faa44d193d204757540d45c7b139b`**, which adds Keys #5 and #6. It freezes the latest 163-sign proposal rather than stopping at the prompt's earlier 114-sign headline.

## Checks actually run

| Check | Result and scope |
|---|---|
| Latest 163-sign coverage from original reader rows | Reproduces every relevant stored filtered Key6A total. Also computes full-denominator figures retaining unresolved identifiers. |
| Real object and sign joins | 45 reviewed signs, 60 unique real sequences on 60 distinct catalogue objects; every ID/sequence is checked against the committed reader table. Exact proposed roots are unchanged. |
| Nonphonetic archaeological contrasts | All 540 sign–artifact cells independently calculated; odds ratios, descriptive intervals, Fisher p-values and full-family BH correction exported. |
| Site controls and multiplicity | 5,000 common site permutations per corpus; max-T across every sign/type contrast and correction over both corpora. 22/540 pass under the stated permutation model. |
| Artifact prediction | Six frozen-C feature sets, formula-grouped cross-validation, transfer to Mahadevan, 199 matched rivals, and conditional cluster-bootstrap intervals. |
| Latest semantic-taxonomy sensitivity | Explicit extension for all 23 later signs, three regularization settings, another 199 matched rivals, and nested training-only parameter selection. Positive and negative results retained. |
| Unique-label equivalence control | Fresh column-permuted identity fit has identical accuracy and effectively identical log loss. |
| Older decoys | Joined all four tester files to their key; retained both replay testers and kept each item intact across testers in stratified permutations. |
| Published three-wave combination | Fisher arithmetic reproduced from stored p-values; assumptions and adaptive sign overlaps examined. Underlying lexical shuffles were not rerun. |
| External source spot-check | ICIT authors' M-1088 example agrees with Lipi 3462.1 after display/reading reversal; seal type agrees. No assertion of independent findspot authentication. [Primary documentation](https://epigraphica.de/indus/menueindus.htm). |
| Internal consistency | Frozen source hashes, 163 unchanged roots, 60 exact sequences/objects, 45 signs, 540 contrasts, BH arithmetic, protected whole-formula folds and unresolved-token regression cases all pass. |

## Current coverage discrepancy

These figures count **assigned values**, not correct translations or established phonetic values.

| Corpus | Filtered upstream score | Every nonempty sign retained |
|---|---|---|
| Unpartnered intact Mahadevan | 1,761 / 1,994 tokens = **88.31%** | 1,761 / 2,161 = **81.49%** |
| Completely assigned Mahadevan faces | **380 / 563 = 67.50%** | **325 / 627 = 51.83%** |
| Combined intact tokens | 13,062 / 15,203 = **85.92%** | 13,062 / 15,370 = **84.98%** |
| Completely assigned combined faces | **2,546 / 4,163 = 61.16%** | **2,491 / 4,227 = 58.93%** |
| All faces, including damaged | 18,265 / 23,710 tokens = **77.04%** | 18,265 / 24,040 = **75.98%** |

The same identifier-format filter exposed by the earlier audit remains in `key6a_wave4_strike.py:extract_tokens`. Unmapped `X…` signs disappear, 64 intact faces disappear entirely, and **55 additional mixed intact faces are falsely counted as fully assigned**. Their exact IDs/sequences are released. This updates the earlier audit's 40-face figure at the smaller 114-sign vocabulary.

Key6C's parity discussion describes the shortened corpus as 'cleanly crosswalked' and treats retained unknowns as an undesirable denominator effect. However, numeric filtering does not merely select complete crosswalked rows: it also removes unknown signs from mixed rows. Its 'all clean tiers pass' invariant therefore cannot validate transfer coverage. Key6B does separately flag 50 affected fully assigned faces at its intermediate 140-sign stage; that partial acknowledgment does not fix the later 163-sign scorer.

## Why the newer wins do not settle the older failures

The original decoy result is reproduced: **9/58 versus 10/60**. Both method-replay files together give **28/57 versus 36/58**. The old constrained compound output remains negative: **11 observed versus 12.678 shuffled**, reported p≈0.770. These tests concern earlier mappings and cannot falsify every new sign. Conversely, new whole-lexicon coverage, sign-order consistency, city specialization or dictionary matches do not repair those tests unless they defeat the same hard semantic rivals.

The new expanded-taxonomy rival result is a real **conditional positive** for broad grouping (p=0.005, 199-rival floor). It is more relevant than another dictionary match, but the corpus was exposed, the grouping specification is exploratory, structural/identity baselines perform better, and no individual meaning is identified. It narrows the claim to useful grouping relative to this null rather than a decoded vocabulary.

Key6B's seal-area hierarchy shows that selected sign sets correlate with size conditional on its controls. The 'elite' set explicitly includes the fish family; the labels are assigned to those sets. That is not independent proof that fish signs denote stars or that selected signs encode a particular social rank. The area statistic was not independently rerun in this continuation.

Likewise, nonsignificant time trends are not equivalence tests proving a stable spoken key across 600 years. Some chronology uses depth bands rather than absolute object dates. Time stability of sign use can coexist with many different meanings and pronunciations. These are code/interpretation checks, not newly estimated chronological effects.

## Lexical and family comparison limits

The current seven-family figures remain **conditional reported results**. We independently check combination arithmetic, stored per-sign promotion statistics and exact sign-set overlaps. We do not authenticate every dictionary gloss, reconstruct Bronze Age phonology or repeat all synonym/domain decisions in null runs.

Of the 18 Wave-2 promoted signs, the stored stem probabilities have **one below 0.05 and none below 0.05/30**. Aggregate lexical evidence cannot be distributed to certify every sign. Wave 4 reuses five previously tested targets even though they were not previously accepted as locked; the full list is in `reported_claims_arithmetic.json`.

Unequal dictionary concept coverage, different gloss languages, synonym opportunities, reconstructed versus daughter-language forms, borrowing and chronology remain unresolved by equal shuffle counts. No honest language-family posterior follows from these p-values. A seven-family reference set also omits unknown/extinct languages and possible multilingual usage.

The strongest required language test is still prospective: semantic constraints fixed without candidate-language knowledge, followed by the same full search procedure for every family and for decoys. This continuation deliberately prioritizes that missing condition over searching for more Dravidian matches.

## What was not independently reproduced or authenticated

- All historical scripts and 5,000-shuffle dictionary campaigns.
- Raw extraction from every excavation catalogue, original sign photograph, dictionary scan, or crosswalk entry.
- Every known object/copy/mould/context grouping in the committed metadata.
- The Key6B area and chronological headline calculations as fresh end-to-end runs.
- A new seven-family comparison with externally constrained semantic labels.
- Human grammatical/semantic judgments or a genuinely unexposed corpus.

No numerical outcome is invented for these gaps. The unscored expert materials and prospective protocol identify the missing evidence. Reproduction of derived files cannot substitute for it.

## Portability

The new code is self-contained within the continuation and resolves paths from its own location. It imports no upstream analysis module and uses no shared `/tmp/typo_lex` cache. Scientific dependencies are pinned. `maxT.py`, `nested_prediction.py` and other new modules import only the continuation's own helper module.

Original scripts include hardcoded `/home/antigravity/Cuuper22/ivc` paths, including Key6B. Their existence or successful syntax compilation does not demonstrate that a clean checkout can regenerate their data. The new reproduction instructions distinguish running this continuation from rerunning the historical project.
