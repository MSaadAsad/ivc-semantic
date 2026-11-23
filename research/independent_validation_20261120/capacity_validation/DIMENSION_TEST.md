# Do the counts describe length, area or volume?

22 November 2026. The user's hypothesis has two distinct versions:

1. Marks describe a measurable property of the **vessel itself**. This can be compared with the recovered jar measurements.
2. Marks record lengths/areas of **external goods or land**. This needs an independently identified cloth length, plot area or other endpoint linked to the account. A jar's width or projected area is not that endpoint. The vessel comparison does not test this second version.

The comparison below is retrospective. A four-row pilot was computed before this note, so this is not preregistration. The original three jars were already selected in earlier work because their volumes match their counts; they are development evidence, not fresh random observations.

## Equal-complexity physical models

Use the same four cases for the primary models: H-372, H-371, H-370 and H95-2661. Input sources and exclusions are in `inputs/vessel_dimensions.csv` and the existing eight-vessel source inventory. Do not infer a whole-vessel dimension from a sherd or inscription's dimensions.

- Length: maximum external diameter, D. A circumference model is identical after changing the unit byπ, so do not count it as an independent result.
- Area: largest circular cross-section, πD²/4. This is not total curved surface area, cloth area or a field plot.
- Volume: reported interior profile capacity, with the fresh H95 trace used for its main value.

Each hypothesis has one fitted scale and no intercept: quantity=k×number of marks. Learn k as the geometric mean of quantity/count on the training objects. Predict the omitted object's **count** from its measured quantity/k. This puts all models on the same response scale. Every object is omitted in turn; publish all unrounded predictions. Primary score: root mean squared log-count error, which is invariant to measurement units. Also publish mean absolute count error and mean absolute percentage count error for interpretation.

The primary panel also has a one-parameter constant-count baseline: predict the geometric mean count in the other three jars, ignoring their dimensions. This checks whether geometry improves prediction beyond the small panel's count distribution.

Separately train on the original three jars and evaluate H95. Report original-three-only performance to expose selection, not to claim a new confirmation of volume. Retain a conditional fifth case (MD-1374) and sixth (K-90) as sensitivities, with their mixed-count and photo-scale assumptions visible. Keep both1? specimens unscored.

Height is a separate secondary operationalization. H-372's flattened table does not securely identify its external height, so no value is guessed. On the three objects with clear external heights compare diameter, height, circular-section area, bounding-cylinder side area πDH, and volume on that same three-object subset. The side area is an envelope proxy, not a measurement of the actual irregular pottery surface.

## Measurement and scope checks

Stress-test the primary comparison over all81 combinations of independently perturbing each diameter/overall linear scale by−2%,0,+2%. Coherently scale areas by the square and capacities by the cube. Independently consider the three published sphere/ellipsoid/profile volume calculations for each original jar, plus the H95 trace minimum/main/maximum. Crossing these choices gives6,561 geometric/model scenarios. They are analyst-selected scenarios, not a probability distribution or confidence interval.

Check unit invariance, exact recovery of synthetic length/area/volume models, source exclusions, all fold memberships and the unchanged source counts. Do not fit separate units to individual jars, optimize a dimensional exponent, round predictions to improve a score or declare a language from a winning geometry model. With four primary objects there is no population-level accuracy claim or significance test.

## Evidence for external length/area accounts

Kenoyer2010, *Measuring the Harappan World*, pp.117–118, documents physical linear-measurement devices and discusses architecture. [Primary chapter](https://www.harappa.com/sites/default/files/pdf/Kenoyer%202010%20Measuring%20the%20Harappan%20World.pdf). The inspected text does not link the jar's sign034 or a sign700 account to an independently measured textile length or land area. Its p.119 example of two-line-marked well bricks supplies a physical length and a possible commission mark, not an established account-unit reading.

The [museum-object discussion of the shell scale](https://www.harappa.com/content/indus-scale) identifies a ruler-like object from Mohenjo-daro DK Room46/Block18, with divisions and a circle. Such graduations support linear measurement practices but do not identify the dimension represented by a separate four-stroke jar account. Competing scale reconstructions are not adopted as deciphered units here. These were bounded source checks, not an exhaustive search of all surviving textiles, plots or inscriptions.

Prior-work search: targeted materialized `work_scripts`/`jobs/out` searches found no equivalent same-vessel, equal-parameter diameter/section-area/capacity count prediction. Existing `met_03_physical.py` uses text length, sherd area and object size as controls or associations, and already fits the original three jar volumes. Those are credited; the new comparison is not described as the first study of Indus length/area measurement.

## Results

The comparison uses four primary objects, not 69 independent objects: 69 is the number of predictions across overlapping panels and models. The baseline contributes four separate predictions.

| Assumed quantity | Average percentage error predicting omitted mark counts | Average absolute count error |
|---|---:|---:|
| Maximum width / circumference |22.1%|0.98 marks|
| Widest circular cross-section area |20.0%|0.90 marks|
| Interior capacity |27.7%|1.33 marks|
| Constant count, ignoring geometry |44.2%|2.00 marks|

The area model also has the lowest primary log-error score. The additional H95 jar carries four strokes (catalogue rim sign **034**, proposed reading **four**). Training on the original three jars predicts **3.82 marks from width, 2.92 from area and 2.20 from capacity**. This is a comparison of dimensional interpretations of a count; it does not supply a spoken word or a new translation. No sign700 cup/measure is transcribed in that catalogue rim entry; its separate body marks are not transcribed there.

The original selected three favor volume extremely closely. Adding conditional MD-1374 favors area by the primary log score (width narrowly wins by percentage error); also adding the unlabelled-scale K-90 favors volume. The separate three-object height panel favors width. On the four-object panel, area stays ahead across all 6,561 chosen stress configurations, but this does not repair source selection or establish general predictive accuracy. Those configurations are neither independent archaeological observations nor a probability of an area reading.

**Relevance to the hypothesis:** length and area are live alternatives to a universal full-capacity interpretation. These measurements do not select a reliable replacement: the length unit alone ranges from 11.9 to 20.5 cm of diameter per mark across the four jars. They do not decide whether an external account records cloth length or land area; no such measured subject was recovered. No named unit, sign pronunciation or language is established.

## Reproduce and inspect

From the repository, run the existing capacity calculation first, then this extension:

```sh
python3 research/independent_validation_20261120/capacity_validation/run.py
python3 research/independent_validation_20261120/capacity_validation/dimensions.py
```

[Illustrated comparison](results/dimensions.html), [all folds](results/dimension_predictions_all_folds.csv), [baseline folds](results/dimension_constant_baseline.csv), [all panel scores](results/dimension_model_scores.csv), [eight-row dimension source table](inputs/vessel_dimensions.csv), [excluded uncertain readings](results/dimension_excluded_readings.csv), [summary](results/dimension_summary.json).

Analytical checks passed for known synthetic length/area/volume relations, measurement-unit invariance, excluded readings, fold counts and absence of the target from its training objects. Computation ran locally in seconds; Colab units: 0.

The final HTML was checked in isolated Chrome at desktop and mobile sizes: all four comparison tables and the scientific figure loaded, all report links resolved, no script errors or page overflow occurred. Wide tables scroll within their containers. Desktop and mobile screenshots were visually inspected.
