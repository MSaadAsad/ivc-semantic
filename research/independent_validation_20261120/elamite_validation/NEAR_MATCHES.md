# How close are the near spellings, and do they beat other languages?

23 November 2026. **Small character distances do not automatically make good rebuses. No matched unrestricted-language comparison has established an Elamite advantage.**

The 496 one-edit witness rows reduce to **185 distinct written word pairs**. Each differs by one insertion, deletion or substitution only **after** folding vowel length/repetition, b/p, d/t, g/k and repeated consonants. Keeping consonant distinctions and doubling gives:

| Conservative normalized edit distance | Distinct written pairs | Witness rows |
|---|---:|---:|
| One character |111|286|
| Two characters |66|201|
| Three characters |8|9|

Thus 74/185 distinct pairs (40.0%) require more than one character change under the conservative rule. The 185 pairs are not independent roots, semantic directions or validated rebuses. Neither key measures a reconstructed phonemic distance. The conservative rule still joins syllabic spelling and folds vowel length/repetition.

Most witness strings are short: in 461/496 rows the longer permissive key is four or five characters. One substitution in a four-character form affects a quarter of its letters. That fraction is not a linguistic probability or a phonetic similarity score.

Examples from the actual candidates:

- **hal-ti “door” / hal-mi “sealed document”:** one t/m substitution. Closeness alone does not establish the same pronunciation or a regular relation.
- **si-ir-ri “bowl?” / si-it-ti “sit”:** conservative keys sirri / sitti require two substitutions; permissive keys siri / siti require one. The bowl gloss is also uncertain.
- **qa-bar “box” / qa-ap-pa-ak “include”:** conservative keys qabar / qappak require three edits; permissive qapar / qapak require one. The “one-edit” label hides multiple prior simplifications.

By contrast, the two priority directions are not members of this one-edit group: **roof / protection uses the same recorded form**, and **jug / enemy uses a separately labelled noun-class-stem match**. Staff / affection matches only with doubled-consonant folding. None is established as an Indus value.

[Basello2023, pp.19 and27–28](https://unora.unior.it/bitstream/11574/217200/1/basello2023introduction-elamite.pdf) explains why Elamite transcription conventions, reconstructed sound contrasts and nominal endings must be distinguished. A character operation is not automatically an innocuous spelling variation or a historical sound law.

## Comparison with Dravidian and other languages

**The new open-target search has only been run on Elamite.** Its eight qualified directions or 680 raw witnesses cannot be ranked directly against a count of fixed Dravidian meaning pairs. They differ in targets, source sizes, coverage, morphology handling and review rules. No head-to-head probability or language winner was calculated.

There are relevant existing comparisons, but they answer different questions:

- Our [expanded fixed-meaning comparison](https://github.com/MSaadAsad/ivc-semantic/blob/research/independent-validation-2026-11-20/research/independent_validation_20261120/expanded_rebus_test/README.md) gives Dravidian 38/48, Sumerian 11/48, Akkadian 3/48 and Elamite 0/48 under its exact normalized / distinct-sense rule. Both concepts are covered in 48, 45, 31 and 18 pairs respectively. The panel was assembled through Dravidian-oriented research; these are not independently assigned archaeological meanings. On its broader automatic 51-pair panel, Dravidian 13 and Sumerian 14 do not exceed both specified chance baselines.
- Cúper’s [broader picture/class comparison](https://github.com/Cuuper22/ivc/blob/727dfd411a4faa44d193d204757540d45c7b139b/jobs/out/language_machine2.md) reports no family passing its combined sound-shuffle threshold. For the primary picture variant, Elamite’s unadjusted combined p is 0.16 and Dravidian’s 0.82. Those are not probabilities of the languages being correct; neither reaches the stated seven-family threshold. That experiment restricts destination meanings by machine classes and uses the older Elamite resource, so it is not the current unrestricted search.
- Our [selection-aware replay](https://github.com/MSaadAsad/ivc-semantic/blob/research/independent-validation-2026-11-20/research/independent_validation_20261120/selection_aware_rebus/README.md) retains an unusual Dravidian fit within its documented meaning-choice universe, while showing that choosing only successful candidates can manufacture a perfect retained count in every sampled randomized dictionary. It also does not supply an independent semantic assignment.

The present evidence therefore does **not** show Elamite matching better than Dravidian or the other languages. A fair new comparison would apply the same picture inventory, unrestricted target search, language-appropriate documented morphology, lexical coverage/size controls and review rules to every language, with its discovery choices repeated in the controls. It would then need predictive validation on actual inscriptions. That comparative experiment remains unrun.

Reproduce this size audit with `python3 research/independent_validation_20261120/elamite_validation/near_match_audit.py`. [Distinct pairs](results/near_match_distinct_pairs.csv). [Summary](results/near_match_summary.json). This audit reads existing candidates; it does not rerun the discovery or any prior language experiment. Colab units: 0.
