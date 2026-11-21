# Broader dictionary overlap, including synonyms

**This comparison covers all 5,558 recoverable numbered groups in the supplied full DEDR text and TSV fallback, across 21 languages. It is not restricted to the 100-word list.** We recover **274 groups containing a Brahui form**, including **48 explicitly questioned comparisons** and **226 without that marker**. These are dictionary groups, not 274 proven inherited words or an exhaustive Brahui vocabulary.

The main finding is twofold: many Brahui synonyms were outside the elicited list, and the full Brahui inventory has a stronger relative overlap with Kurukh–Malto than its raw overlap with the much larger Tamil dictionary inventory suggests. This characterizes recorded comparative vocabulary, not the language of the Indus inscriptions.

## Full-inventory overlap

For each Brahui-containing group, we checked which other languages appear in the same group, including historical forms and synonyms. Different senses and questionable comparisons remain visible; group membership alone does not prove identical semantics or borrowing direction.

| Other language | Groups also containing Brahui, out of 274 | Total groups for that language | Shared groups after excluding questioned Brahui comparisons, out of 226 |
|---|---:|---:|---:|
| Tamil | **223** | 3,533 | 186 |
| Malayalam | **205** | 2,753 | 171 |
| Kannada | **199** | 3,070 | 162 |
| Telugu | **195** | 2,732 | 160 |
| Kurukh | **114** | 793 | 100 |
| Malto | **104** | 719 | 91 |

Raw totals favor languages with large dictionary inventories. We therefore also standardize against non-Brahui groups having **exactly the same number of other recorded languages**, excluding Brahui and the language being evaluated. Each Brahui group contributes the background probability for its exact coverage stratum. Groups without controls are explicitly excluded, not assigned zero: all 274 are eligible for Tamil, Kannada, Telugu and Kurukh; 273 are eligible for Malayalam and Malto.

| Other language | Shared groups in eligible strata | Expected from exact documentation breadth | Observed / expected |
|---|---:|---:|---:|
| Tamil | 223 | 223.42 | **1.00** |
| Malayalam | 204 | 189.26 | **1.08** |
| Kannada | 199 | 209.10 | **0.95** |
| Telugu | 195 | 200.27 | **0.97** |
| Kurukh | 114 | 85.54 | **1.33** |
| Malto | 103 | 83.79 | **1.23** |

Kurukh and Malto have the two largest ratios among all twenty comparators under this exact-breadth standardization. This is a descriptive comparison of dictionary co-attestations, not a reconstructed family tree or evidence that an Indus inscription is northern Dravidian. Editorial choices, semantic change, related entries, inheritance and borrowing all affect the inventory. The separate [questioned-comparison sensitivity](results/brahui_exact_breadth_standardization.csv) reports the exact-breadth calculation on the 226 unmarked Brahui groups as well.

The simple Jaccard comparison also shows why a single ranking is insufficient: Kurukh is highest at 0.1196, **Toda is next at 0.1183**, then Malto at 0.1170. All 441 ordered language comparisons, including inventory sizes and both directional overlap fractions, are in [all_language_pair_overlap.csv](results/all_language_pair_overlap.csv).

For completeness we preserve a coarser breadth-matched simulation with 1,999 draws, bands 0–3, 4–7 and 8+ other languages, and Holm correction across twenty comparisons. Its apparent excesses are larger, because wide bins leave documentation differences within them. The exact-breadth ratios above are the preferred descriptive adjustment. Neither procedure is calibrated as a test of ancient-language identification.

## What the broader search actually recovers

The following entries can be inspected directly in the [complete Brahui inventory](results/brahui_full_inventory.csv). They illustrate several different relationships; they are not a new list of validated sign readings.

