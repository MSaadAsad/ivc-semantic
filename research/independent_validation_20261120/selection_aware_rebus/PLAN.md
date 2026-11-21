# Selection-aware rebus search: fixed analysis plan

20 November 2026 local. Inputs and policies fixed before this new search is evaluated. This is a retrospective, bounded replay of documented lexical choices, not a reconstruction of every human decision or a preregistered decipherment.

## Prior-work check

Compared the local continuation at 673096505c1f06d11a33b7e0fbd63d81b7a2377b, upstream work at 727dfd411a4faa44d193d204757540d45c7b139b, and the upstream default tree at 648417d7607b6df507ade950b637b37e0441c31c. Upstream branch heads were checked on this turn.

Existing related work is credited, not called absent:

- work_scripts/key2a_rival_audit.py: fixed meaning pairs, single-headword and normalization audits, sound and domain controls. It does not reselect among alternative meaning specifications inside every dictionary null.
- work_scripts/key4b_bootstrap_wave2.py, key5a_big_six_strike.py and key6a_wave4_strike.py: candidate searches and fixed source-domain lists with shuffle tests; available selections/subsets are scored separately rather than replaying the complete recorded meaning-choice search in each shuffled dictionary.
- work_scripts/gsol_01_k1_audit.py: genuinely refits category/bilinear models for every semantic decoy assignment, but does not search alternative pictorial/rebus meanings in dictionaries.
- upstream main research/extensions_20261001/phonetic_null/REPORT.md and phonetic_null.py: equal-budget whole-inscription Sanskrit key optimization on real and synthetic sign corpora; a different question from picture-to-meaning rebuses.
- upstream main research/extensions_20261001/alternation_null/REPORT.md: explicitly selection-aware structural rewrite/family scans. The general principle of selection-aware testing is already implemented there.
- our expanded_rebus_test: six inventories and multiple scorers with fixed semantic specifications; no per-null lexical meaning-variant selection.

No implementation or results for the exact bounded seven-family lexical selection replay below were found in the inspected code. This is a repository-specific novelty statement, not a claim of worldwide methodological novelty or proof about unrecorded branches/history.

## Frozen search universe

Reuse all 178 recorded case rows across the six frozen panels in expanded_rebus_test/cases.json, including failed candidates. A row is one published combination of source-picture concepts and target concepts. Group rows by sign ID. Duplicate rows cannot earn multiple sign points. The primary target set is the previously frozen 48 distinct representative signs.

Permitted choices are a source-listed meaning-pair row and one of the existing phon_exact, phon_stem, or ascii_exact normalizers. Each row retains its full documented synonym lists. The dictionaries are the same seven pools, using the same form alternatives and gloss/sense cleaning as the preceding experiment. Do not mix parts from different source rows or invent new meanings after observing results. The main scorer uses distinct dictionary entries OR the existing distinct-sense same-entry polysemy rule; the disputed generated-cluster exclusion remains removed.

This is a finite representation of documented flexibility. It omits unrestricted synonym invention, arbitrary morphological changes, visual description generation, corpus/context selection, compounds, full chronology and unrecorded abandoned hypotheses. A surviving result is conditional on this universe and is not correction for the entire historical search.

## Policies and endpoints

For the real dictionary AND EACH randomized dictionary, evaluate:

1. Fixed48: original fixed pairs and exact normalization; reproduce 38 Dravidian and 11 Sumerian exact-plus-polysemy hits.
2. SoundChoice48: fixed meaning pair, choose the best of three normalizers separately for every sign.
3. MeaningChoice48: choose any recorded meaning-pair row for each of the 48 signs, exact normalization fixed.
4. MeaningAndSound48 (PRIMARY): choose any recorded row and any of the three normalizers for each primary sign. Score the number of successful signs out of 48; failed signs remain in the denominator.
5. GlobalSound48: choose meaning rows per sign but use only one globally chosen normalizer, optimized afresh in each draw.
6. CandidatePromotion48: allow promotion of 48 sign IDs from the full recorded candidate pool, with any recorded meaning row and normalizer. Its score is min(48, number of successful candidate sign IDs). Also report the uncapped successful-ID count to expose saturation. These candidate IDs can include related signs/allographs; they are not asserted independent readings. The same source dependencies are retained in real and null calculations.

Keep the real primary winner's row/normalizer for each sign and score that fixed recipe on the same null draws. Label this explicitly as a naive post-selection baseline. Its apparent p is not a valid selection-adjusted inference. Comparing it with full null reselection measures the price of the documented flexibility.

Publish the actual chosen row/normalizer for every sign and family. Resolve ties by source inventory order, then phon_exact, phon_stem, ascii_exact. Promotion ties use sign ID order. No hidden tuning, sampled optimizer convergence or changing search budget: exhaustively search the finite candidate universe.

## Randomization and multiplicity

Primary null: 9,999 whole-entry gloss/sound reassignments within the preceding form-length and form-count strata. Secondary null: 9,999 legacy cluster-preserving reassignments. Whole gloss/sense bundles stay together, preserving ordinary colexification/polysemy; these tests address phonological matching and the specified search, not whether a language's colexification patterns are historically appropriate. Polysemy therefore does not gain an artificial advantage from being destroyed only in controls.

Use distinct fixed family seeds and identical draws across policies within a family. Report complete score arrays, means, central 95% null ranges, exceedance counts and upper-tail Monte Carlo p=(1+exceedances)/10000. Holm-adjust seven primary family p-values. Report the legacy-null correction separately and a conservative larger-of-two-null sensitivity. Other policies are diagnostic; report a global Holm sensitivity across all seven families × seven genuine policy endpoints. The naive fixed-winner baseline is not included as a valid inferential endpoint.

Also report the fraction of fully reoptimized fake dictionaries reaching the *old* 38/48 threshold, carefully distinguishing it from a p-value for the newly optimized real score. For candidate promotion report success at the predeclared 48 cap and the uncapped yield; do not hide ceiling effects behind 100% retained accuracy. Do not identify the Indus language from raw cross-family counts.

## Verification and execution

Check the search optimizer against explicit candidate/normalizer loops, monotonicity of nested policies, unchanged fixed48 counts, row-duplication invariance and p-value recomputation. Preserve source and code hashes for rerunning. Benchmark runtime before the full run and respect the repository's approximately two-minute local computation rule. Update README/DIARY, publish a readable figure and complete report, then commit and push the authorized research branch.
