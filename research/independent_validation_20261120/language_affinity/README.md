# Which Dravidian language is the proposed key closest to?

**Follow-up:** the [meaning-matched overlap comparison](../language_overlap/README.md) adds a pinned DravLex source and dictionary-coverage controls. It finds 5/11 scorable cognate families in each of Brahui, Kurukh and Malto, versus Tamil 10/11 and Malayalam 8/11. These are different measures from the exact-spelling counts below; one exact Brahui spelling never meant only one related word.

The subsequent [full dictionary and synonym investigation](../full_dictionary_overlap/README.md) improves extraction recovery and documents missed synonyms, shifted meanings and qualified comparisons. Earlier parser-dependent counts below are historical results; use the full-inventory report for current dictionary attestation coverage.

**The proposed key is closest to recorded Tamil forms. This measures the proposal's lexical sources; it does not identify the language of the Indus inscriptions.** The source code explicitly chooses Tamil first when it constructs its representative Dravidian headwords. A new, retrospective comparison across 21 languages quantifies that preference and checks how some of the claimed sound bridges travel across the family.

This extension was requested after the independent semantic-validation dossier. It adds language-by-language extraction, comparisons and inspectable witnesses to the existing research branch. It uses the repository's existing dictionary and hypotheses; it supplies neither fresh archaeological observations nor independent semantic judgments.

## 1. The printed key

The 163-sign master contains **87 distinct starred lexical components**, after splitting alternatives and compounds, removing bracketed English operators such as `[CAGE]`, and collapsing repeated roots. Allographs and repeated components do not multiply the sample. Eighty-four components are found somewhere in the parsed dictionary. Three (`iṉ`, `paṉṉiru`, `ēḻ`) are not located under this conservative extraction; this does not establish their absence from the languages.

| Language | Exact matches to the 87 key components | Components with a form in an identified cognate set |
|---|---:|---:|
| Tamil | 83 | 83 |
| Malayalam | 54 | 82 |
| Kannada | 30 | 79 |
| Telugu | 8 | 79 |
| Brahui | 1 | 27 |

There are **76 components with cognate-set coverage in all four major literary languages**. Their mean normalized spelling distance to the printed components is Tamil **0.000**, Malayalam **0.093**, Kannada **0.225**, Telugu **0.372**. Zero means an exact match. This is a description of spellings, not a historical distance estimate or a probability of identification. Cognate sets are located through exact component matches anywhere in the dictionary; homonyms can give more than one candidate set. We do not infer a particular sense from this lookup.

The causal problem is visible in `work_scripts/key2a_rebus_lock.py`, function `build_fixed_pdrav_2branch`: its language priority begins `Ta, Ma, Ka, Ko, Tu, Te` and ends with `Br`. It assigns `root_hw` from the first eligible form, then builds most of its English gloss material from Tamil, Malayalam, Kannada and Telugu. Consequently, an exact-spelling test is predisposed to return Tamil. The dictionary's [own preface](https://dsal.uchicago.edu/dictionaries/burrow/frontmatter/frontmatter.html), §§11–12 and 45–46, also explains its unequal lexical resources and Tamil head position, while warning that Tamil forms are not automatically Proto-Dravidian reconstructions.

## 2. Hold the claimed etymon pairs fixed

To avoid finding replacement dictionary matches for every language, we extracted **35 sign–etymon-pair claims for 24 signs**, comprising **33 distinct ordered etymon pairs**, from the two latest upstream bridge tables (`key5a` and `key6a`). The actual DEDR entry numbers stay fixed. Repeated pairs used for several signs remain visible; these are not 35 independent discoveries. Direct, single-entry semantic bridges are outside this particular comparison.

For each language we retrieve its attested forms in those same two entries and measure the smallest normalized edit distance between forms. No substitute etymon is permitted. Forms can include derivatives or different senses within an entry, so this is an **optimistic form-retention check**; matching spelling does not certify the intended meaning or a plausible ancient rebus.

| Language | Both entries represented, out of 35 | Exact form pairs | Exact pairs when vowel length is folded |
|---|---:|---:|---:|
| Tamil | 34 | 16 | 21 |
| Malayalam | 26 | 5 | 8 |
| Kannada | 25 | 2 | 4 |
| Telugu | 27 | 0 | 1 |
| Brahui | 0 | 0 | 0 |

On the **21 pairs covered in all four major languages**, exact matches are Tamil **7**, Malayalam **2**, Kannada **2**, Telugu **0**; after folding vowel length they are **11, 5, 4, 1**. This confirms that the selected bridges are more portable into Tamil in this dataset. They were developed using the same dictionary and Tamil-first representation, so this is a conditional property of selected hypotheses, not an independent branch-identification result. No significance test treats these selected, partly repeated pairs as independent evidence.

**Brahui's zero is a coverage failure:** none of these pairs has both entries represented in our Brahui extract. It is not 35 observed phonetic mismatches. The conservative extract has **225 Brahui etymon groups**, compared with **3,524 Tamil groups**. Neither number is a count of the language's entire vocabulary.

See [fixed pair witnesses](results/fixed_pair_portability.csv), [summaries](results/fixed_pair_summary.csv) and the source claims retained in [design.json](design.json).

## 3. A rebus that does not distinguish Tamil

The established proposal **fish → star** gives a useful diagnostic example. In the source DEDR entries **4885** (fish) and **4876** (shine/star), both senses have the same form in:

| Language | Fish | Star |
|---|---|---|
| Tamil | mīṉ | mīṉ |
| Malayalam | mīn | mīn |
| Kannada | mīn | mīn |
| Kota | mi·n | mi·n |
| Toda | mi·n | mi·n |

