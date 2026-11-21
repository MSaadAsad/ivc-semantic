# Statistical report

All new results refer to frozen source commit `727dfd411a4faa44d193d204757540d45c7b139b`. The continuation does **not** rerun or certify every historical dictionary shuffle. It tests the semantic/predictive gap directly. Exact outputs and seeds are under `../results` and `../frozen`.

## Data and sampling units

The reader table has 9,252 rows. Excluding Mahadevan rows marked as partnered leaves 6,862 faces, including damaged faces. The intact set has 3,600 Lipi and 627 unpartnered Mahadevan faces. No nonempty identifier is silently discarded.

Archaeological models use the committed physical-object/copy-event tables: **4,476 Lipi events** and **990 unpartnered Mahadevan events** marked `is_event_rep=True`. This preserves upstream known-batch deduplication; it is not independent authentication of every batch decision. The Lipi event types include 2,227 seals, 1,138 miniature tablets, 569 pots, 207 tags, 151 copper tablets, 40 rods and other objects. Multiple faces remain attached to one object. Unknown signs remain predictors or uncovered tokens.

All predictive cross-validation keeps identical **whole-object full-text strings** in one fold. This prevents direct whole-formula train/test duplication. It does not group every partially overlapping formula, workshop, excavation context or unrecognized copy. The sign classifications and proposed semantic groups were developed using these corpora, so the exercise is retrospective even though the classifier's outer evaluation folds are protected.

## Artifact prediction: proposal versus language-free baselines

Outcome: seven artifact classes, with bangle/tool/other pooled as `other`. Every model has site, log inscription length and number of faces. Structure uses the frozen FRAME v3 classes crossed with initial/middle/final/solo position. Identity uses exact sign counts. Semantics uses proposed broad semantic-domain counts. No phonetic dictionary matching enters the classifier.

Models are multinomial logistic regressions. The initial comparison freezes `C=1`; no model's hyperparameter is selected from its test results. A subsequent nested sensitivity chooses `C` from 0.1, 1 and 10 using three inner formula-grouped folds inside each of five outer folds.

| Features in addition to context | Initial grouped-CV log loss, nats | Accuracy |
|---|---:|---:|
| None | 0.840985 | 70.40% |
| Positional/structural roles | 0.767464 | 73.28% |
| Original Key6B semantic taxonomy | 0.798870 | 72.07% |
| Sign identities | **0.748642** | 75.29% |
| Identities + structural roles | 0.753047 | 75.29% |
| Identities + original semantic taxonomy | 0.752067 | 75.38% |

The original Key6B taxonomy classifies 140 signs; the 23 later additions are retained as an explicit unclassified group. Because that could disadvantage the latest proposal, an **exploratory second specification** assigns those 23 signs to broad domains using their already proposed meanings, without inspecting any additional artifact outcomes. These assignments and rationale are frozen separately, not passed off as the original taxonomy or a preregistration.

| Features, complete 163-sign semantic specification | Nested grouped-CV log loss | Accuracy |
|---|---:|---:|
| Context | 0.840985 | 70.40% |
| Roles | 0.767464 | 73.28% |
| Semantics | 0.798514 | 72.01% |
| Identities | **0.748642** | 75.29% |
| Identities + semantics | 0.752436 | 75.49% |

For these data, inner-fold selection chose `C=1` for every model and outer fold. Thus the original conclusion does not depend on fixing this parameter arbitrarily. The full sensitivity table is retained: at `C=0.1`, adding semantic features gives a modest log-loss improvement, while at `C=10` the identity model overfits and compressed semantics performs better. These results must not be suppressed. They demonstrate that semantic grouping can function as regularization; they do not independently identify the meanings.

Two thousand bootstraps resample complete formula groups, conditional on the fitted outer-CV predictions. For the nested comparison:

- Semantics minus identity log loss: **+0.049872 nats**, conditional 95% interval **[+0.023731, +0.074613]**. Positive is worse for semantics.
- Identities-plus-semantics minus identity: **+0.003794**, interval **[−0.000750, +0.008054]**. No clear incremental improvement.
- Semantics minus structural roles: **+0.031050**, interval **[+0.014839, +0.047990]**.

These are estimation intervals for specified models on reused evidence, not posterior probabilities for a decipherment. Shared excavation contexts and the original mapping search are not included in the uncertainty. The three comparisons are reported together; no confirmatory hypothesis-test claim is attached to selecting a favorable interval.

## Matched rival vocabularies: one null and one positive finding

The 199 rival mappings permute complete frozen lexical entries within cells matching structural class, log2 frequency octave, slash-alternative count and hyphen complexity. Sign sequences and frequencies stay fixed; the inventory of meanings and semantic-category counts is preserved. Frequency matching is a band constraint, not exact equality of weighted category token mass. Dictionary search is absent for every mapping, so flexibility is equally zero in this predictive application. These are constrained randomized alternatives, not authenticated rival-language lexicons.

Thirty-seven cells permit swaps; **101/163 signs are movable**. On average, 64.04 sign-to-entry assignments change, and 39.12 signs change broad domain in the original-taxonomy comparison. Many values remain fixed or move within one domain. This restricted null has limited power and is not a test of every plausible vocabulary.

