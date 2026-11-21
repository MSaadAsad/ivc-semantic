# Meaning-matched overlap: Brahui, Kurukh, Malto and the other Dravidian languages

**Broader follow-up:** [full dictionary overlap and synonyms](../full_dictionary_overlap/README.md) examines 5,558 recoverable groups, including 274 with Brahui, beyond this 100-word source. It recovers historical synonyms and corrects the dictionary extraction counts below: the 73-anchor totals become Kurukh 18, Malto 15, Kannada 61 and Brahui 9. The eleven-concept DravLex results remain the original elicited-list results, not absence claims about the languages' full vocabularies.

**Brahui, Kurukh and Malto each match 5 of 11 scorable basic meanings in an additional, meaning-matched wordlist comparison.** Kannada also matches 5, Telugu 4, Malayalam 8 and Tamil 10. The proposed vocabulary overlaps more with Tamil and Malayalam in this small panel, but the northern overlap is substantial and is obscured by comparing exact spellings. The three northern languages match different subsets; none separates from the other two by total score here.

This extends the earlier [spelling and dictionary-portability audit](../language_affinity/README.md). It holds the meanings and intended dictionary entries fixed, rather than accepting any homonym with the key's spelling. It adds a pinned external modern wordlist and dictionary-coverage controls. These calculations compare the proposed vocabulary; they do not establish that the signs actually have those meanings.

## New source and comparison rule

We downloaded the openly licensed **DravLex** CLDF dataset, derived from Kolipakam and colleagues' comparative work, at commit **`37578075e5ccb09c43022f7f1282125e748de84d`**. It contains **2,127 forms for 100 basic meanings across 20 language varieties**, with published cognate judgments and loan flags. Source files, license, citations and hashes are bundled in [external/dravlex](external/dravlex).

The additional source provides elicited modern forms and annotations, rather than another search over the same raw DEDR extraction. Its etymological judgments themselves draw substantially on DEDR, so it is not an independent confirmation of those etymologies or of the Indus proposal. Neither the proposed semantic assignments nor the selection of readings is independent.

We assembled a retrospective [13-concept panel](panel.json) from basic meanings explicitly represented by the existing proposals: eye, fish, foot, head, horn, man, moon, mountain, one, star, two, sit and see. Each is anchored to a particular DEDR entry and sense. We excluded generic meanings that would require changing the proposal: young plant is not automatically generic tree, hump is not generic back, and bend is not generic nose. The proposed small/cikka connection remains unresolved and was not silently repaired.

Ten concepts have a cognate class linked to the intended DEDR entry by explicit references in the source annotations. For **see**, the recorded Tamil `kāṇ-` in class `see-A` supplies a manual link to the proposal's DEDR 1443; a separate sensitivity removes this link. **Moon/tiṅkaḷ** and **sit/iru** have no identifiable corresponding class in this source and remain **unscorable**, rather than being counted as failures for every language. Thus the primary panel contains **11 meanings**. This is a small, curated panel, not a random sample of the key or a preregistered test.

A match requires a recorded word for the **same meaning** assigned by the source to the intended cognate class. Exact spelling is unnecessary. We exclude forms explicitly marked as loans and judgments marked doubtful. A different recorded cognate class counts as no match in this elicited list; a missing word is reported as missing. Neither establishes absence from the language's full vocabulary.

## Results on the same 11 meanings

All seven languages below have recorded words for all 11 meanings:

| Language | Matching cognate families | Recorded meanings |
|---|---:|---:|
| Tamil | **10** | 11 |
| Malayalam | **8** | 11 |
| Kannada | **5** | 11 |
| Brahui | **5** | 11 |
| Kurukh | **5** | 11 |
| Malto | **5** | 11 |
| Telugu | **4** | 11 |

This replaces the misleading impression that one exact Brahui spelling means almost no Brahui overlap. It also gives a real difference in the other direction: the proposed cognate families occur more often in this Tamil and Malayalam list. The vocabulary was originally selected with a Tamil-first dictionary workflow; that selection effect persists even after we fix the meanings.

