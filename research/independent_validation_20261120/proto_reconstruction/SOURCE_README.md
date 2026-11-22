# The Dravidian Database — version 1.2

**Reconstructed lexicon of the Dravidian subgroups linked to the Dravidian Etymological Dictionary**

Creators: Louis L. Merriam (ORCID 0009-0004-1734-8019) and Andreas Fuls
License: CC BY 4.0 · Web interface: https://dravidiandb.com/dravi/index.htm
Versions: v1.0 (2026-07-18, 10.5281/zenodo.21433491) · v1.1 (2026-09-03, 10.5281/zenodo.22286173) · v1.2 (this record) · all versions: 10.5281/zenodo.21433490

Version 1.2 completes the response to peer review of the accompanying data paper (*Journal of Open Humanities Data*, under revision). Relative to v1.1 it (1) re-imports Starostin's six StarLing reconstruction databases in full, from a fresh crawl (2026-09-05; record counts identical to the 2026-08-29/30 crawl), at database granularity — one record per StarLing entry, each carrying Starostin's own proto-language label — and removes the version 1.0 batch, whose records had been collapsed to one per root and labelled by attestation rather than by source (122 of his Gondi-Kui forms had thereby been labelled South Dravidian II, 611 South Total Dravidian and 6 Northern Dravidian, none of which are his nodes); (2) requires attestation in both Telugu and Gondi-Kui for South Dravidian II in the evidence-based classification, assessing Telugu-only support at Proto-Telugu; (3) regenerates the CLDF package and the SQL dump from the final tables (the v1.1 CLDF package predated the final v1.1 table); (4) deposits the re-import, CLDF, SQL and paper-figures scripts so that every number in the data paper is produced by the deposited code.

Relative to v1.0, versions 1.1 and 1.2 together (a) re-extract the DEDR from the DSAL digital edition, recovering 6,302 language-blocks / 12,156 lemmata lost in the 2025 extraction; (b) import Starostin's databases in full and retain them side by side with Krishnamurti's and the author's forms; (c) add a Gondi-Kui level and give every reconstruction two levels — the one its source claims and a mechanically computed evidence-based one; (d) add a CLDF distribution with Glottolog codes; (e) deposit the processing pipeline and a SQL dump.

## Files

| File | Rows | Description |
|---|---|---|
| `pdr_04.csv` | 15,629 | Reconstruction records, all sources side by side (schema below) |
| `dedr_entry_v11.csv` | 72,091 | Attested lemmata: one row per lemma, with language, form, simplified form, gloss, provenance (unchanged from v1.1) |
| `dedr_entry_raw_v11.csv` | 54,506 | Language-level DEDR blocks as extracted (both extraction generations; unchanged from v1.1) |
| `cldf/` | 86,989 forms | CLDF Wordlist (`Wordlist-metadata.json`, `forms.csv`, `languages.csv`, `parameters.csv`, `cognates.csv`), validated with pycldf |
| `dravidian_db_v1.2.sql.gz` | 142,584 | MariaDB/MySQL dump (utf8mb4) of the three tables above, with keys on DEDR number and classification |
| `classify.py` | — | Recomputes `evidence_classification` / `evidence_verdict` from the two CSVs and verifies the shipped columns |
| `pipeline/` | — | Crawl, import, build and verification scripts (see *Reproducibility*) |

All CSVs are UTF-8 with a header row; the SQL dump contains the same three tables. Load it with
`gunzip -c dravidian_db_v1.2.sql.gz | mysql -u USER -p DBNAME`. The v1.0 and v1.1 files remain available under their own DOIs.

## `pdr_04.csv` — reconstructions

