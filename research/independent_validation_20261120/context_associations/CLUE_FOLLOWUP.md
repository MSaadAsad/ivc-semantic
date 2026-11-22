# Which material and findspot clues did Cuuper already consider?

**Most broad clues were already considered. The clearest additional lead is a published set of inscribed gold bead-caps that has not been identified in the current gold-object inventory.** The other useful extension is to obtain actual object masses and source-specific context, rather than count a guessed reading's original material clue again as confirmation.

Scope: the current upstream `work` branch was checked on 2026-11-21 against `727dfd411a4faa44d193d204757540d45c7b139b`; GitHub reports them identical. The inventories below cover all 9,252 catalogue observations, separating Lipi objects from paired catalogue records. Prior-work searches cover the materialized original scripts/reports plus targeted GitHub code searches. GitHub search returns older indexed files; absence from those searches is not proof that Cuuper never thought about something.

## Already considered versus still open

| Clue | Existing work | What remains worth doing |
|---|---|---|
| “Gold weight” on gold M-2129 | Explicitly used in choosing sign 645's reading in `sound_v3_c.py:14` and `sound_v3_report_tail.md:15`. | Treat the object as a selection clue. Test a prediction on other evidence. |
| Proposed gold-weight sign concentrated near gold hoards | `sound_v5_job2.py` tested DK-area concentration: 10/13 versus 70% baseline, p=.42. It also tested numbers two positions away: 5/43 versus 10.9%, p=.51. `jobs/out/sound_list_v5.md` records both. | Exact hoard membership could be more informative than the very broad DK area, if original inventory numbers can be linked reliably. |
| Numbers and a proposed weight-unit function | Later `met_01_ladder.py`, `met_02_multiface.py`, and `metrology_ledger.md` already examine numeral series, count direction, unit relationships and cross-face equations. | “It takes numbers” has already been investigated. A direct measured-mass prediction for this gold object is a different, narrower claim. |
| Physical checks on artefacts | `met_03_physical.py` studies sherd thickness, vessel capacity, dimensions and estimates copper-tool masses from volume/density. | The exported M-2128/M-2129 rows contain no measured masses. Do not present an actual gold-mass test as already completed. |
| Cloth/cotton signs on textile tools and in textile areas | `cotton_2_whorls.py`, `cotton_house.md`, `beads_cotton.md` and the semantic-anchor scripts already investigate these. The report says a second whorl site did not validate 390 and reports failed thread/cloth predictions. | Independent identification of actual textile tools/deposits and residue or fibre evidence, followed by predictions fixed before checking the inscriptions. Broad textile associations are not an untested idea. |
| Sealing backs as evidence of packaging | `stamps_6_backs.py` and `backs_seen.csv` already inspect box, cord, possible cloth/sack and reed impressions, with count-line tests. | Direct, independently coded textile impressions could refine this, but “look at sealing backs” alone is not new. |
| Copper tablets, sign 407 and animal motifs | May 31 sign-control reports plus `copper_2_pairs.py`, `met_02_multiface.py`, `sem_02_anchors.py` and the new 845 follow-up already address these. | New specimen contexts or a new discriminating prediction are needed; another raw copper association repeats old work. |
| Same-room seals sharing signs | `research/extensions_20261117/findspot_room/REPORT.md` already compares room, depth and middle versus terminal signs; `stamps.md` follows seal/impression circulation. | Do not relabel a repeated-room example as a first room test. |
| C-87 specifically | Earlier sound-list evidence includes C-87. The archive's `risky_740405_c87_exception_adjudication_20260531.json` treats it as an intact two-sign exception in a formula test. | Its exact archaeological workshop crosswalk needs separate checking. Being mentioned in a formula test does not establish a textile interpretation. |
| Sign 690 on tablets and its neighbours | `key4b_bootstrap_wave2.md` already reports 4.11x tablet enrichment in Lipi and 0.96x (3/25) in New. `sound_v3_a.py:38` tests a following 740; `sound_v3_values.py:30` reports 10/20 versus 10.2%. `decoy_replay_A.py` tests preceding 435/436; registry scripts also test 690 as a linker. | A generic before/after-sign check is not new. A Sumerian-kad-specific grammatical comparison would need a separately defined attested construction and discriminating predictions. No such new comparison was run here, and the loanword is not established. |
| Inscribed gold bead-caps, their signs and possible shared engraving hand | No analysis of these identified in the inspected original scripts/reports or targeted indexed searches. | Recover photographs, museum numbers and transcriptions; match them to the corpus before claiming expansion or predicting meanings. |

## The strongest source lead: the gold hoard is more than two inscriptions

