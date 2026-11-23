# Frozen source inputs

- `dholavira2015_register.csv`: factual specimen fields extracted from Bisht 2015, §8.2.4, printed pp 309–329, using the public report viewer. Viewer pages 327–347 correspond to printed pages 309–329. All 61 numbered entries are retained. Duplicate accession 43884 is not repaired or merged.
- `dholavira_observations.csv`: individually reviewed, paraphrased reverse-side observations and qualified attachment interpretations for those 61 entries. An unmarked back is not automatically a token; textile traces do not identify stored commodities.
- `other_fastening_records.csv`: four named observations from the public text of the preliminary 2016 presentation by Frenez, Prabhakar and Bisht. Their specimen figures were not recovered, and no signs are transcribed from them.
- `existing_catalogue_subset.csv`: the 252 existing Lipi metadata faces at Dholavira, Gola Dhoro (Bagasra) and Shikarpur, frozen from the source metadata used by the continuation. Object and face counts remain distinct.

Source URLs are included in the source tables. Public report HTML/page caches remain outside the repository; no full report text is redistributed. The misleadingly named AncientPortsAntiques Dholavira-Bisht2015 PDF is secondary commentary and is excluded from the primary register and decipherments.

`western_sites.py` reruns the candidate crosswalk from these inputs and the existing translation catalogue. `western_sites_extract.py --page-cache PATH --metadata PATH` rebuilds the factual register and metadata subset if the original cached public viewer pages and metadata CSV are available. The extraction does not generate new sign readings. Retrieval and source review: 23 November 2026.
