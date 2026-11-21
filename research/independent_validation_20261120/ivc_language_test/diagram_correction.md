# Diagram correction: historical groups and actual English meanings

20 November 2026. The previous Venn grouped Kannada with Telugu, separated Kannada from Tamil/Malayalam, and showed only seven languages although the underlying analysis covered 22. That was a poor display for a historical-linguistic comparison. It has been withdrawn and replaced with a complete English-labelled subgroup chart and an atlas showing all 22 languages.

**The lexical judgments have not changed in this correction.** The existing 1,474-cell language/claim table retains SHA-256 `a1303637d398551ce2682e721394aa6829207c9a0d2989852076d2ad899f6f4b`. This is a correction of classification, aggregation and presentation, not a new demonstration of the Indus language.

## Correct display groups

The conventional classification in [Krishnamurti 2003, printed pp. 19–20](https://assets.cambridge.org/97805217/71115/sample/9780521771115ws.pdf) places **Kannada with Tamil/Malayalam in South I**, and **Telugu with Gondi, Kui and Kuvi in South II**. Kolami, Naiki/Naikri and Parji are Central. Only our studied varieties are listed below; these are not exhaustive branch membership lists.

| Display group | Studied varieties | Both meanings recorded, out of 48 | Same written form, out of 48 |
| --- | --- | ---: | ---: |
| South I | Tamil, Malayalam, Kannada, Tulu, Kota, Toda, Kodagu | 46 | 25 |
| South II / South-Central | Telugu, Gondi, Konda, Pengo, Manda, Kui, Kuwi | 18 | 1 |
| Central | Kolami, Naikri, Naiki, Parji, Gadaba | 2 | 0 |
| Kurukh–Malto | Kurukh, Malto | 2 | 0 |
| Brahui | Brahui | 0 | 0 |

Group membership means **one individual language supplies the whole connection**. The first meaning cannot be taken from one language and the second from another. A group total does not mean that every language in the group has every connection.

Kurukh–Malto and Brahui are conventionally called North Dravidian, but their unity as a distinct subgroup is debated. They are displayed separately rather than asserting a new tree. [Kobayashi 2020, pp. 467–468](https://gengo.l.u-tokyo.ac.jp/masatok/JAOS_140_2_Kobayashi.pdf). Kuwi is the source's spelling for Kuvi; Kodagu is also called Kodava. The source's Naiki and Naikri varieties are Central. Its Dravidian Gadaba records must not be confused with the Austroasiatic language Gutob, also called Gadaba.

Gondi, Kui and Kolami were **already included in the 22-language data**. They were inadequately represented by the old selected-language figure. The corrected atlas shows them explicitly.

## What were 45/48, 29/48 and 2/48 counting?

They were unions of **recorded two-sided meanings in the old display sets**, not 45, 29 and two established ancient readings, nor counts of identical-sounding words.

| Superseded set | Both meanings | Same written form |
| --- | ---: | ---: |
| Tamil / Malayalam | 45/48 | 25/48 |
| Kannada / Telugu | 29/48 | 7/48 |
| Brahui / Kurukh / Malto | 2/48 | 0/48 |

Those counts can be reproduced from the unchanged data, but the sets were inappropriate for historical subgroup comparison. The old `venn_regions.csv` is withdrawn; [superseded_group_audit.csv](results/superseded_group_audit.csv) preserves the correction transparently. [branch_summary.csv](results/branch_summary.csv) and [branch_overlap_regions.csv](results/branch_overlap_regions.csv) contain the corrected groups and every overlap region.

“Same written form” is a separate modern spelling check, not a reconstructed sound correspondence. Cognates can differ regularly in sound, so a failure of exact spelling is not proof against common ancestry. Conversely, belonging to a cited cognate family does not supply a missing second meaning.

## What are the actual proposed meanings?

Every chart row now spells these out: **fish picture → star**, **bow picture → sell**, **jar picture → house**, **spear picture → chief**, **line picture → tax**, and so on. These remain the proposal's English hypotheses. No knowledge of the sign catalogue is needed to read the rows.

Concrete examples in the unchanged matrix:

- **Fish → star:** both senses are documented within Tamil, Malayalam, Kannada, Kota, Toda and Malto. The Malto forms are different; modern exact-form matching is not the same result as meaning-family survival.
- **Sprout → infant:** Malto supplies the northern two-sided example. Brahui and Kurukh have sprouting vocabulary in the comparison but the checked records do not establish the infant meaning for those forms.
- **Carrying pole → guard** and **cage → assemble/store** are the two complete connections recorded in the Central group under the fixed family/sense rules.
- **Horn/tusk** is a single-meaning family documented in Tamil, Kurukh, Malto and Brahui. It is therefore visible in the 67-claim atlas, although it is not one of the 48 two-meaning pairs.
- **One** and **two** have their cited numeral meanings in all 22 varieties. Brahui also has the checked three family and a questioned inside comparison. Brahui's 0/48 does not mean it has no inherited Dravidian vocabulary.
- **Eye/sight** can be recorded without the proposed second meanings **weight/property** or **copper**. The atlas now distinguishes first-meaning-only from second-meaning-only records.

[The plain-English catalogue](semantics.md) gives every proposed meaning and the languages documenting both sides. [semantics_catalogue.csv](results/semantics_catalogue.csv) retains all source sense alternatives and cited etymological groups.

## Historical implication

The southern concentration remains visible after correcting the display. It does not locate the Indus language in a subgroup. The readings were developed using a Tamil-centered dictionary pool, and documentation differs substantially among languages. [Kolipakam et al. 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5882685/) explicitly discuss the concentration of DEDR coverage in the major literary languages and the difference between cognate-family history and same-meaning comparison.

The family's estimated age does not date each root, specialized administrative sense or picture-pun. This diagram reconstructs neither a Proto-Dravidian lexicon nor a phylogeny. Establishing ancestral vocabulary requires independently justified cognacy and sound correspondences; linking it to Indus requires independently supported sign meanings. Missing documentation is not proof of historical word loss.

## Verification

Checks verify all 22 varieties appear exactly once; Kannada/Tamil/Malayalam, Telugu/Gondi/Kui/Kuwi, and Kolami/Parji/Naiki/Naikri are assigned to the sourced groups; every group credit is supported within an individual language; every English meaning appears; all 67 claims and 48 connections are accounted for; set partitions reconcile; and the source lexical matrix is unchanged. Original font outlines are fitted within each row while preserving their aspect ratio, and the rendered charts were inspected for readability.
