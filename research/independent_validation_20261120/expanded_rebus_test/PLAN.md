# Expanded rebus comparison: analysis plan fixed before scoring

21 November 2026 UTC / 20 November local. Follow-up to the three-group positive-control pilot and twelve-pair filter diagnostic. The analyst has seen earlier repository results; this is a retrospective robustness analysis, not preregistration or independent semantic assignment.

## Inputs and scope

Use all 48 fixed two-sided claims from the prior 67-claim inventory; all 51 automatic Key2A pairs; all 30 Key4B, 13 Key5A and 24 Key6A candidate rows, including failed/not-promoted rows; and the unchanged original 12-pair panel as a reproduction check. These are six overlapping panels, not 178 independent observations. Freeze exact source regexes where available. Use literal, boundary-matched source concept lists otherwise. Freeze manually translated German concept lists for the German-glossed Elamite lexicon before scoring. Do not restrict competing dictionaries to Dravidian etymon IDs or tune regexes to observed witnesses.

Account for every row of the 163-sign master separately: the master includes numerals, literal readings, compounds and allographs; these are not 163 independent picture-to-meaning rebuses. Retain all source candidates regardless of outcomes or promotion. Do not add synonyms after looking at scores.

## Comparisons

Reuse the seven source dictionary pools and Key2A phonological/gloss normalization unchanged. Compare (1) original distinct-cluster filter and (2) distinct dictionary entries irrespective of generated cluster, each with/without the existing distinct-sense, same-entry polysemy criterion. Compare exact normalized phonology (primary), the existing stem normalizer and ASCII normalization (sensitivities). A uniform entry rule is a sensitivity, not a validated etymological repair. Do not call non-equivalent clusters linguistic evidence against a language.

Primary panel: 48 fixed claims. Primary scorer: exact normalized phonology, distinct entries OR documented distinct-sense polysemy. Primary competitors: all seven pools. Also report original strict exact scores to expose continuity with the pilot. Automatic 51-pair panel tests transfer to broader source domains; the three later candidate panels include search failures and illustrate selection sensitivity. Existing results on these panels are not new; the comparative filter sensitivities and recalculated nulls are new.

## Controls and inference

Run 9,999 shared target-domain permutations per panel, preserving dictionaries, source-side concepts and the target-side inventory. Use identical permutations across languages for paired language-advantage tests. Report null means, upper-tail Monte Carlo p=(1+exceedances)/(1+9999), and excess over null. Permutation diagonal may retain some correct pairings; these are random-assignment baselines, not independently false readings.

Run 9,999 sound/meaning reassignment controls with the legacy cluster-preserving permutation and 9,999 with entry-level form-complexity strata (shortest form length bins 2–3, 4–5, 6–7, 8+; one vs multiple forms). Keep whole gloss/sense bundles together. The latter avoids defining the randomization units through the disputed cluster IDs; it is not a model of historical language evolution. Polysemy remains invariant under sound reassignment and is tested by domain permutation. Report both sound nulls rather than selecting the more favorable one.

For the seven primary language tests, require both domain and entry-stratified sound significance: use the larger p-value, then Holm adjustment over seven languages. Also report a global Holm sensitivity across every panel/scorer/language combination for the two null requirements. For primary-scorer pairwise Dravidian advantages, test differences against shared domain permutations and Holm-adjust its six comparisons within each panel. A raw score tie is not statistical equivalence; failure to beat a rival is not proof of that rival.

Coverage: report both-domain representation, coverage-qualified scores and pairwise tests restricted to claims with both sides represented in both dictionaries. Report entire-dictionary eligible-edge counts. Reverse identical input records to measure order sensitivity. Verify both the original twelve-pair and automatic fifty-one-pair strict exact counts against committed tables, recording dictionary-build drift rather than hiding it.

## Meaning of a result

This tests robustness of lexical evidence conditional on supplied sign meanings. These meanings were selected during a Dravidian-oriented search; conditional randomization p-values do not remove that selection or establish an Indus reading. A strong conditional Dravidian result must be reported, as must collapse under controls. No result here substitutes for independent archaeological semantic assignment and fresh predictions.

## Execution

Benchmark the vectorized implementation before the full run. Local jobs must respect the repository's approximately two-minute computation limit; if the complete calculation is projected beyond that, use the authorized Colab workflow. Save every cell, null distribution, recovered witness and source hash; generate a figure; validate counts/nulls against brute force, update README/DIARY, and push the work branch.