| Semantic specification | Observed log loss | Rival mean | Rival central 95% range | One-sided empirical p |
|---|---:|---:|---:|---:|
| Original taxonomy | 0.798870 | 0.803227 | 0.796770–0.810536 | **0.105** |
| Expanded 163-sign taxonomy, exploratory | 0.798514 | 0.806752 | 0.800254–0.812173 | **0.005** |

The expanded taxonomy beats every one of its 199 rivals: **0.005 is the plus-one Monte Carlo floor**, not a precise arbitrarily small p-value. The null central range is not a confidence interval for a causal effect. The observed improvement over the expanded rival mean is **0.008237 nats**. This positive finding belongs beside the negative one. If the two taxonomy specifications alone were the declared family, Bonferroni would give 0.010; that narrow adjustment does not account for all post-development semantic decisions.

Interpretation: the later semantic grouping contains useful constraints relative to these locally shuffled groupings. It still performs worse than sign identity and roles, supplies no clear incremental gain over identity, and was derived on exposed evidence. It therefore does not establish 'tax', 'king', 'house', a Dravidian word, or any individual sound. Nor does the initial null prove those interpretations false.

## Cross-corpus application

Training on Lipi and applying to all 990 Mahadevan events gives log loss 1.388739 for context, 1.377579 for roles, **1.311179 for identity**, and 1.425246 for the original semantic taxonomy. Among the **807 full-text strings absent from the Lipi training objects**, the corresponding values are 1.432122, 1.417766, **1.349724**, and 1.476598. The original identity-plus-semantics model gives 1.362832 on this novel-full-text subset.

This is a useful transcription/domain-transfer stress test, not an untouched semantic holdout. Projected crosswalks, differing object mixes, damage, and repeated historical exposure remain. The expanded-taxonomy/nested sensitivity was run on Lipi, so no expanded-taxonomy Mahadevan score is implied by this table.

## Information-equivalence control

Any unique label assigned to each sign is an invertible recoding. In information terms, a deterministic mapping adds no information conditional on the exact signs. For a regularized fitted model, grouping can still help as a prior or compression choice.

A fresh identity-model fit after a bijective feature-column permutation reproduces accuracy exactly. Log loss differs by about **6.6 × 10⁻⁹ nats**; the maximum probability difference is **1.2 × 10⁻⁵**, consistent with optimization tolerance. This is not a claim that an implausible vocabulary defeats every language test. It demonstrates why a sign–artifact association cannot be credited to its word label unless a discriminating external constraint is tested.

## Archaeological associations, effects and corrected tests

All **45 signs × six target object types × two corpora = 540 contrasts** are released, including failures. Pooled Fisher enrichment tests have Benjamini–Hochberg adjustment over that full family. Haldane–Anscombe odds ratios and approximate log-OR intervals describe each contingency table; they do not model excavation clustering.

A stronger sensitivity uses 5,000 common within-site label permutations per corpus. Expected intersections and hypergeometric variances are calculated from fixed site margins. For each shuffle, the maximum standardized excess across **all 270 contrasts** is retained. Each cell's max-T p-value is then Bonferroni-adjusted for the two corpora. Under this exchangeability model, **22/540** pass familywise 0.05: 19 Lipi contrasts and three Mahadevan contrasts. The corrected p-value floor is approximately 0.000400. These are not Gaussian 'sigma' extrapolations.

Examples include Lipi cup-like 700 on miniature tablets, comb-like 400 on miniature tablets and rods, and 615/407/845 on copper tablets. Copper-tablet association for 615 and 142 also survives in Mahadevan. Sign 595 survives there but not in the same corrected Lipi contrast. This supports heterogeneous artifact-related functions; it does not choose between tax, commodity, institutional, ritual or series labels.

The original selected-target site-permutation table is also retained. Its naive Bonferroni-540 p-values cannot cross 0.05 at 5,000 draws because of Monte Carlo resolution. The all-contrast max-T analysis addresses that limitation without choosing only favorable cells. Neither approach removes dependencies from unidentified text/copy families or excavation selection; those remain limits, not hidden claims of independence.

## Existing decoys and reported lexical statistics

Joining the preserved tester files to their blinded key reproduces **9/58 real versus 10/60 decoy** successes. Pooling both later replay testers gives **28/57 versus 36/58**, rather than reporting only the first replay. Permuting real/decoy item labels within original job/frequency cells while keeping both testers' observations together gives one-sided real-better p-values **0.4163** and **0.9208**, respectively. These are reanalyses of old observations, not new blinded experiments.

The reported 44-sign Fisher arithmetic is reproduced: input p-values 0.0004, 0.0002 and 0.001 yield **χ²₆ = 46.49799**, independence-reference p **2.35605 × 10⁻⁸**. The arithmetic is correct. Disjoint sign IDs do not demonstrate independence of shared dictionary-derived statistics. Neither the full lexical-selection process nor a synchronized dictionary null was rerun in this continuation. This number is therefore not promoted into independently calibrated evidence for a language.

Code inspection also finds that Wave 4 overlaps earlier **tested** lists on `142, 527, 585, 595, 692`. Excluding previously *locked* values is different from excluding previously *tested* hypotheses. 'Fourth independent, zero-overlap wave' needs that distinction. Changing failed domains and repeating a sign is adaptive exploration, not an independent confirmation.
