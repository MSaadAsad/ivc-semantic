# Additional inscribed-jar capacity test

**The additional four-stroke Harappa jar reconstructs to about89L; Cúper's fixed rule predicts37L.** This weakens the specific interpretation **one tall stroke=9.24L of full vessel capacity**. It does not establish what language the marks represent or exclude other accounting interpretations.

[Open the illustrated report](results/capacity.html). [Prediction/geometry comparison](results/h95_capacity_comparison.svg). [Source drawing and trace](results/h95_profile_overlay.svg).

## Could the marks describe length or area?

The [new dimensional comparison](DIMENSION_TEST.md) tests all three against the same four jars, learning a common unit from the other jars before predicting each omitted count. Average count errors are **20% for widest cross-section area, 22% for width and 28% for capacity**, versus44% when ignoring geometry. Width predicts3.82 marks for the additional four-mark H95 jar; area predicts2.92 and volume2.20. The original selected three instead favor volume, and including two conditional objects can reverse the preference. This is an exploratory alternative, not an identified ancient unit or a new translation.

[Open the length/area/volume report](results/dimensions.html). **Accounts for external cloth lengths or land areas remain untested:** vessel geometry is not the measured subject of that hypothesis. The report retains that distinction, all source cases and every prediction.

[Illustrated chart (PNG)](results/jar_marks_comparison.png) · [Scalable chart (SVG)](results/jar_marks_comparison.svg). The chart puts Kenoyer's published H95 drawing beside its proposed four-mark reading, all four jars' measurements and the count predictions. Redrawn tallies are explicitly schematic, and the original three versus additional jar remain distinguished. It uses the existing results without fitting any new models. Regenerate with `python3 research/independent_validation_20261120/capacity_validation/illustrate_dimensions.py` after the calculations; this optional plotting step needs Matplotlib and Pillow. The source underlay is extracted from the attributed overlay already in the repository, so no source PDF download is required.

## What was tested

The primary drawing labels the jar **H95-2661/6640-501**, an accession-based candidate for catalogue **H-2263**. The complete existing catalogue reading is **“4”**, sign034. The drawing also includes separate body writing and potter's marks that the rim-only catalogue entry does not transcribe. Its caption instead givesH95-2662; the catalogue unit string differs. All identifiers and discrepancies are retained.

Applying the existing9.24L unit gives **4×9.24=36.96L** before changing any interpretation. A fresh trace of the published inner wall, rotated using its independently labelled20cm scale, gives **88.90L** up to the rim. The source geometry does not use the predicted number to establish its scale.

| Comparison | Litres | Meaning |
|---|---:|---|
| Existing fixed prediction |36.96|Four strokes at9.24L each.|
| Reconstructed inner capacity |88.90|Piecewise linear radius profile; circular cross-sections.|
| Chosen tracing/scale perturbations |80.69–97.91|All27 combinations: ±3px radius, ±2px scale-bar length, ±2% vertical scaling. Not a confidence interval.|
| Broad ±10% linear-size scenario |64.81–118.33|Volume scales cubically. Does not encompass every possible error in restoration or drawing.|
| Later Wells2015 unit applied unchanged |161.60|Four strokes at40.4L; this also fails to match this jar's rim capacity under the tested scenarios.|

The calculated capacity is **2.41 times** the repo's prediction. The mismatch survives the listed tracing/scale variations. It remains conditional on accurate drawing/restoration, rotational symmetry, the four-stroke interpretation and the accession link.

**Partial filling remains possible.**37L is about42% of the jar's reconstructed capacity, reached at roughly56% of its interior height. A claim that the marks record an amount put into the jar is different from a claim that they record its full capacity. No fill mark or independently specified fill rule was recovered. Neither a particular commodity nor a new unit is chosen after seeing the result.

## Does another proposed unit fit better?

**Fuls's previously proposed22.6L unit predicts90.4L for four marks**, only1.50L (1.7%) above our88.90L reconstruction. The sign transcription remains **“four”**; this changes the unit assigned to each count, not its spoken reading.

However,22.6L was calculated using this same H95 jar together with MD-1374, so its close fit is not independent validation. A conditional comparison excluding H95 uses only MD-1374's138.8L divided by six marks:23.13L/unit, predicting92.53L here (4.1% high). That assumes its three vertical/three oblique marks are equivalent counts, and relies on a source profile not independently retraced here. The exact catalogue join for MD-1374 remains absent.

The [alternative-unit table](results/alternative_unit_assignments.csv) retains these dependencies and the deliberately target-fitted22.225L/unit value, whose perfect fit proves nothing. No named Dravidian unit is identified by fitting litres. The next discriminator is a prior rule for deciding **which unit applies** from other inscription/context evidence, followed by a different vessel.

## A correction to the old calibration

The continuation previously repeated the repo's9.24L figure and described its three source jars as measured27.30/55.56/65.89L. That source description needs correction: the repo obtained those numbers from older news reporting. **Wells's later primary account explicitly gives about40.4L per tall stroke**, and Fuls2012 reports profile capacities121.0/240.6/283.8L for the same three jars.

Those are not three fresh test objects, and their different source versions must not be pooled. The later calculations use dimensions taken in Wells's2009 examination, not direct liquid-filling measurements. The cause of the older/later discrepancy has not been established here. The older9.24L anchor and its propagated absolute ladder capacities therefore need source reconciliation before being presented as established physical calibration. Existing structural evidence for counts is a separate question.

The [calibration-source comparison](results/original_calibration_source_comparison.csv) preserves both sets. Fuls table cells were recovered from public author-posted text; the original PDF table was not visually verified. Wells's40.4L figure is also directly stated in his book's running text.

