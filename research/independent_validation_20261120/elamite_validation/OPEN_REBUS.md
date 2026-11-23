# Additional Elamite rebus candidates for Indus signs

23 November 2026. **The search now extends to alternative meanings, instead of requiring Elamite to reproduce Cúper’s Dravidian-oriented pairs.** It produces two priority lexical leads and several weaker ones. It does not supply a full Elamite translation or identify the Indus language.

[Open the illustrated, searchable report](results/open_rebus.html). [Reviewed leads](results/open_rebus_curated_leads.csv). [All 680 raw witnesses](results/open_rebus_all_candidates.csv). [Complete source review](results/open_rebus_review.csv).

## What we found

| Picture | Elamite bridge | Alternative meaning | Evidence and qualification |
|---|---|---|---|
| Roof | ku-uk → ku-uk | **Protection** | The legacy dictionary explicitly labels literal roof and figurative protection; the structured release also gives protection. Recorded polysemy, not a newly demonstrated unrelated homonym. Roof is only one interpretation of the chevron drawings. |
| Jar / jug | pi-ti → pi-ti-r | **Enemy** | The structured source gives jug and enemy-SG; final -r is a documented noun-class ending. **Same stem, not identical whole words.** The older jug interpretation is uncertain. |
| Door / gate | hi-el / hu-el → same forms | Royal court | Recorded gate-to-court metonymy, with late figurative attestations. The rectangular pictures are also described as boxes or bricks. |
| Door / gate | zi-ip → zi-ip | Royal support | Tentative, truncated legacy wording; requires the original dictionary page and contexts. |
| Seed | pa-ar → pa-ar | Descendants | Recorded metaphor; seed / offspring is not specific to Elamite, and a related sprout / offspring idea is already in the repo. |
| Staff / sceptre | ha-at-ti ≈ ha-ti | Affection | Only matches after folding consonant doubling; the sceptre entry has source cognate flag ḫaṭṭu. Not established homophony. |
| Cup / bowl | si-ir-ri ≈ si-ri | Ear(s) | Uncertain vessel interpretation, doubling normalization and late target sense. |
| Cup / bowl | si-ir-ri ≈ si-ri | True / correct | Same uncertainties and source family as cup / ear, not an independent confirmation. |

The two priority directions are **roof → protection** and **jar → enemy**, because their lexical steps can be stated explicitly. Priority is a research judgement, not a significance score or proof of an Indus reading. A valid dictionary bridge could still produce an implausible inscription. None of the surrounding sign sequences has been shown to read coherently in Elamite here.

## Dates and original-language evidence