| Meaning or domain | Recorded Brahui form | Comparative entry and interpretation |
|---|---|---|
| See | **xaning** | DEDR 1443, with Tamil *kāṇ*. A genuine documented synonym missing from the elicited see cell. |
| Eye | **xan** | 1159, with Tamil *kaṇ*, Kurukh *xann*, Malto *qanu/qan*. |
| Bow | **bil** | 5422, with Tamil *vil*. Extends the comparison beyond the short scored panel. |
| Milk / milky sap | **pāḻẖ** | 4096, with Tamil *pāl* and several other languages. |
| Three | **musiṭ**, adjective **musi** | 5052, with the Tamil *mūṉṟu/mū-* family. |
| You, singular / plural | **nī / num** | 3684 / 3688; broadly shared pronominal material, not a unique northern diagnostic. |
| Mother / grandmother | **ammā** | 183; a widespread kin/nursery word, a weak branch discriminator. |
| Horn | **marg̠ẖ** | 4720, with Tamil *maruppu*, Kurukh *marᵃg*, Malto *margu*. Tamil's historical form matters even if a modern list records another word. |
| Mountain | **mash** | 4742, with Tamil *malai* and other southern/central forms. No Kurukh or Malto member appears in this entry. |
| Hold / keep / restrain | **tōning** | 3480, with the *toṭu* touch/hold family. The semantic range is not identical across languages. |
| House / wife | **urā** | Recorded under 752 (*ūr* village/town), alternatively 698 (*uḷ* inside). A Dravidian comparison with competing analyses; not the proposed *kuṭi* house family, 1655. |
| Cooking pot | **xō** | 2225, alongside Tamil *kōy* vessel for taking out toddy. Not the proposed *kuṭam* family, 1651. |
| Old / broken earthen pot | **kalanḍ** | 1305, alongside *kalam* vessel/ship. The dictionary questions the Brahui comparison. |
| Twist, especially a rope | **pirg̠ẖing** | 4177, with the *piri/puri* twist/strand family. |
| Bundle / knot | **putunk; muṭṭux** | 4509; 4921. Other lexical families than the proposed *kaṭṭu* 1147; semantic availability is not proof of that proposed rebus. |
| Clothes / cloth | **puc** | 4479, a questioned comparison. Not the proposed *tai* sew/weave family, 3473. |
| Sit / dwell | **tūling**, Nushki **tūsing** | 3291, alongside Tamil *tuñcu/tuyil* sleep/stay. The relation to *tūṅku*, 3376, is cross-referenced with a question; do not merge sit, sleep and hang as one unchanged sense. |
| Moon | **tūbē** | A questioned comparison under brightness/purity, 3338, with an additional white-word cross-reference. Not the *tiṅkaḷ* moon/month family, 3213; it is not automatically Persian. |

These examples show why we must distinguish: a synonym omitted by a short list; a related root with changed meaning; a different root for the same concept; an explicitly uncertain comparison; and an identified loan. Only the first case directly repairs a missing-word inference. None supplies independent archaeological support for a sign meaning.

## Relation to the current proposed vocabulary

The same previously frozen set of **73 DEDR anchors** from the 35 sign–etymon-pair claims plus basic-concept anchors is retained for continuity; it does not cover every component of the 163-sign key. Under the improved extraction, group attestations are Tamil **70**, Malayalam **63**, Telugu **62**, Kannada **61**, Kurukh **18**, Malto **15**, Brahui **9**. The [complete witnesses](results/fixed_target_witnesses.csv) include empty and qualified cells explicitly.

The Brahui anchors include *xaning* see, *xan* eye, numerals one/two, horn, mountain, hold/keep, a skip/prance form and a tripod noun. The tripod **trikkal** in entry 1479 is not by itself evidence that ordinary Brahui “foot” is *kāl*. Basic wordlists and dictionary-family attestations answer different questions.

The broader dictionary still has no Brahui member in several **particular proposed families**: *kuṭam* pot (1651), *kuṭi* house (1655), *aḷa* measure (295), *paṭi* weight/allowance (3849), *vari* tax (5266), *tai* sew/weave (3473), *vēl* spear (5536), or *vēḷ* chief (5545). This does not mean Brahui lacks words for those concepts. We have documented some alternative roots above; we have not established inherited replacements or a specific donor language for every remaining concept.

