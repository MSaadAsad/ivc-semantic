# Elamite words for unresolved Indus signs

23 November 2026. **The recipient language is unspecified.** We are looking for Elamite-derived readings that might fill gaps in the Indus script, potentially as borrowed terms. A matching modern Dravidian word is not required. These candidates might also occur under a wholly Elamite hypothesis; lexical matches alone do not distinguish that from borrowing.

[Open the sign illustrations and actual inscription examples](results/unread_elamite.html). [Six focused candidates](results/unread_focus_candidates.csv). [Complete unresolved-sign inventory](results/unread_Elamite_rebus_candidates.csv).

## Concrete candidates

| Unresolved sign | Proposed Elamite source | Actual context | Why investigate / main qualification |
|---|---|---|---|
| **362**, doorway with an inner rectangle, M77:201 | **hi-el / hu-el**, gate → royal court | **H-345**, Harappa: 362–740–090; existing proposed reading “Manager of the [362] house.” | An illustrative gap fill is **“Manager of the [court] house.”** The doorway has two first-choice votes and rank-one crosswalk share 1.0. Court is only a candidate; the neighbouring house/manager words and English syntax remain provisional. |
| **621**, partitioned rectangle, M77:242 | **hi-el / hu-el**, gate → royal court | **M-180**, Mohenjo-daro: 621–740. Other 621 texts frequently end in this sign. | Door has three first-choice votes and crosswalk share 0.833. Court is an institutional candidate for the slot. Older guesses already include stored / registrar-title; no new discovery of the slot itself is claimed. |
| **572**, door/arrow outline, M77:195 | **hi-el / hu-el**, gate → royal court | **H-1021**, Harappa: 368–572–741–235–740–090, with [572] still unresolved in its catalogue reading. | Door has two first-choice votes and crosswalk share 1.0. The arrow-like interior and longer compound/name context need analysis before assigning the whole sign a gate word. |
| **360**, gate/table outline, M77:202 | **hi-el / hu-el**, gate → royal court | **H-2217**, Harappa: 360–257; both catalogue values remain unknown. | Gate has two first-choice votes, crosswalk share 0.75. There is no full translation; the second sign remains unresolved. |
| **202**, doubled seed-like figure, M77:268 | **pa-ar**, seed → descendants/offspring | **H-183 / H-184**, Harappa: 920–220–892–202–400, ending in the existing proposed [202]–junior. | Seed has two first-choice votes and crosswalk share 1.0. The picture has two elements; the whole value, grammatical number and lexical dates have not been established. |
| **484**, hatched chevron, M77:136 | **ku-uk**, roof → protection | **H-2362**, Harappa: 484–400, existing proposed [484]–junior. | A weaker picture assignment: the first choices are ladder:2, abstract:1, with no first-choice roof vote. The literal roof sense is late in the available source. Kept as a possibility rather than a secure roof/protection reading. |

**362, 621, 572 and 360 are alternative places to investigate the gate/court word, not four simultaneously decoded signs.** Their different shapes and different contexts must be reconciled before assigning any shared sound or treating them as allographs. No form is chosen merely to make an English phrase sound good.

The source words are pre-existing dictionary entries: HK:1236/1270 give literal gate/portal and figurative royal court; HK:156 gives descendants, literally seed; HK:1021 gives literal roof and figurative protection. The structured English source corroborates protection (N:1345) and seed (N:314/441), but has shared Hinz–Koch ancestry rather than independent attestations. The court figurative senses in these cached glosses are Neo-/Achaemenid-Elamite, protection is Middle/Neo-Elamite and seed/descendants dates are unspecified. **An early enough word-and-sense attestation remains to be established for these prospective loans.**

## What was searched

The 711-row sign inventory contains 541 sign IDs outside the frozen 163-sign key after excluding IDs whose canonical allograph is already covered. “Unresolved” here means lacking a value in that phonetic key. It does not erase earlier source guesses, catalogue glosses, allograph studies or word-free role assignments.