- **Roof / protection:** HK:1021 gives Neo-Elamite roof literally and protection figuratively. N:1345 gives ku-uk “protection,” Middle / Neo-Elamite. This search has not established an early attestation of the literal picture word.
- **Jar / enemy:** N:888 gives pi-ti “jug,” Neo-Elamite; N:890 gives pi-ti-ir “enemy-SG,” Middle Elamite. N:889 separately gives Old Elamite bi-ti-ir. HK:338 calls pi-ti a vessel, perhaps jug, uncertain. Later attestation does not establish that the jug term existed in the mature Indus period, and a different spelling is not silently made an exact match.
- **Morphology:** [Basello2023, printed p.28 / PDF p.22](https://unora.unior.it/bitstream/11574/217200/1/basello2023introduction-elamite.pdf) analyses the animate noun-class endings -r and -p and explicitly uses enemy piti-r. [Badamchi2025, pp. 27–29](https://www.academia.edu/161289676/The_Old_Elamite_Treaty_A_complex_diplomatic_arrangement) discusses bi-ti-ir in the Naram-Sin treaty. These support the enemy word and its morphology; they do not independently attest the jug word or an Indus rebus.
- **Phonology:** Basello, pp. 19 and 27, discusses transcription conventions, competing sound analyses and possible stop contrasts. Folding b/p, d/t, g/k or consonant doubling is a search sensitivity, not an established historical sound law or proof of identical pronunciation.

The DigitalPasts source is pinned to [commit3160b20](https://github.com/DigitalPasts/ALP-MEGA2024/tree/3160b20f5cd84b387343d071749bb90419148743/Elamite_materials/EWB-EJSmithFiles). Its noun CSV row identifiers in our outputs include the header offset: N:888 corresponds to file line888. The legacy HK identifiers are the existing repo table’s IDs, not original dictionary page numbers. Both lexical resources derive from Hinz–Koch; agreement between them is not an independent ancient attestation. Raw glosses, warning flags, forms, periods and source identifiers are preserved in every candidate row.

## What is additional to the existing repo?

Cúper already implemented a broader multilingual picture-word search in `lang_m2`, including Elamite. We inspected its scripts and materialized evidence before extending it. Its Elamite output has ten witness rows representing three semantic directions: **house → negative**, **jar → lord** and **roof → his head**. Roof → protection and jar → enemy are absent from that output. Seed / offspring and hang / weigh already have related conceptual treatments elsewhere in the frozen pair recipes.

This extension removes the older destination-class keyword restriction, admits the structured English lexical hints alongside the full 2,452-row legacy table, searches all available picture nouns, and adds a separately labelled, source-supported noun-class-stem channel. Candidate publication is not gated on a language-family rank. It releases every witness and the negative source review, rather than only the attractive examples.

**Novelty is bounded to the inspected implementation and outputs.** The dictionary meanings are pre-existing. This is not a claim to be the first scholar to observe these Elamite senses or to have searched every historical document in the repo.

## Scope, normalization and selection

The [design record](OPEN_REBUS_PLAN.md) documents the initial scope and the later exploratory coverage/morphology repairs. No Cúper target meaning, Dravidian sound or archaeological outcome selects a destination. Existing meanings are consulted only for retrospective novelty annotations.

- **417 drawings inventoried:**320 have source two-/three-of-three picture labels; 97 abstract or unpictured drawings remain in the inventory rather than becoming failed words. Agreement is at drawing level; it does not establish every alternative noun. These are reused repo picture judgements, not new independent human assignments.
- **73 picture noun types; 24 have eligible lexical anchors.** This is broad within available data, not a complete Elamite vocabulary or exhaustive sign decipherment.
- **10,636 source rows considered:**8,184 common-vocabulary DigitalPasts rows plus 2,452 legacy rows. Filtering and sense splitting leave 7,498 eligible source rows / 9,754 sense records / 6,106 conservative normalized forms. None of these is an independent-root count.
- **680 witness rows:** 164 conservative whole-form, 14 permissive-key, six noun-class-stem and 496 one-edit. Synonyms, alternative senses, source repeats and grammatical forms create duplicates. **680 is not the number of valid rebuses.** All 184 non-near witnesses were reviewed at source-gloss level; the 496 near spellings have not received a complete philological review and are not promoted.
- Conservative normalization joins syllabic spelling, removes numerical sign indices and folds vowel length/repetition. It preserves consonant diacritics and doubled consonants. The permissive key additionally folds b/p, d/t, g/k and repeated consonants. No initial syllable, theme vowel or arbitrary substring is deleted.
- The morphology channel removes only final -r or -p when the structured record explicitly has terminal -SG or -PL respectively. Raw forms and the derivation remain visible. A separately flagged sensitivity removes initial dot-separated putative determinatives; compounds with internal dots remain excluded.
- One-edit search requires both normalized strings to have at least four letters and two consonants, plus the same initial-vowel status and first consonant. It generates leads, not a declaration of phonetic similarity.
- Unix English spelling checks affect review flags only. Missing a word list does not remove candidates; supply `--english-wordlist` to reproduce the local flags. Effective picture aliases and German translations are released in `open_rebus_picture_terms.json`.

Many lexical records already collide under normalization: 38.5% of sense records have another same-language head under the conservative key, 40.7% under the permissive key. These figures include polysemy, spelling duplicates, grammatical stripping and editorial noise. They are a warning about search flexibility, **not a chance-match p-value** or a measure of Elamite’s fit to the Indus script. No language-identification significance claim is made.

## Source traps kept out of the headline

- Gate / door, pillar / post and brick / baked brick are synonyms or paraphrases.
- House → negative is already an older Elamite candidate direction, even though new spelling witnesses do not trigger the exact-pair lookup.
- Cup → English “shale” conflicts with German *Schale* “bowl”; possible translation/annotation error, quarantined pending the original source.
- Door el → eye is explicitly a shortened **writing** for elt in the source; no identical spoken words established.
- “Man from Harku / Mimuras” is a gentilic or ethnonym, not the general word for man.
- Horn-people → herdsmen is a transparent derived expression, not a bare-word homonym.
- Possessed/plural house forms versus a truncated silver gloss, and house versus relatives interpretations, remain quarantined rather than being asserted as new rebuses.

## Connection to actual signs and next validation

The report shows real repo drawings, not invented sign shapes: roof example M77:135 / Lipi482; jar M77:342 / Lipi740; person with staff M77:25 / Lipi142; leaf/seed M77:373 / Lipi790. The crosswalk and the noun interpretations remain hypotheses. A word for a depicted component does not automatically name the whole compound sign. The rectangle M77:237 illustrates the door/box/brick ambiguity without assigning it a unique Lipi sign.

[3,560 sign–catalogue-face occurrence rows](results/open_rebus_example_sign_occurrences.csv) provide existing proposed readings and recorded findspots for those four representative Lipi signs. They are references across catalogues, not 3,560 distinct independent objects or Elamite translations. They were assembled after lexical discovery and have not been used to test semantic predictions.

For a meaningful next test: verify the literal words and dates from original passages, settle a sign-picture assignment independently, then freeze the candidate value and its encoding of any noun-class ending. Require it to predict surrounding signs or new archaeological evidence better than competing values. That independent prediction remains outstanding. The present result **adds explicit Elamite alternatives to test; it does not strengthen the Elamite–IVC hypothesis by a validated reading.**

## Reproduce and inspect

Run from this repository with Python and NumPy; raw source bytes are verified against the pinned Git blob IDs.

```sh
python3 research/independent_validation_20261120/elamite_validation/fetch_inputs.py --destination /tmp/ivc-elamite-inputs
python3 research/independent_validation_20261120/elamite_validation/open_rebus.py --source-dir /tmp/ivc-elamite-inputs
python3 research/independent_validation_20261120/elamite_validation/open_rebus_report.py
python3 research/independent_validation_20261120/elamite_validation/open_rebus_check.py
```

The HTML embeds the original sign drawings and works offline. Checks recover an unrestricted synthetic target and same-entry polysemy, distinguish whole-word/stem/permissive/near channels, guard suffix removal, retain source problems, verify provenance hashes and reconcile all 417 drawings,73 picture nouns and680 candidates. Runtime is recorded in the search summary; the discovery run took about four seconds locally. Colab units: 0. The standalone export is a viewing bundle; reproduction requires the repo’s picture, crosswalk, legacy dictionary and original source files.

Browser verification loaded eight illustrated cards and all 680 audit rows without script errors, missing local links or horizontal page overflow at desktop/mobile sizes. The search filter was exercised and the two-lead illustration visually inspected. To repeat with the catalogue’s existing Playwright installation and Chrome: `node research/independent_validation_20261120/elamite_validation/open_rebus_browser_check.mjs`. The generated `open_rebus_priority.png` is an export of the report’s two priority cards.
