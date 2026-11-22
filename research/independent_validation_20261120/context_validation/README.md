# Exact archaeological contexts and the existing proposed readings

Added 22 November 2026. **Thirty existing objects now have accession-linked source annotations**, including eleven Harappa objects assigned to three named rooms in one house and all six catalogue objects from Bagasra. The [searchable report](results/contexts.html) shows every complete proposed reading beside the location, deposit and archaeological qualification. This is source expansion and comparison material; zero independent semantic validation tests were run.

## What the additional evidence says

| Find group | Actual existing proposed readings | Archaeological evidence and implication |
|---|---|---|
| Harappa AreaC, Room1 | H-1664: **“3 Woven-Cloths”**; terracotta cone H-2559 remains unread/unassigned. | Domestic-debris pits and a small **kiln or oven**, in a room opening to the street. A cloth reading does not turn the room into a textile workshop. |
| Same house, Room2 | H-2186 face1: **“2 measures”**; face2: **“Weave/Cloth Guard/Porter 4 Woven-Cloths.”** Seal fragment H-1681: **“two quarters: Two; [lost sign].”** | Two objects in a room whose floor debris/fill contained inscribed finds. The measure and cloth proposals occur together in a household assemblage, but craft function and the readings remain unverified. |
| Same house, Room3 | Measures3–4, proposed junior/lord and house/keeper formulas; H-1869 and H-1868 repeat **“4 measures” / “Keeper of the Bracketed-Star House.”** | Seven objects, several moulded tokens. Repeated formulas/copies are dependent evidence. All eleven objects in the three rooms belong to **one house**, not eleven independent workshops. |
| Bagasra, SE corner near faience/lithic activity | BSR2037: **“5, Guard/Keeper (*kā)”**. BSR8288: **“[322]-Moon-First-ward-Hunter-[352]-[292].”** Current key instead glosses its assigned signs as **ration, month/moon, single-house, merchant**, leaving352/292 unassigned. | Reported at100/105cm near the same activity area; one vicinity cluster. These are administrative-looking proposals, not an explicit independently verified name for faience. The two reading versions are preserved rather than silently reconciled. Neither seal is securely assigned to an Eq2 workshop-use floor. |
| Bagasra shell area | BSR6952: **“[lost sign]-[lost sign]-[lost sign].”** BSR5555 has no preserved inscription and no catalogue match. | The shell-production association is useful archaeology, but **neither fragment supplies a readable inscription** with which to test “bangle.” |
| Bagasra gateway | BSR7368: **“share: [893]-Lady-[236].”** BSR7197 has a longer proposed chief formula, retained in full in the report. | A sealed pit at223cm and a likely secondary deposit at26cm, respectively. Same trench does not establish the same deposit or use episode. |
| Rakhigarhi RGR6304 | **“two shares: Home-High-star.”** Current key differs: share,2,millet/grain,rayed-star. | Independently reported on **RGR-2**, in Mature Harappan levels. The bead factory with two elephant sealings is on **RGR-1**. The exact accession join does not put this unicorn seal in that factory. |

The household’s cloth proposals are an interesting lead for future non-script evidence. They are not independent confirmation of textile manufacture. The same applies to possible administrative readings near faience production: many unrelated administrative meanings could fit such a location. No semantic success/failure score is assigned after seeing those readings.

## Released scope

- **37 source-context records**: candidate functions, physical grounds, depositional cautions and unassigned cases. These records are not37 independent, securely classified assemblages.
- **37 source-item records**: the complete25 illustrated Harappa1990 finds, all seven Bagasra seals/fragments, four Rakhigarhi steatite-analysis objects and one explicitly unjoined record for the two reported factory sealings. Records are not all single inscribed objects: the final record refers to a pair, and the steatite inventory includes debris/blank controls.
- **30 exact accession matches to existing objects /43 catalogue faces**: Harappa23, Bagasra6, Rakhigarhi1. Harappa’s house subset is11 objects/17 faces.
- **Six unmatched accession records**, retained: H90-1687, H90-1576, BSR5555, RGR573.B, RGR-s1, RGR3607. Absence from the catalogue is not absence from the excavation or a lost word.
- **One unverified candidate record**, not joined: RGR-1’s pair of elephant sealings. Lipi5560.1 is a possible catalogue candidate; matching city and animal cannot establish identity.
- **Zero independent ratings and zero semantic validation tests.** Context annotations were assembled retrospectively by a curator familiar with the key. The source-only packet is prepared for later independent review; its existence is not blinding.

All source context is added in separate columns. The original catalogue’s area, house, room, strata, signs and existing translation fields are unchanged. Multiple faces are displayed separately but never counted as independent objects. Household and Bagasra vicinity/gateway clusters are explicit. Full source disagreements and page coverage are in [SOURCES.md](SOURCES.md).

## Why a comparative craft-word test is not run here

The retrieved links do not supply a securely classified, adequately replicated set of contrasting craft-use contexts. The actual Eq2 faience, Eh3 bead and Eo15/16 ceramic production contexts have no exact inscription join in this collection. The readable SE seals are vicinity finds. The shell-associated fragments have no readable words. The Harappa house has several readings but an unidentified craft function. Giving the seals workshop labels from their proposed words would create the agreement we intended to test.

The strongest next data recovery targets are concrete: identify the **two RGR-1 factory sealings by excavation accession or verified photographs**, and recover excavation-unit/floor relationships for **BSR2037/8288**. The former would supply factory-linked inscriptions; the latter would establish whether the near-faience pair actually belongs to a production/use assemblage. A function claim still needs independent assessment of deposit history and comparative contexts. Neither target is a result already obtained.

## What was already done

Cúper already tested broad craft zones, site/material associations, household sharing and cross-city seal-size/rank patterns. This source-linked room/deposit expansion was not found implemented in the materialized original scripts/reports inspected; that is narrower than claiming he never considered any of these finds. Some catalogue rows already cite the Harappa figures. The earlier16-object Trench54 source crosswalk is credited and is not counted again. No new translation is claimed.

## Files and reproduction

- [Collection protocol](COLLECTION_PROTOCOL.md), recorded after initial source leads and before the accession/readings join.
- [Source-only context evidence](inputs/source_contexts.csv) and [complete source-item inventory](inputs/source_specimens.csv).
- [All joins, nonmatches and candidate status](results/accession_links.csv).
- [Every linked face and complete reading](results/readings_with_source_context.csv), [summary](results/summary.json), [standalone HTML](results/contexts.html).
- [run.py](run.py) uses the Python standard library and the existing catalogue. It checks inventory sizes, exact joins, nonmatches, face preservation and the key false bead-factory attribution. It does not score meanings.

Verification: the accession checks passed; the released HTML loaded all87 table rows (43 faces, seven nonmatches/candidates and37 contexts), search filtering worked, all five local report links resolved, and desktop/mobile browser checks found no script errors or horizontal page overflow. Reproduction uses the full repository layout described below; the standalone export is a viewing/data bundle.

From this repository:

```sh
python3 research/independent_validation_20261120/context_validation/run.py
```

All computation is local and takes under a second; Colab units used:0. Original public PDFs are source references rather than redistributed attachments.
