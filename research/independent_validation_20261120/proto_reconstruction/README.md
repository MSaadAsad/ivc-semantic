# Reconstructed vocabulary check across the full inscription inventory

21 November 2026. This follows the completed [reading-and-findspot catalogue](../translation_catalogue/README.md). It adds the **entire 15,629-record reconstruction table**, rather than treating modern Tamil headwords as Proto-Dravidian.

**The older reconstructions support some proposed wordplay, but they do not establish most of the proposed pairs as identical Proto-Dravidian forms.** Bow/sell is a clear positive lexical example. Fish/star and mountain/garland require a historical account of differing reconstructed forms. This is a full-table lexical screen, not a new reconstruction of the language, a sound-change chronology or a decipherment of previously unread objects.

## Complete scope

- **178 existing pair recipes across 93 candidate sign IDs**: the fixed 48, original 12, automatic 51 and later 30/13/24 panels. They overlap, use different breadths of meaning and are not 178 independent established readings. The automatic panel includes artifact-context domains, which are not independently assigned meanings.
- **All 163 current sign values**, with whole-form/etymon and explicit-component links. A lexical link is an opportunity to examine a proposed word, not verification of its meaning. Compound components do not establish a compound's grammar or ancient usage.
- **Every one of the 9,252 combined catalogue face/line observations**, retaining its existing proposed reading, city and recorded context. Lexical findings are attached to occurrences. Repeated signs and paired catalogues do not multiply lexical evidence.
- **Every reconstruction record**, including subgroup forms and the compilers' new proposals, remains available in source-separated outputs. Primary older-source comparisons use only records attributed to Krishnamurti (2003) or Starostin (2006–2013).

## What the fixed 48 show

| Recorded outcome | Proposed pairs |
|---|---:|
| Equal recorded forms at the Proto-Dravidian level, after the specified semantic/form exclusions | 3 |
| Apparent fourth equality excluded: “young; sprout” does not establish “human child” | 1 |
| Equality found only at a subgroup level in this screen | 9 |
| Both meaning domains recorded together, but no exact reconstructed-form equality | 20 |
| Incomplete two-sided reconstruction coverage | 15 |
| Total | 48 |

These are **not 3 proven readings and 45 disproven readings**. Exact equality is a deliberately narrow criterion: real rebuses can involve near-homophones, and a difference in a reconstruction is not a dated sound change. Missing coverage is not a historical absence. “Only at a subgroup level” describes this table's records, not proof that the word did not exist earlier.

The three lexical cases are:

| Proposed meaning pair | Recorded older reconstruction | Material qualification |
|---|---|---|
| Bow / sell, sign 892 | Krishnamurti *wil / *wil-; Starostin vil / vil- | The publisher's index directly corroborates the forms. The table's mechanical attestation classification supports “sell” only at South Total Dravidian; that is weaker than independently demonstrating both meanings across the family. It does not overturn the source author's reconstruction or date the word. |
| Rice/grain / tax, sign 413 | Starostin ari / ari | The table labels both Proto-Dravidian, but its attestation fields are narrower. Southworth explicitly questions projecting the administrative tax sense back unchanged from southern evidence. |
| Drum / capacity measure, sign 540 | Starostin par_- with both glosses | One polysemous reconstructed record, not two independent homophone etyma. Its attestation field supports South Total Dravidian. |

Consequently **none of those three passes the additional requirement that both table attestation flags independently support the source's Proto-Dravidian label**. That requirement is a mechanical documentation-breadth diagnostic, not an expert verdict on whether the reconstruction is valid. The superficially positive fourth case, sprout/child, would pass those flags but fails the human-child sense check. These distinctions prevent a small exact-match count from becoming a claim of historical validation.

## Concrete unresolved or contrasting cases

- **Fish / star:** Krishnamurti reconstructs *mīn “fish” but *miHn “star”; the publisher's index prints both. Starostin's corresponding forms are also distinguished in the table. South Dravidian I has an explicitly recorded *mīn alternative for the star family. This identifies a sound-history question; it does not establish when the forms converged or that the Indus reading fails. `H`, vowel length and the source's consonant notation are retained, not erased to manufacture a match.
- **Mountain / garland:** Starostin's Proto-Dravidian rows give màl- and māl-ai. The length/morphological differences remain visible. A sound-change and derivational account is needed before calling them the same ancient word.
- **Line / tax:** the line/scratch reconstruction is available at the Proto-Dravidian-labelled level; the tax word *var-i is recorded at subgroup levels in the older table. This is not proof that taxation or its vocabulary was absent in the Indus period. It is a gap in the claimed ancestral lexical support.

The full nearest-form diagnostic records exactly which written reconstruction characters differ. Its edit count is **not a phonological distance, a sound law or a date**, and it never upgrades a result to an exact match.

## Additional pairs from the larger table

`full_table_equal_form_pairs.csv` enumerates **4,236 pairs of reconstruction records** with different linked DEDR numbers, different glosses, the same source/ancestral level and an equal recorded form. **662** of these record pairs are attributed to the older sources at the Proto-Dravidian level. They are not 662 independent words, newly discovered etymologies or Indus readings; some are abstract templates, alternative reconstructions or duplicated source analyses. The `fully_specified_form` field distinguishes incomplete templates.