The full 20-variety results are in [dravlex_summary.csv](results/dravlex_summary.csv). Some varieties have substantial missingness: for example Parji has only 6 of the 11 meanings recorded, so its four matches must not be compared as four observed failures plus additional zeros. Analyses use recorded coverage explicitly.

The eleven concepts do not deliver a statistically resolved language ranking. We calculated two-sided exact paired tests on shared recorded meanings for all **190 language pairs**, with Holm adjustment; **none passes 0.05 after adjustment**. Brahui versus Tamil has one Brahui-only match and six Tamil-only matches (unadjusted p=0.125). Brahui versus Kurukh has one match unique to each, and Brahui versus Malto has two unique to each (both p=1). These tests describe this selected small panel; they are not probabilities of which ancient language was spoken.

## What overlaps in the northern languages?

| Meaning / intended family | Brahui | Kurukh | Malto |
|---|---|---|---|
| Eye — DEDR 1159 | **xan** | **kʰann** | **a:ndu** |
| Fish — DEDR 4885 | Different, loan-flagged form | Different family | **mi:ndu** |
| Foot — DEDR 1479 | Different family | Different family | Different family |
| Head — DEDR 3103 | Different family | Different family | Different family |
| Horn — DEDR 4720 | **maɾgʰ** | **maɾag** | **maɾgadu** |
| Man — DEDR 399 | Different family | Different family | Different family |
| Mountain — DEDR 4742 | **maʃ** | Different family | Different family |
| One — DEDR 990 | **asit** | **o:nd** | **o:nd** |
| Star — DEDR 4876 | Different, loan-flagged form | **bi:nko** | **bi:nka** |
| Two — DEDR 474 | **iɾat** | **i:rəb** | Different families |
| See — DEDR 1443, manual anchor | Different family | Different family | Different family |

Forms and cognate assignments above follow the pinned source, including its transcription and dialect differences. In particular the source classifies Malto `a:ndu` with the eye family despite the surface difference; we have not independently reconstructed its phonology. Every recorded form, alternative class and loan flag is released in [dravlex_concept_scores.csv](results/dravlex_concept_scores.csv), and the actual source comments establishing the entry/class anchors are in [dravlex_annotation_witnesses.csv](results/dravlex_annotation_witnesses.csv).

Two examples matter:

- **Horn favors the northern recorded forms:** all three northern words belong to the proposed *maruppu* family. The elicited Tamil word is `kombə`, assigned to another family. Tamil has historical *maruppu* in DEDR; the modern list is not an exhaustive dictionary.
- **Mountain provides a Brahui connection:** Brahui `maʃ` and Tamil `malai` are assigned to the same family. The recorded Kurukh and Malto terms belong elsewhere. This is a concrete difference among the northern lists, even though their totals tie.

Removing the one manual see anchor leaves a **10-concept** panel: Tamil **9**, Malayalam **7**, and Brahui, Kurukh, Malto and Kannada **5** each; Telugu remains **4**. Including the flagged loans also has its own released run. A source loan flag does not exhaustively identify Balochi, Iranian, Indo-Aryan or uncertain loans, so this is not a completely de-borrowed Brahui lexicon.

## Broader dictionary overlap, with coverage controls

The small basic-word panel cannot represent titles, measures, commodities and most of the proposed key. We therefore also fixed a broader set of **73 distinct DEDR entries**: all entries in the previously frozen 35 sign–etymon-pair claims, plus the 13 basic-concept anchors, deduplicated. This does not search for replacement etymologies. The supplied dictionary extract yields 5,224 numbered entry chunks after splitting glued rows.

We record whether each language is explicitly represented in an entry's main text. This is **dictionary attestation**, not proof that a particular sense or proposed rebus survives in that language. Raw entry segments are provided for checking; compound forms or a cognate with a shifted meaning may still produce an attestation. English continuation words misread as headwords by a form parser do not determine this entry-level measure.

| Language | Target entries attested, out of 73 |
|---|---:|
| Tamil | 70 |
| Malayalam | 63 |
| Telugu | 62 |
| Kannada | 60 |
| Kurukh | **17** |
| Malto | **14** |
| Brahui | **10** |