The verified Elamite lexical pool and all 417 picture descriptions produce 473 automatic literal-anchor rows touching 66 unresolved sign IDs. These are raw dictionary witnesses; they include repeated forms, compounds, grammatical forms and known source ambiguities, not 473 independently recovered words. Applying the eight previously reviewed rebus directions yields 48 sign/direction/picture rows touching 25 unresolved IDs. Every lower-support mapping remains in the downloadable inventory. No Dravidian vocabulary is used to select these candidates.

[348 sign–catalogue-face occurrence rows](results/unread_candidate_occurrences.csv) retain both catalogues, original readings and recorded findspots. [Profiles](results/unread_candidate_profiles.csv) show unique formulas, initial/final positions and immediate neighbours. The catalogues and repeated formulas are not independent objects or experiments. This is retrospective descriptive context, not a fresh semantic validation.

The focused display favours a rank-one crosswalk share of at least 0.75 and two first-choice votes for the relevant pictured noun. This is an exploratory display rule, not a measure of independent semantic confidence. 484 is explicitly retained below that picture-evidence rule to show the distinction. Complex tree/jar signs and a cup held by a person are not automatically given a whole-sign reading from one component.

## What is additional to Cúper’s work?

Cúper's `lang_m2/units.csv` already lists 362 as house/door in a name-like slot, 484 as ladder/roof, 621 as a title after the jar and 202 as a number/person/name-start candidate. `key6a/trackA_per_sign_bridges.csv` already tests a Dravidian-oriented room/window-to-office/guard bridge for 621 without placing it in the final key. The sound-free reader supplies registrar-title and unanchored-name labels. Those structural questions are not new here.

The extension is **specific Elamite lexical alternatives applied to the unresolved phonetic inventory**, with source qualifications and every recorded context. The earlier Elamite discovery emphasized already-assigned 482/740; the present search moves to the user's requested gaps instead. It does not claim these words are established loans, new Elamite vocabulary or fully translated texts.

## What would make one a loanword candidate worth promoting?

For 362 or 621, first recover early gate/court attestations and verify the drawing against actual specimens. Compare court with the existing stored / registrar / name alternatives using a frozen prediction, then check inscriptions or independently recorded archaeological evidence excluded from selection. A court term should explain its contexts more specifically than a generic institution or personal name.

If a supported sign meaning and sound correspond to an Elamite word, test whether the surrounding Indus system is consistent with that being a borrowed term. The recipient could be Dravidian, another known family or an unidentified language. Borrowing does not require that the word survive in modern Dravidian. Conversely, a lone Elamite dictionary match cannot establish borrowing, donor direction, a recipient language or an entire Elamite inscription.

The user's separate comparison question is retained with its limits: the old selected 48-pair lexical checks give Dravidian stronger conditional results, while broader word-free/picture-led tests do not identify a language. That does not turn the current unresolved-sign search into an Elamite-versus-Dravidian vocabulary contest or supply numeric language odds.

## Reproduce

```sh
python3 research/independent_validation_20261120/elamite_validation/unread_elamite.py
python3 research/independent_validation_20261120/elamite_validation/check_unread_elamite.py
```

Requires the previously verified Elamite source cache at `../elamite-sources` relative to the checkout, plus the repo's sign pictures, crosswalk, current key and catalogue. The default path is resolved by the code from the checkout; no external recipient-language dictionary is read. Runtime about 10s locally; Colab units: 0. [Full summary](results/unread_Elamite_summary.json). The browser report is self-contained apart from its downloadable links.

The earlier [modern-Dravidian portability appendix](PORTABILITY_SCOPE_CORRECTION.md) addresses a different question and is not used to identify or reject these possible loans.

Browser verification loaded all six cards and sign drawings with no script errors, missing local links or page overflow at desktop/mobile sizes. The desktop preview was visually inspected. Repeat using `node research/independent_validation_20261120/elamite_validation/unread_browser_check.mjs`; pass the export directory as its optional argument.