| Column | Meaning |
|---|---|
| `id_pdr` | Record ID |
| `number` | DEDR etymon number the record is linked to (empty for 122 records — 116 of Starostin's and 6 of Krishnamurti's — whose root could not be linked to a DEDR etymon) |
| `source_classification` | The level the record is reconstructed at: the level of the StarLing database it comes from for Starostin's records (see the mapping below), Krishnamurti's own level for his, the author's assignment for his own. Starostin's layered reconstructions keep their structure — where he gives, say, Proto-Dravidian, Proto-South Dravidian and Proto-Telugu forms of one root, each is a record at its own level |
| `note` | Source label as written by the source (e.g. `Starostin: Proto-Gondi-Kui (Gondwan)`) or derivational note |
| `reconstruction` | Reconstructed form (scholarly transcription, no leading asterisk) |
| `simplified` | Search form: diacritics removed; d→t, c→s, w→v, z→s; ǯ written ʒ; ŋ and ʒ kept; geminates reduced |
| `meaning` | English gloss(es) — the source's own gloss |
| `reference` | `Starostin, 2006-2013` (12,868) · `Krishnamurti, 2003` (891) · `Merriam, 2025` (1,672) · `Merriam, 2025 (after Starostin, 2006-2013)` (author's emendation of a Starostin Gondi-Kui form; 198) |
| `classification_basis` | Subgroups attesting the etymon in the DEDR, e.g. `SDI+Te+GK+CD` (units: SDI, Te, GK, CD, KM, Br), or a flag: `no DEDR link (source-assigned level)`, `DEDR entry not found in digitized data`, `manual-review: …` |
| `evidence_classification` | The deepest node **within the record's own subgroup** that the DEDR attestation supports. Attestation is restricted to the daughters of `source_classification` before the last common ancestor is taken, so a Proto-Telugu form of a family-wide etymon is assessed against Telugu, not against the whole family. Comparing the two columns shows whether a source's claimed level is matched, exceeded, or unsupported by the DEDR evidence |
| `evidence_verdict` | `supported at level` (14,425) · `supported only at <node>` (941) · `unattested within subgroup` (97) · `no attestation data` (166). Of the 15,463 records with attestation data, 93.3% are supported at the level their source claims; the author's records agree in 1,864 of 1,865 cases (the exception is a South Dravidian II form now assessed at Proto-Telugu under the v1.2 rule) |

Starostin's databases and their levels: `dravet` (Proto-Dravidian) → Proto-Dravidian, 2,211 records · `sdret` (Proto-South Dravidian) → South Dravidian I, 3,885 · `telet` (Proto-Telugu) → Proto-Telugu, 2,836 · `kogaet` (Proto-Kolami-Gadba) → Central Dravidian, 1,509 · `gndet` (Proto-Gondi-Kui, "Gondwan") → Gondi-Kui, 1,439 · `ndret` (Proto-North-Dravidian: Kurukh and Malto) → Kurukh-Malto Dravidian, 988. Of the 13,615 StarLing entries, 807 Proto-South Dravidian entries and one Proto-North-Dravidian entry list daughter forms without a reconstructed proto-form and were not imported as reconstructions (version 1.0 had imported some of these daughter forms as if they were reconstructions); 62 entries that cite two DEDR numbers are recorded once under each; one entry longer than 60 characters was skipped. No record credited to Starostin carries the South Dravidian II, South Total Dravidian or Northern Dravidian labels, which are not nodes of his classification.

Proto-language labels: Proto-Dravidian · South Total Dravidian (= Krishnamurti's "South Dravidian", i.e. SDI + SDII; the label avoids confusion with Starostin's "South Dravidian", which is SDI) · South Dravidian I · South Dravidian II (etyma attested in both Telugu and Gondi-Kui) · Gondi-Kui · Proto-Telugu (Starostin only) · Central Dravidian (Kolami, Naikri, Parji, Gadaba) · Kurukh-Malto Dravidian (Starostin's "North Dravidian") · Northern Dravidian (Brahui, alone or with Kurukh-Malto).

## `dedr_entry_v11.csv` — attested lemmata

`entry_id`, `source_entry_id` (→ `dedr_entry_raw_v11.entry_id`), `lemma_ord`, `dedr_index_id` (DEDR number; ≥100000 = appendix), `lang_str`, `entry_str` (form), `simplified`, `entry_meaning`, `provenance` (`original-2025` | `dsal-recovery-2026`). Rows with `lang_str = PDr.` are the DEDR's own occasional proto-forms (731 rows); they are excluded from the CLDF forms table because the reconstruction table supersedes them.

Languages (26): Tamil, Malayalam, Kannada, Tulu, Kota, Toda, Kodagu, Koraga, Irula, Betta Kurumba, Alu Kurumba, Belari, Telugu, Gondi, Konda, Kui, Kuwi, Pengo, Manda, Kolami, Naikri, Parji, Gadaba, Kurux, Malto, Brahui.

## CLDF package

`cldf/` is a CLDF 1.x Wordlist generated from the two tables by `pipeline/build_cldf.py`: every attested lemma (71,360) and every reconstruction (15,629) is a row in `forms.csv`; the 26 modern languages carry Glottocodes in `languages.csv` and each proto-language is a language in its own right; DEDR etyma are the parameters and the cognate sets (`cognates.csv`: 86,867 rows in 5,627 cognate sets; the 122 unlinked reconstructions carry private `nolink` parameters and no cognate-set row). Validate with `cldf validate cldf/Wordlist-metadata.json`.

## Reproducibility

`pipeline/crawl_dsal.js` and `pipeline/crawl_starling.js` are browser-console scripts that fetch the DSAL DEDR pages and the StarLing databases and save them as text. `pipeline/dsal_parse.py` turns the DEDR crawl into language-blocks and lemma rows (the v1.1 recovery step). `pipeline/starling_reimport.py` builds the whole Starostin set from the StarLing crawl and the v1.1 table (`python pipeline/starling_reimport.py starostin_dravidian_crawl.txt pdr_04_v11.csv dedr_entry_v11.csv`): one record per StarLing entry, linked to DEDR numbers through the entry's own "Number in DED" field (9,145 records), otherwise by voting among its daughter reconstructions looked up in the sub-branch databases (3,506), the DEDR number the same form carried in v1.1 (65) or the author's emended Gondi-Kui forms (13); 116 could not be linked. `pipeline/starling_import.py` is the v1.1 importer, kept for the parsing functions the re-import reuses. `classify.py` recomputes `evidence_classification` and `evidence_verdict` for every record and exits nonzero on any mismatch with the shipped columns (`python classify.py pdr_04.csv dedr_entry_v11.csv`; add `--write out.csv` to regenerate them); it also re-derives `classification_basis` and reports any disagreement — the shipped file has none. `pipeline/build_cldf.py` and `pipeline/build_sql.py` regenerate the CLDF package and the SQL dump; `pipeline/paper_numbers.py` prints every figure quoted in the data paper from the deposited files. The scripts were implemented by an AI assistant (Claude, Anthropic) under the author's direction; the DEDR crawl was run on 2026-08-29 and the StarLing crawl used here on 2026-09-05.

## Known limitations

The dataset inherits the DEDR's coverage and editorial decisions: reconstruction records exist for 5,085 of its 5,557 main etyma, the remainder being etyma for which none of the three sources offers a proto-form (typically entries that Starostin groups without reconstructing). Reconstructions differ in confidence by source and by attestation — consult `reference` and `classification_basis`. 122 records (0.8%) have no DEDR link; 5 are flagged for manual review. In 97 records (0.6%, 94 of them Starostin's) the subgroup reconstructed is not attested in the linked DEDR entry, because Starostin's subgroup databases draw on language data the DEDR does not record under that etymon; these carry `evidence_verdict = unattested within subgroup` and should be treated as source-attested only. The simplified forms are a search aid, not a phonological claim.

## How to cite

Merriam, L. L., & Fuls, A. (2026). *The Dravidian Database: Reconstructed lexicon of the Dravidian subgroups linked to the Dravidian Etymological Dictionary* (Version 1.2) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.21433490

Sources: Burrow & Emeneau (1984) *A Dravidian etymological dictionary*, 2nd ed., Clarendon (digital edition: DSAL, University of Chicago) · Krishnamurti (2003) *The Dravidian languages*, CUP · Starostin (2006–2013) *Dravidian etymological database*, StarLing · Southworth (2005) *Linguistic archaeology of South Asia*, RoutledgeCurzon.
