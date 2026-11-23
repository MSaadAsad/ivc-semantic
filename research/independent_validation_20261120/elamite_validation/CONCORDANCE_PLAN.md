# Direct Indus-sequence check: an Elamite-style concordance model

22 November 2026. The question is whether an Elamite-compatible grammatical mechanism predicts Indus writing, without comparing Elamite with Dravidian vocabulary. Source grammar and raw corpus sizes were inspected before fitting this model. This is a retrospective representation test, not a decipherment or independent semantic assignment.

## Linguistic prediction and its limits

Basello2023, *An Introduction to Elamite Language*, printed28/PDF22, describes nominal class suffixes and agreement across modified nouns and modifiers; examples include a repeated third-person suffix across a noun phrase. It also explicitly notes that the head may lack an overt suffix, especially with names and kinship terms, and that writing can use different spellings for a sound. [Primary chapter](https://unora.unior.it/bitstream/11574/217200/1/basello2023introduction-elamite.pdf). Stolper2004, *Elamite*, pp.73–74, independently describes this nominal agreement and supplies the person/gender/number suffix inventory. [Primary chapter](https://www.elamit.net/depot/resources/stolper2004original.pdf).

Test the **conditional writing model** in which agreement sometimes appears as the same independent Indus marker after two distinct stems: `A–s–B–s`. Extend to multigraph stems by allowing earlier marker positions. If that representation is useful, copying an earlier candidate suffix should improve predictions of later signs on inscriptions excluded from fitting. A second representation checks whether the same graphical four-corner cage is repeated on adjacent distinct graphic base families. This could express agreement within logograms.

These are two possible representations, not necessary properties of every possible Elamite inscription. Neither a win nor a loss identifies/excludes Elamite: other languages have agreement, and agreement could be omitted, fused or written with varying syllabic signs. No marker is assigned the sound r/p/k or an English noun merely because a pattern is found.

## Prior work

Existing `typo_02_grammar_fit.py` measures sign order and assumes roles for740 and title signs; `gsol_02_qap.py`/`gsol_03_eval.py` already fit competing language dictionaries with semantic/rebus/morphophonetic objectives. `key2c_elamite_bridge.py` already tests Linear-Elamite sign-shape/sound transfer. These are not repeated as new results. A targeted materialized-script/report search for copied suffixes and class-agreement markers found no implementation of the predictive copy mixture specified here. The claim of novelty is bounded to those inspected files.

## Data and prediction split

Use only raw sign sequences, object type, site and object-event keys from `work_data/sense/events_lipi.json` and `events_new.json`, plus purely graphical decompositions in `work_data/signlist/mark_families.csv`. No Dravidian roots, sign translations, English semantic categories or dictionary affinities enter either model.

For the linear model retain complete-looking numeric-ID sequences of length≥4 with no000/ALT/X tokens. This filter detects transcription damage, not actual physical completeness. Train on distinct Lipi formulas and test on distinct New formulas absent from Lipi. The input inspection found1,373 and183 such formulas respectively. Evaluate each position from the fourth sign onward; weight each full formula equally. Report all raw object/face counts and every prediction. Exact-form separation does not prove different physical objects or genuinely fresh archaeology. The corpora were used in earlier research; this is held out only with respect to this model fit.

Split Lipi formulas deterministically80/20 using a SHA256 hash before fitting the copying coefficient. Choose suffix candidates only from the inner training portion: nonnumeral signs occurring at least20 times there. Exclude IDs below060 as the repository's early numeric-sign block. Do not choose candidates from test successes. Copy candidates must have a preceding stem sign and at least one intervening sign before the target; the immediately preceding stem signs must differ, to reduce direct whole-word repetition.

## Linear models

Baseline: a smoothed sign predictor conditioned on inscription-length band, target position (interior/final), object type and the immediately preceding sign. Use fixed smoothing weights10 and10, with a global unigram prior including an unknown-sign bucket. No semantic roles are assumed.

Agreement representation: mix that predictor with a distribution over admissible earlier suffix candidates. A single coefficientλ is selected on inner-validation predictions, over0–0.95 in0.005 increments. If no candidate occurs, fall back to the baseline. Refit the baseline on all Lipi formulas, freezeλ and the inner-training candidate list, then score New formulas. The formula-equal primary score is mean gain in bits per predicted sign, averaged over full formulas; also report joint bits per formula. Report formula-level bootstrap intervals, the number of effective copy opportunities and actual successful repeats. Do not treat every token as an independent inscription.

Repeat the specified comparison in reversed sequence order as a diagnostic, not a second independent corpus. Also report the unchanged training/validation fit and whetherλ selected zero; no alternate direction or coefficient is promoted after seeing results. Sampling uncertainty is not a probability that the inscriptions are Elamite.

## Graphic representation

Use only mark-family descriptions explicitly saying four small vertical lines/strokes enclose a base. Do not merge different kinds of brackets, two-line cages, four-pair cages, hats or generic “other” marks into a single grammatical class. Publish the exact admitted rows. Compare adjacent signs with distinct root base families (trace the existing graphic decomposition graph; discard cycles/ambiguous roots). Use unique formulas, with train/test formula overlap removed, and record plain/plain, plain/caged, caged/plain and caged/caged counts. This is a descriptive check, not a claim that every sign is a word or every cage grammatical. Do not generate a significance claim from an empty or tiny marked subset.

## Verification

Check that a synthetic `A–s–B–s` grammar is recovered, that a sign-independent control does not yield useful held-out gains, and that no test formula/target affects candidates, smoothing orλ. Publish source hashes, split membership, predictions, candidates, source limitations and all admitted graphic rows. Keep local compute below two minutes and record actual runtime/Colab usage.

Post-fit diagnostic addition: the initial run selectedλ=0 in both directions. Release every specified grid coefficient's validation/test score to make that boundary solution inspectable. These curves are not used to select another coefficient from the test set. A zero interval for the selected model means the two predictors are identical, not a precisely estimated universal absence of agreement.

Post-fit sparse refinement: the broad copy pool may dilute a small set of true grammatical markers. Fit a greedy subset of at most six signs (the six distinct nonzero marker types in the cited nominal-class inventory) and the same coefficient using only inner Lipi validation. Refit the baseline on all Lipi formulas and freeze the selected subset/coefficient before scoring New. Preserve every selection step. This refinement was designed after viewing the first model's test outcomes, so it is exploratory, not a fresh preregistered confirmation. The New data do not enter its optimization, and any resulting marker IDs are not automatically Elamite phonetic values.