## How large was the expansion?

- Recovered the **complete eight-vessel Fuls inventory**: three original calibration objects and five additional source vessels. This does not mean eight new specimens or measurements.
- **One additional vessel** supplies an identified numeric inscription and an independently labelled interior profile for the primary comparison. This is one concrete case test, not a general accuracy estimate. No p-value was calculated.
- **K-90:** visually verified its two rim strokes and separate body inscription in the primary catalogue. The photograph's scale units are unlabelled, so Fuls's103L estimate remains conditional and is not a second independently verified result.
- **MD-1374:** an unjoined source vessel with three vertical and three oblique marks; it is not silently equated with CISI M-1374, a different catalogue record. No fixed model prediction is scored.
- **MD-63-3 and MD-63-6:** explicit Mackay plate-reference links to M-2063 and M-2061. Their current proposed readings are respectively **“Of the Seed-weight-King house”** and **“Seed-weight; One Bamboo-star; Hill-share, [unclear sign], second-ward house.”** Fuls's tentative1? is not a confirmed capacity count; the unchanged capacity parser supplies no prediction for either.
- Screened **all635 pottery faces on629 catalogue objects**. Only the original `POT:T:g` domain receives parser predictions;190 objects receive numeric candidates. These are not190 measured jars. A catalogue “complete” label does not certify an intact physical vessel with reconstructable volume.
- Exposed a **K-90 face-order issue**: the actual parser returns1cup when its body face is processed first, but2 when the rim face is first. That behavior is preserved and released, not silently repaired to improve agreement.

All exclusions, readings, source volumes and joins are in the [eight-vessel inventory](results/eight_vessel_source_inventory.csv). The [full pottery screen](results/all_pottery_prediction_screen.csv) retains every existing object, not only numerical candidates.

## Prior work and independence

Cúper already analysed the three original jars, M-2066 geometry, pot-wall thickness and metrological distributions. This does not repeat those as new tests. An H95 profile/capacity comparison was not found implemented in the materialized original scripts/reports inspected.

The general approach is published, and another public repository already traced the H95 drawing. Both are explicitly credited in [SOURCES.md](SOURCES.md). Our trace coordinates and code were produced afresh, but the earlier88.3/85.96L results were already known. **This is retrospective corroboration of geometry and a new comparison with Cúper's fixed rule, not blind validation or an untouched archaeological discovery.** No independent raters or new laboratory measurements are claimed.

The initial trace was revised once because its overlay visibly missed the inner wall. Both coordinate sets are retained; the corrected contour was not fitted to a target volume. The result is88.90L, compared with Fuls's reported88.3 and the other repository's85.96. Seeing these prior results limits independence.

## What this adds to Cúper's work

This continuation improves the checking of one specific capacity claim. It exposes conflicting source values for the original calibration, compares the unchanged9.24L rule with one additional scaled interior profile, and releases tracing uncertainty, source disagreements and excluded cases. The37L prediction versus approximately89L reconstructed is evidence against applying that fixed rule to this jar's full capacity, subject to the stated identity and geometry assumptions.

The alternative22–23L pattern appears on two vessels from different cities: H95-2661 at Harappa gives22.2L per mark in our reconstruction, while the published MD-1374 estimate at Mohenjo-daro gives23.1L if its six mixed marks are equivalent counts. Both vessels contributed to Fuls's earlier22.6L proposal. They therefore do not provide an independent dataset validating that proposal. The original three Harappa jars instead give about40.1–40.5L per mark in Fuls's reported profiles;22.6L is not a universal fit to the recovered data.

Fuls proposed the alternative before this continuation, and another public project already traced the H95 drawing. Neither the unit nor the general approach is claimed as our discovery. The fresh comparison with Cúper's fixed conversion and the explicit source qualifications are the additions here.

This is a stronger source check on a numerical interpretation, not an established replacement decipherment. No new translation, sign pronunciation, named ancient unit or language identification has been demonstrated.

## Reproduce

The calculations use Python's standard library and extract only the original metrology parser's pure definitions from `work_scripts/met_common.py` and `met_03_physical.py`. They neither import those modules nor create/overwrite upstream logs. Mathematical checks cover cylinders, cones, frustum subdivision, partial filling and cubic scale dependence. Inventory, identity-exclusion, parser-order and uncertainty checks also run.

From the repository:

```sh
python3 research/independent_validation_20261120/capacity_validation/run.py
```

To regenerate the source-underlaid overlay, supply the primary PDF from [SOURCES.md](SOURCES.md); this optional step needs PyMuPDF and Pillow and checks the file's SHA256:

```sh
python3 research/independent_validation_20261120/capacity_validation/run.py --source-pdf /path/to/kenoyer2025-reprint.pdf
```

[Design and disclosed exposure](DESIGN.md), [trace coordinates](inputs/h95_profile_trace.json), [full source inventory](inputs/fuls2012_inventory.csv), [all sensitivity scenarios](results/h95_geometry_sensitivity.csv), [fixed predictions](results/h95_fixed_predictions.csv), [fill levels](results/h95_fill_levels.csv), [summary](results/summary.json).

All computation took less than a second locally. Colab units used:0. The standalone export is a viewing/data bundle; reproduction uses the repository layout.

The geometry/parser checks passed. Browser verification loaded both scientific figures and all eight source rows, resolved the report links, and found no script errors or mobile page overflow. The source overlay was visually checked against the inner wall; the first trace is retained as superseded rather than silently discarded.