Kenoyer and Miller describe two inscribed pendants and two inscribed bead-caps from one DK-E jewellery hoard. The cap marks repeat; they also observe similar engraving and suggest ownership as a possibility. This supplies an alternative to weight labels and a concrete source-recovery target. Their third pendant was unexamined in that study; its present inscription status is not established here. [Primary examination, 1999, p.134 / PDF p.28](https://www.harappa.com/sites/default/files/pdf/Kenoyer1999_Metal%20Technologies%20of%20the%20Indus%20Valley%20Tradition.pdf#page=28).

Our catalogue has only **two records explicitly labelled Gold**, M-2128 and M-2129. Both have E2044-related excavation strings, consistent with a shared hoard route, but museum-number crosswalks must be recovered before identifying every publication specimen. No bead-cap row has been identified as gold. A cap could be present under unknown material or a different catalogue number. **No additional accepted inscription or translation has been added.**

Useful test after source recovery: compare the cap mark with the pendant inscriptions and other objects from the same hoard. A recurring mark might identify an owner, maker, pair or commodity. Each rival makes different predictions about which objects should share it. Keep all objects from one hoard together when withholding evidence; they are not independent archaeological contexts.

## Additional study incorporated: one specific tablet-production assemblage

The [new archaeological evidence table](results/archaeology.html) joins Kenoyer's 2005 Figure 3 and Figure 4 accession numbers to **16 existing inscribed objects / 25 faces**. Two blank tablets and a figurine are retained as unmatched source controls, not added as inscriptions.

The source groups H-2076, H-2077, H-2078 and H-2079 as partly inscribed examples of the same inscription. The catalogue has three observed sequences across those four objects. Two are already marked non-intact, so this is a newly recorded production relationship, not a demonstrated flaw in intact-only tests. A separate reported mould/product candidate joins H-2191 to H-1912; both corresponding faces contain 700–033, currently proposed “3 measures”. The exact unit remains unresolved. [Primary source, discussion and figures](https://www.harappa.com/sites/default/files/pdf/Kenoyer%202005%20Faience%20Workshop.pdf#page=3).

Cuuper's `twins.md` and `hands_1b_tally.py` already examine unfinished seals and engraving hands generally. That is prior work. No specific accession-linked analysis of this four-tablet group or reported mould/product pair was identified in the inspected scripts/reports and targeted searches. Adding these production relations does not constitute a new statistical test or an independent decipherment.

The raw `IMPL` category in our table should also not silently determine function: the independent source describes jewellery pendants. Raw catalogue type and source-supported artefact interpretation need separate fields. “Inscribed gold object” does not itself mean an implement or a physical balance weight.

## A direct physical test that remains unperformed here

For M-2129, obtain a reliable measured mass and establish what the written seven modifies. The specific hypothesis “this inscription records this object's own gold mass” then predicts a numerical relation. It is narrower than “645 is a weight term”: an inscription could instead record a person's name, a transaction or a quantity of another object. Do not use a later Tamil weight or an adjustable multiplier to manufacture agreement.

The existing physical export gives M-2129 dimensions 46.0 by 16.8 mm, with no thickness or mass; M-2128's dimensions are blank. These are recorded fields, not a mass measurement. The current data cannot execute the direct weighing test.

## Two further clues that need interpretation, not another translation claim

- **Unknown sign 898 is not confined to the gold pendant.** All four Lipi objects containing it are released: gold M-2129, clay object H-1011 with 898 alone, Harappa tablet H-211, and steatite seal M-154. H-1011 had already appeared in Cuuper's textile-tool candidate inspection, without solving 898. This gives actual comparison objects for identifying a mark or name element. It does not determine its meaning or prove what seven counts on M-2129.
- **C-87 and C-22 share catalogue locus 215, square 9/D.** The existing source check links that locus with jewellery manufacture and weighing. Their proposed readings differ: C-87 is “Of the Weave/Cloth House”; C-22 includes proposed gem/cotton/received values. C-87's recorded elevation is +9.5 ft and C-22's is +10.4 ft. The association is a source-check queue, not proof of the same depositional event or a textile workshop. Blind functional assignment must distinguish jewellery production, textile production, storage and general trade. [Earlier source check and exact limits](results/COPPER_845.md).

## Reproduce and inspect

Run `python research/independent_validation_20261120/context_associations/clue_followup.py`.

- [Both gold objects](results/clue_followup/all_gold_records.csv)
- [All 26 Lipi objects with proposed gold-weight sign 645](results/clue_followup/all_645_records.csv)
- [All four Lipi objects with unknown sign 898](results/clue_followup/all_898_records.csv)
- [Both catalogue objects from Chanhu-daro locus 215](results/clue_followup/workshop_locus_215_records.csv)
- [Original physical fields for the gold objects](results/clue_followup/gold_physical_fields.csv)
- [Prior-source search matches](results/clue_followup/prior_source_matches.csv)
- [Counts and scope limits](results/clue_followup/summary.json)

This follow-up adds source leads and a reproducible inventory. It runs no new significance tests and establishes no new sign meaning. No Colab units used.
