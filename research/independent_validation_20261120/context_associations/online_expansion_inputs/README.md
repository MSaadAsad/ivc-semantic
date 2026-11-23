# Additional online animal and inscription sources

Retrieved 23 November 2026. Work and commits remain local while GitHub is off.

The raw public downloads are kept outside the repository in `work/online-expansion-20261123`. The factual source rows, source qualifications, original illustrations and existing-metadata subset here make the report rerunnable without new network requests.

- `animal2024_rows.csv` preserves worksheet rows 6–2380 of Bhaskar 2024 ESM13, including every original A–U field. Repeated IDs are not merged. Blank-ID continuation rows carry a separately labelled preceding row-group reference; they are not additional specimens. Ten named identifiers fail the strict CISI parser, including suffix-i forms and bare `1534`; no object IDs are invented for them.
- `animal2024_source_notes.csv` retains the workbook's legend, exclusions and grouped illegible references. These grouped references are not expanded into fabricated individual observations.
- `frontal33_review.csv` records the separate ESM1 illustrated rows after visual review of all six illustrated pages. The front-facing and above/behind signs are separate variables, not a forced linear reading. Mahadevan numbers are retained. Questions and PDF/workbook disagreements stay explicit; uncertainty is not silently removed.
- `existing_animal_metadata.csv` freezes relevant existing Lipi records for the identifier join. A source object's A–F panels are not automatically equated with numerical corpus faces. The crosswalk is at object-reference level.
- `images/` contains cropped image/reference table cells for the 33 illustrated cases, without reconstruction, and one unmodified embedded Binjor photograph from a secondary reproduction. Attribution and treatment are in `image_sources.csv`.
- `animal2022_named_records.csv`, `animal_version_changes.csv` and `animal_version_summary.json` preserve the baseline and source-version comparison. The public 2022 download matches the archived Git blob `680420e98c40c66ef3edcc9d115c821133760ccc` byte-for-byte. Normalize whitespace/zero padding for reference comparison while retaining suffixes; compare sets of common-field values per reference, not independent specimen counts. The new explicit sign-coding column has 32 populated named rows, and common labels change for 421 groups. The five unmatched illustrated objects were already listed in the older source.

Sources:

- Bhaskar 2024, *Markers and agencies of anisotropy in the Indus sign system*, [publisher page](https://link.springer.com/article/10.1007/s43539-023-00102-3), [ESM1 PDF](https://static-content.springer.com/esm/art%3A10.1007%2Fs43539-023-00102-3/MediaObjects/43539_2023_102_MOESM1_ESM.pdf), [ESM13 workbook](https://static-content.springer.com/esm/art%3A10.1007%2Fs43539-023-00102-3/MediaObjects/43539_2023_102_MOESM13_ESM.xlsx). The 2022 catalogue is already archived upstream; it is not a new source discovery here. The updated supplements are credited to their author, not presented as our iconographic discoveries.
- [Official ASI parliamentary answer, 19 July 2021](https://sansad.in/getFile/loksabhaquestions/annex/176/AU183.pdf?source=pqals): eleven Binjor seals in aggregate. It does not provide eleven inscription transcriptions.
- [Binjor photograph reproduction](https://faculty.fordham.edu/vinod/kalyanaraman2021.pdf), PDF p17, originally credited to S. Subramanium / Frontline excavation reporting. Only the photograph is used; the compiler's proposed Vedic and metalwork readings are not adopted. No exact accession/trench, normalized sign sequence or English translation is asserted.

The raw worksheet has 2,022 named rows and 353 continuation rows; the strict parser yields 2,002 distinct references. These counts are not forced to match the paper's headline of 2,023 animal-bearing objects. Preserve denominator differences and repeated entries. The source's 31 workbook F3 rows and the separate 33-object illustrated register are also not the same population.

Rebuild source extraction with `online_expansion_extract.py --cache PATH --metadata PATH`, then build the report using `online_expansion.py`. No workbook is modified or re-exported. XML extraction preserves source values; no phonetic or semantic hypothesis is fitted during import.
