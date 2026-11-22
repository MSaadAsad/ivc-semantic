# Primary residue-data sources

These files support an object-identification feasibility check, not a completed decipherment test. Source sample IDs are laboratory/study identifiers unless an independent archaeological crosswalk is supplied. Existing sign labels were already frozen before this work; the present matching was not blind to the published chemical results.

## Kotada Bhadli, 2020

Chakraborty, Slater, Miller, Shirvalkar and Rawat, *Compound specific isotope analysis of lipid residues provides the earliest direct evidence of dairy product processing in South Asia*, Scientific Reports 10, 16095. DOI: 10.1038/s41598-020-72963-y.

- [Main paper](https://www.nature.com/articles/s41598-020-72963-y.pdf).
- [Supplementary document](https://media.springernature.com/full/springer-static/esm/art%3A10.1038%2Fs41598-020-72963-y/MediaObjects/41598_2020_72963_MOESM1_ESM.docx).
- Input `kotada2020_tableS1.csv`: all 59 entries from the first supplementary table, retaining authors' tentative interpretations. Figure and chemical results do not establish an inscription match. Source is open access under CC BY 4.0; sample facts are attributed here.

## Northwest India, 2021

Suryanarayan et al., *Lipid residues in pottery from the Indus Civilisation in northwest India*, Journal of Archaeological Science 125, 105291. DOI: 10.1016/j.jas.2020.105291 (online 2020).

- [Author-deposited published paper](https://eprints.whiterose.ac.uk/id/eprint/168890/7/1_s2.0_S0305440320302120_main.pdf).
- [Official dataset and licence](https://www.repository.cam.ac.uk/items/2a3c9cb0-5a81-49ac-afb2-0c567f9024ea), DOI 10.17863/CAM.54273.
- [Original data.csv](https://www.repository.cam.ac.uk/bitstreams/a312d55c-48f4-4c08-9c63-ce3bbd834d54/download).
- Input `northwest2021_original_data.csv` is preserved unchanged with attribution; the repository declares CC BY-NC 4.0. It contains **124 rows: 122 archaeological samples plus two modern references**. The main paper reports 172 analysed fragments; the downloaded CSV is not a 172-row complete sample register.
- [Recovered 42-page vessel-image supplement SI3](https://www.repository.cam.ac.uk/bitstreams/83b1b0f1-7620-4eba-956c-c7434b03426a/download), hidden on the repository's second file-list page. Table S15 (PDF pp.39–42) supplies **49 low-yield sample IDs**, retained in `northwest2021_SI3_low_yield_IDs.csv`. The difference from the paper's total is 50; one entry remains unreconciled. No 50th ID or result is invented. SI3 text contains no inscription/graffiti annotation; this does not prove every photographed vessel is uninscribed.

## Northern Gujarat, 2022

García-Granero et al., *Integrating Lipid and Starch Grain Analyses From Pottery Vessels to Explore Prehistoric Foodways in Northern Gujarat, India*, Frontiers in Ecology and Evolution 10, 840199. DOI: 10.3389/fevo.2022.840199.

- [Full article and Table 2](https://www.frontiersin.org/journals/ecology-and-evolution/articles/10.3389/fevo.2022.840199/full).
- Input `gujarat2022_table2.csv`: all 28 vessel rows from Table 2, including reported starch counts. Site heading rows, totals and ubiquity percentages are not vessels. Detailed Supplementary Table 1 was not recovered; the main text describes sample selection and vessel portions. Article is open access under CC BY.

## Additional literature checked, excluded from the pooled sample inventory

- Suryanarayan, Akshyeta (2019), *What's cooking in the Indus Civilisation? Investigating Indus food through ceramic lipid residue analysis*, doctoral thesis, University of Cambridge. [Repository record](https://www.repository.cam.ac.uk/items/a75679a0-c5cf-42a0-81a5-3d3b08aa4d31), [public thesis PDF](https://api.repository.cam.ac.uk/server/api/core/bitstreams/515b5736-fa26-4c70-9ffb-7d5e9292221b/content). Section 5.1.1 (printed pp.128–129 / PDF pp.162–163) describes uncertain-provenance teaching-collection samples. Tables 5.2–5.3 and 6.1–6.2 list five Kalibangan-labelled and five Mohenjo-daro-labelled sherds; Appendix B has photographs. These ten are inventoried separately in `thesis2019_groupI.csv`; no museum/excavation crosswalk or commodity identity is supplied here. Much of the thesis's other material overlaps later publications and is not pooled again. Printed p.132 identifies MD samples; p.335 / PDF p.371 supplies their images. Kalibangan quantitative values are not imported because Tables 6.1 and F.1 differ in sample/yield assignments; this is retained as source uncertainty, not corrected by guessing.

- Bourgeois and Gouin (1995), *Résultats d'une analyse de traces organiques fossiles dans une « faisselle » harappéenne*, Paléorient 21(1), 125–128, DOI 10.3406/paleo.1995.4613. [Primary article/first-page text](https://www.persee.fr/doc/paleo_0153-9345_1995_num_21_1_4613). A Nausharo perforated-vessel fragment is described; no specimen-to-inscription crosswalk was recovered in the inspected material. The full article was not retrieved. Do not pool this as an inscription-labelled dairy object or treat the older fatty-acid interpretation as a modern species-specific identification.
- Ghosh et al., *Does form entail function? Understanding pottery functionalities through absorbed residues within ceramics from the Harappan sites of Karanpura and Ropar in India*, DOI 10.1016/j.qeh.2024.100050. Publication metadata and abstract references located; full sample tables were not retrieved, so no sample count or inscription linkage is asserted here. Ropar is the site also called Rupar in our catalogue. This is a follow-up source route, not a completed review.

## Scope and chemistry

Starch observations can provide cereal/pulse evidence; broad lipid/isotope categories do not identify sesame specifically. Lack of a detectable plant signal is not proof that a plant was never present. A written commodity may also be an owner/name element or refer to a transaction; a contents prediction must specify its grammatical and object-use assumptions before being scored.

Public files were retrieved on 2026-11-21. Raw research PDFs and transient web pages remain local scratch files rather than being republished. `prepare_inputs.py` recreates the source-table extracts from those downloads.