The dictionary often omits the fish gloss after its first appearance. Our extraction preserves those cognates and flags the inferred gloss; otherwise a parser could falsely make this rebus appear Tamil-specific. This lexical example is compatible with several languages. Whether an Indus fish sign actually means “star” still requires independent evidence.

## 4. Broader keyword search: diagnostic appendix

We also copied **79 historical visual/target domain specifications**, keeping the latest per sign to produce **68 distinct sign hypotheses**, including failed and retested proposals. Without adding synonyms, each language was searched for the copied English keywords on both sides. Exact normalized forms yield candidate links; same-entry links and links across different DEDR entries are separate.

With explicit and conventionally omitted/`id.` glosses included, length-preserving candidate counts are Tamil **59/68**, Malayalam **26/68**, Kannada **25/68**, Telugu **16/67** and Brahui **1/14** (numerators are signs with any candidate; denominators are signs with at least one recorded word on both sides). The four-major-language common-opportunity set contains 67 signs. The one Brahui candidate is sign 690, with words glossed “knot, bundle”; overlapping meanings make this a weak discriminator.

These are **keyword-retrieval candidates, not adjudicated semantic successes**. Broad or overlapping English glosses, dictionary richness, selection of the domains during earlier Dravidian searches and variant forms can all increase counts. Reporting opportunity coverage alone does not correct these effects. Different DEDR numbers are not guaranteed independent etymologies. We therefore do not use these counts to rank the ancient language. All four combinations of explicit/inferred glosses and preserved/folded vowel length are released, including every witness and sign-level result.

## 5. Brahui without Balochi influence

Inherited Brahui material is a usable comparison source. [Elena Bashir's comparative notes](https://salrc.uchicago.edu/workshops/sponsored/121203/resources/brahui.pdf) identify retained Dravidian numerals, pronouns and morphology alongside contact effects. In the repository dictionary, Brahui **nī** “you” (DEDR 3684) and **iraṭ** “two” (DEDR 474) provide concrete inherited comparisons. Their wider distribution makes them poor evidence for a specifically Brahui identification.

This run **does not claim to have removed all Brahui loans**. Its automatic exclusion only recognizes explicit Sanskrit/Prakrit/Indo-Aryan loan notation in entry headers; it removed no entries in this input. It does not screen Balochi, Persian or Arabic loans, mixed derivatives, calques or contact-induced phonological changes. A defensible inherited-only Brahui dataset needs item-level source histories, dialect labels and uncertain cases retained as uncertain. Modern geography alone cannot date a feature to the Harappan period.

## 6. What would identify a branch?

The next comparison should discriminate **shared innovations** and dated sound correspondences, rather than rewarding vocabulary shared throughout Dravidian. A generic SOV order, an agglutinative suffix or a widespread numeral cannot identify a particular branch. The dictionary preface's example of Tamil palatalization of earlier *k* before front vowels illustrates the kind of contrast worth testing; an inscription would need an independently constrained sound value to make that contrast observable.

An executable next study would:

1. Obtain archaeological semantic assignments from raters who do not see the proposed Dravidian roots. Lock accepted alternatives and disagreements before lexical lookup.
2. Specify equal search budgets, transcription rules, morphology and contact exclusions for Tamil/Malayalam, Kannada/Tulu, Telugu and other southern/central languages, Kurukh/Malto and Brahui. Treat ancestral or extinct sister varieties as explicit possibilities.
3. Select contrasts where those models predict different rebus survival, sound correspondences or morpheme positions. Discard shared-retention examples as branch discriminators.
4. Freeze each model's predictions, then test them on held-out archaeological observations and any independently anchored name or sound evidence. Keep sign-identity and structural baselines, matched rival meanings and correction for selecting among languages.

The present evidence supports a clear statement about **the proposal's Tamil-shaped construction**. It does not yet distinguish an ancient Dravidian branch, establish a Brahui-specific connection, or replace the independent semantic assignment and predictive validation required by the main dossier.

## Reproduce and inspect

Python 3.9+ and the standard library are sufficient:

```sh
python3 research/independent_validation_20261120/language_affinity/audit.py
python3 research/independent_validation_20261120/language_affinity/check.py
```

The first script verifies frozen input hashes before writing outputs. `--freeze` documents the original extraction and must not be used to bypass an input mismatch. Its required inputs include the existing raw DEDR TSV and latest bridge tables, in addition to scripts and the master key. It imports no upstream analysis modules and changes no proposed roots.

The raw input has 4,621 physical TSV rows; conservative splitting yields 5,224 numbered entry chunks. This is a parse of the supplied extract, not a claim to have exhaustively captured the printed dictionary. Nested notes are excluded; internal optional phones retain the shorter form. Primary normalization preserves vowel length and consonant distinctions, maps equivalent r̤/ḻ transcription, and converts DEDR vowel-length dots to macrons. The length-folded sensitivity changes only the five long-vowel spellings. Whole `id.` and empty glosses inherit the previous explicit gloss within an etymon and are individually flagged. Such inherited glosses still require linguistic checking.

The released source-example checks verify Brahui numerals/pronouns, punctuation-less Kui/Kuwi/Konda labels, omitted fish glosses, all five fish/star witnesses, and output accounting. These checks guard specific extraction failures; they do not certify every parsed record. [All results](results) include the parsed forms for inspection, the complete 21-language summaries and candidate witnesses. No human semantic ratings, reconstructed ancestral lexicon or independent decipherment accuracy is claimed.