`new_picture_anchored_alternatives.csv` supplies **3,476 exploratory alternatives**, including **441 Proto-Dravidian-labelled alternatives** from the older sources, after excluding targets already covered by that sign's recorded recipes. Picture terms still come from the existing proposal. Broad recipes, species names, polysemy and gloss-matching errors require manual review. These candidates do not change the frozen key.

One concrete example is the proposed mountain sign: the older-source table records **màl- “mountain”** and **màl- “next, second”** under different etyma. This supplies an alternative dictionary possibility alongside the existing garland interpretation. It does **not** say that the sign means “second.” New context predictions would have to distinguish those possibilities.

## Source, correction and method

Source: Merriam & Fuls, [The Dravidian Database v1.2](https://zenodo.org/records/22682542), CC BY 4.0. The unmodified input is preserved as `results/input_table.csv.gz`; the released source README is `SOURCE_README.md`. Its 15,629 records include **3,512 labelled Proto-Dravidian**, of which **2,966** are attributed to the older sources. The remaining records are subgroup forms. Source labels and the compilation's mechanically inferred attestation labels are never conflated.

**Verified compilation error:** reconstruction record 6460 links Krishnamurti's “fish” to DEDR 4876. The [publisher's original reconstruction index](https://assets.cambridge.org/97805217/71115/index/9780521771115_index.pdf), printed p. 530, assigns fish to **4885** and star to **4876**. `source_corrections.json` applies that one documented link correction while retaining the original field and raw file. Bow/sell is independently checked on printed p. 531. This spot-check does not authenticate every imported row.

For each recorded recipe, the existing English patterns are fixed. The primary 48 also retain their cited DEDR families. Other panels search unrestricted etyma within the original meaning patterns and are explicitly broader. A witness must belong to the **same bibliographic source and ancestral level** on both sides. We compare reconstructed forms after Unicode NFC, removal of editorial asterisks, morpheme hyphens and trailing homonym indices, and separation of explicitly listed comma/semicolon/slash alternatives. Vowel length, consonant distinctions, `H`, accents and underscore notation remain. The compilation's lossy `simplified` column is **never** used to score historical homophony.

Unspecified `V`, uncertainty markers and optional segments do not count as fully specified pronunciations. “Young sprout” does not establish “young human”; “to bow” does not identify the pictured weapon; “fish-hook” does not identify a fish. Those are specified exclusions, not a claim that every remaining gloss witness has received expert semantic review. The matching remains a machine-assisted screen requiring source and sense review.

Component searches use explicitly proposed components and their already-cited etyma or identical written reconstructions. They do not derive a new pronunciation for a missing compound. Unknown signs remain unknown. No inscription's English translation is rewritten as a result of the vocabulary search, and no word is assigned an absolute date from a proto-language label.

This is retrospective work, not preregistered or independently blinded. Sources and reconstructions predate Cúper's current key, but share much of its underlying DEDR evidence. They do not supply independently assigned archaeological meanings. No p-value or probability of decipherment is manufactured from these counts.

## Results and reproduction

The searchable `results/word_pairs.html` now includes actual findspot examples for every sign with recorded occurrences: reference, full recorded location, strata, material and existing proposed translation. Each entry links to every occurrence in the complete catalogue. The examples are chosen for metadata completeness, not as evidence that the proposed meaning is correct.

- `pair_summary.csv`: all 178 recipes and source-qualified outcomes.
- `all_pair_level_results.csv`: every source/level cell, including zeros and missing sides.
- `all_pair_reconstruction_candidates.csv`, `equal_form_witnesses.csv`: every matching reconstructed row and equality witness.
- `nearest_PD_form_differences.csv`: precise transcription differences.
- `all_163_sign_results.csv`, `all_163_reconstruction_links.csv`, `all_explicit_component_links.csv`: every current sign and its lexical opportunities, including missing links.
- `all_inscriptions_reconstruction_screen.csv`: every corpus observation with the lexical findings attached.
- `direct_meaning_reconstructions.csv`: numerals and direct meanings, kept separate from two-sided pun counts.
- `full_table_equal_form_pairs.csv`, `new_picture_anchored_alternatives.csv`: the full discovery outputs, explicitly exploratory.

```sh
python research/independent_validation_20261120/proto_reconstruction/run.py --source /path/to/pdr_04.csv
python research/independent_validation_20261120/proto_reconstruction/check.py
```

Python 3.9+, standard library; the run takes seconds, with no Colab units. The check verifies all source rows, all recipe IDs, all sign values, every catalogue observation, source/level separation, preserved phonological distinctions and the recorded semantic exclusion.

Further primary discussion of the tax/ancestral-meaning issue: [Southworth, Proto-Dravidian Agriculture](https://ccat.sas.upenn.edu/~fsouth/Proto-DravidianAgriculture.pdf), pp. 3–7. Reconstructing a form does not automatically reconstruct every later administrative meaning attached to it.