**Extraction correction:** the preceding 73-anchor report gave Kurukh 17, Malto 14, Kannada 60 and Brahui 10. A broken opening bracket in entry 399 hid later language sections, while an empty `Br.` label in 4100 was wrongly counted. The full-text pass recovers the three language sections in 399 and removes the empty Brahui label. The earlier 11-concept DravLex scores do not change. Earlier source-dependent spelling and dictionary counts remain historical runs; the full inventory and current 73-anchor attestation counts here supersede their extraction coverage.

## Are the Brahui replacements Persian, or unknown?

The six failures in the elicited eleven-concept Brahui comparison require separate answers. Loan flags alone were incomplete: `false` did not establish inheritance.

| Elicited Brahui word | Meaning | Checked interpretation |
|---|---|---|
| **machchī** (`matʃtʃi:`) | Fish | Indo-Aryan loan; DravLex suggests Hindi/Sanskrit, while the Bray-based annotated list specifically compares Sindhi. No basis here to label it Persian. |
| **istār** | Star | Borrowed. The Bray-based list calls it Persian; DravLex tentatively suggests Hindi. Immediate donor route remains unsettled in this review. |
| **narēna / narīna** | Man / male | Strong Iranian comparison: *narīna* “male, masculine” is independently recorded as Persian in Platts. Likely contact vocabulary is an inference here; the precise route into Brahui is not established. The DravLex loan flag did not identify it. |
| **nat** | Foot / leg | An Indo-Aryan derivation has been proposed but is not conclusive; retain as unresolved. |
| **kāṭum** | Head | No specific Persian derivation established in the checked material. Do not equate an unidentified cognate with a proven ancient native word. |
| **unning** | See | Etymology unresolved in the scored source. Brahui also has documented **xaning** in the *kāṇ* family, so this recorded alternative never justified saying that family was absent. |

The [Bray-based annotated Brahui wordlist](https://starlingdb.org/new100/bra.pdf), entries 29, 31, 38, 51, 72 and 80, supplies the historical comparisons and synonyms. [Platts as reproduced by Rekhta](https://www.rekhta.org/urdudictionary?keyword=nariina) supplies the independent Persian comparison. The source annotations behind the elicited forms remain in the pinned [DravLex data](../language_overlap/external/dravlex/cldf/cognates.csv). These observations do not constitute exhaustive loan cleaning or establish a prehistoric contact chronology.

## Reproduce and inspect

```sh
python3 research/independent_validation_20261120/full_dictionary_overlap/analyze.py
python3 research/independent_validation_20261120/full_dictionary_overlap/check.py
```

Python 3.9+ and its standard library suffice. The script verifies hashes of the supplied full DEDR text, TSV, and prior frozen anchor definitions; no network access or upstream analysis imports are needed. Input capture is documented by `--freeze`, not regenerated on default reruns.

The full-text extraction recognizes line-start and inline numbered headers, including lettered subparts and language-label variants. It selects a longest nondecreasing numeric sequence to avoid turning wrapped cross-references into entries, preserves repeated sections under the same number, and falls back to explicitly numbered TSV rows for 5382 and 5530. Within chunks it neutralizes **338 unmatched parentheses**, without changing words, so a broken bracket does not hide all later languages. Every repair and rejected header candidate is released. This improves recovery; it is not a claim that all OCR and segmentation errors have been removed.

The output comprises the complete group-presence matrix, 441 language-pair rows, every Brahui group with raw language text and qualifiers, the fixed-anchor witnesses, exact-breadth standardization, questioned-comparison sensitivity and deterministic simulation draws. Checks verify recovered synonyms, the 399 bracket failure, the 4100 empty-label failure, qualified comparisons, symmetry and totals. Credit remains with Burrow and Emeneau's [Dravidian Etymological Dictionary](https://dsal.uchicago.edu/dictionaries/burrow/frontmatter/frontmatter.html), the supplied upstream extract, and the cited lexical researchers. No independent human adjudication or new archaeological semantic assignment is represented as completed.