Raw counts reflect unequal documentation. We sampled **4,999 control entry sets**, excluding the targets, and exactly matched the targets' presence/absence patterns in Tamil, Malayalam, Kannada and Telugu. A stronger sensitivity additionally matches general coverage in other languages in bins of 0, 1–3 and 4+, excluding the focal language and all three northern languages from that breadth count. Thus a northern result is not conditioned on its own presence or on another northern language. The four major languages are conditioned variables here: their observed counts equal their expected counts by construction, and are not an adjusted superiority result.

Under the stronger control:

| Language | Observed | Matched expected | Observed / expected | Upper-tail p, unadjusted |
|---|---:|---:|---:|---:|
| Kurukh | 17 | 13.48 | **1.26** | 0.1606 |
| Malto | 14 | 12.15 | **1.15** | 0.3158 |
| Brahui | 10 | 6.99 | **1.43** | 0.1508 |

Brahui has the largest **relative excess among these three** in this control, while Kurukh has the largest absolute overlap. These point estimates do not establish a difference among their affinities: each northern observed count lies inside its matched 95% simulation range (Kurukh 8–20, Malto 7–18, Brahui 3–12), and each has Holm-adjusted p=1 across all 42 language/control combinations.

With only the major-language pattern matched, the corresponding ratios are **1.49, 1.40 and 1.66**, with unadjusted p **0.0560, 0.1098 and 0.0714**. Both controls and all other languages are preserved in [fixed_etyma_summary.csv](results/fixed_etyma_summary.csv). The weaker control also detects enrichment outside the north, including Kota, Toda and Kodagu; it is not a uniquely northern pattern. These conditional simulations diagnose dictionary selection and coverage. Related etymologies, semantic domains, retrospective target selection and remaining documentation differences prevent treating them as a complete model of chance decipherment.

## What this adds and what follows

Compared with the earlier spelling comparison, we now have a shared-meaning, sound-tolerant comparison from an additional modern source, a concrete list of northern overlaps and differences, a fixed-entry analysis with coverage controls, and tests that expose how small the effective comparison is. We have not added new validated sign meanings, discovered an independent archaeological holdout, or shown that a northern or southern language is the Indus language.

The useful leads are specific: Brahui mountain and the northern horn family survive a meaning-matched comparison; the northern lists divide on fish, star and two. Those contrasts can guide prospective tests once the corresponding Indus meanings or sounds are independently constrained. They cannot validate those meanings by themselves. The main dossier's requirement for independent semantic assignment and predictive archaeological validation remains unchanged.

## Reproduce and credit

Python 3.9+; standard library only; no network access required after checkout:

```sh
python3 research/independent_validation_20261120/language_overlap/compare.py
python3 research/independent_validation_20261120/language_overlap/check.py
```

The script verifies pinned input hashes, writes all results locally and uses deterministic seed 20261121 for the simulations. `--freeze` documents the original input capture and is not a way to bypass input changes. The source-example checks cover loan flags, sound-different cognates, the horn counterexample, unscorable concepts, manual anchoring and accounting. They do not certify every dictionary segmentation or published cognate judgment.

Credit: Kolipakam, Vishnupriya, Michael Dunn, Fiona M. Jordan and Annemarie Verkerk (2018), **DravLex: A Dravidian lexical database**, with the Lexibank CLDF editors and contributors identified in the bundled README. The downloaded dataset is [CC BY 4.0](external/dravlex/LICENSE); this analysis uses the [pinned GitHub snapshot](https://github.com/lexibank/dravlex/tree/37578075e5ccb09c43022f7f1282125e748de84d), which differs from the tagged v1.1 release. Original study: Kolipakam et al. (2018), [A Bayesian phylogenetic study of the Dravidian language family](https://doi.org/10.1098/rsos.171504). The upstream Indus project retains credit for its hypotheses and supplied dictionary. The present coding and interpretation do not represent independent human linguistic adjudication.
