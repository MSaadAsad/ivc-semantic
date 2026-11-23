# Direct Indus-sequence test of an Elamite-style agreement representation

**The broad repeated-marker model adds no selected predictive rule.** On264 internal validation formulas it selects a copying coefficient of0; its predictions on183 test formulas are therefore identical to the word-free baseline. This supplies no positive support for this written-agreement representation. It does not establish that the Indus language is or is not Elamite.

An exploratory sparse refinement was also run, letting the fitting data choose at most six marker signs. It selects407 from **one validation opportunity**; the test set has **zero eligible opportunities** for that chosen rule. This is an unsupported one-case lead, not a successful language result. The complete subset search steps and test probabilities are retained.

[Illustrated report](results/concordance.html) · [Design](CONCORDANCE_PLAN.md) · [Complete summary](results/concordance_summary.json).

## What was actually tested?

Elamite noun phrases can show matching grammatical endings on linked words. For example, Basello gives `nap-(i)r u-r` “my god”: the final class marker is repeated. The source also explicitly says that an overt head suffix can be absent, especially with names/kinship terms, and that agreement was written in different ways. [Basello, printed28/PDF22](https://unora.unior.it/bitstream/11574/217200/1/basello2023introduction-elamite.pdf); [Stolper, pp.73–74](https://www.elamit.net/depot/resources/stolper2004original.pdf).

The conditional Indus model asks whether a corresponding pattern is useful **if written with a repeatable independent sign**, schematically `A–s–B–s`. Seeing the earlier `s` would help predict the later `s`, beyond the inscription's length, position, object type and immediately preceding sign. Earlier candidate markers must have their own preceding sign, a separating stem and distinct immediately preceding stems. No actual word boundaries or grammatical marker identities are known.

**No Dravidian forms, Cúper sign meanings or dictionary affinities enter this experiment.** It is a direct structural test on Indus sequences, not an Elamite–Dravidian comparison. No sign is assigned the sound r/p/k, and no noun is translated. This mechanism is compatible with some Elamite writing, but is not unique to Elamite or mandatory in every possible representation of Elamite.

## Data and untouched model scoring

| Stage | Distinct full formulas | Purpose |
|---|---:|---|
| Lipi inner fitting |1,109|Build baseline and55 frequent candidate marker signs.|
| Lipi internal validation |264|Choose one shared copying coefficient; optimum0 in both sequence directions.|
| All Lipi fitting |1,373|Refit baseline after the coefficient is fixed.|
| New-formula evaluation |183|Evaluate formulas absent from Lipi; no test coefficient selection.|

The source containers hold4,476 Lipi object-events/5,403 faces and990 New object-events/1,121 faces. Requiring at least four signs and no damaged/non-numeric-ID transcription leaves1,654 Lipi faces/1,373 formulas and205 New faces/189 formulas. Six exact formula overlaps are removed from the New set. These are distinct inscription patterns, **not1,556 independently excavated new objects**. Repeated full formulas count once. All physical-record keys and source sites remain in [membership.csv](results/concordance_formula_membership.csv).

The corpora and graphical inventory existed in the repo and were used in earlier research. Test formulas are excluded from this model's fitting, not archaeologically fresh evidence. A clean numeric-ID transcription is not proof that a physical object is complete. Shared templates and transcription dependencies remain possible after exact-form exclusion.

## Results

| Writing direction | Chosen copying weight | Test positions | Eligible copy opportunities | Actual candidate repetitions | Selected-model gain |
|---|---:|---:|---:|---:|---:|
| As stored, primary |0%|496|326|6|0 bits|
| Reversed, diagnostic |0%|496|351|5|0 bits|

Zero gain is **by construction after zero copying weight was selected**. It is not183 independent failures and the degenerate zero bootstrap interval is not precise evidence against every agreement system. The useful finding is that this particular copy rule failed to earn a place in the model during validation. The separate Elamite language hypothesis remains unresolved.

For example, `095–740–176–740–090` contains a repeated740 at an admissible position. That recurrence alone does not establish that740 is a grammatical ending, or assign a language or translation. Across all primary test opportunities there are only six admissible repetitions. Every position, probability and actual repeat is in [predictions.csv](results/concordance_as_stored_predictions.csv).

The full coefficient curves were added as explicitly post-fit diagnostics after observing the zero optimum. At5% copying weight, primary validation gain is−0.0402 bits/sign and test gain−0.0268. At0.5%, the test curve has a tiny positive0.00287 gain, while validation is negative. That test-set optimum is not promoted into the selected model. All grid points, including this exception, are released in [as-stored curve](results/concordance_as_stored_coefficient_curve.csv) and [reversed curve](results/concordance_reversed_coefficient_curve.csv).

The sparse refinement addresses dilution by non-marker signs. It greedily selects up to six signs and one copying coefficient on Lipi internal validation, then freezes them before scoring New. The six-marker ceiling follows the distinct nonzero nominal-class marker types in the cited grammar; it does not map any sign to those Elamite sounds. The search chooses only407, at95% copying weight, because its one validation opportunity repeats. No eligible407 opportunity occurs in the test formulas, so its zero gain provides no test of the proposed407 rule. This refinement was designed after viewing the broad model's results and is explicitly exploratory. [Selection steps](results/concordance_sparse_selection.csv), [every sparse prediction](results/concordance_sparse_predictions.csv).

## Could agreement be inside a modified sign?

A separate graphical check admits nine existing decompositions specifically describing a four-small-stroke/line cage. It excludes generic brackets, other enclosures, hats and four-pair cages. It compares adjacent signs from different graphic root families rather than counting repeated variants of the same base.

Lipi supplies56 eligible pairs:50 plain/plain and6 plain/caged; no caged/caged pair occurs. The New-formula set supplies only4 eligible pairs, all plain/plain. **There is no marked test pair, so this representation is not evaluable as an agreement confirmation/refutation.** No significance test is reported. [Exact admitted rows](results/concordance_graphic_inventory.csv), [all pairs](results/concordance_graphic_pairs.csv), [counts](results/concordance_graphic_summary.csv).

## Addition to existing work

The repo already tested Elamite dictionaries, grammatical order assumptions, general language-fitting QAP models and Linear-Elamite sign-value transfer. This extension tests a particular repeated-marker prediction using raw sequences and an explicit no-agreement comparator; it does not repeat those earlier tasks as new discoveries. A bounded search of materialized scripts/reports found no implementation of this copy mixture. Generic agreement patterns are not Elamite-specific evidence, and passing this check would still require competing explanations and actual reading predictions.

## Verification and reproduction

```sh
python3 research/independent_validation_20261120/elamite_validation/concordance.py
python3 research/independent_validation_20261120/elamite_validation/concordance_report.py
```

NumPy is needed for the model; Matplotlib for the optional figure. Source hashes, all splits, candidate signs, every test position and both directions are released. Synthetic independent-marker agreement is recovered with positive test gain; a sign-independent synthetic control yields only negligible gain. These are scoring-engine checks, not recovery of a known Elamite corpus. Runtime and zero Colab usage are recorded in the summary. Nothing in this experiment produces an established Elamite translation of an Indus inscription.

Verification confirmed disjoint formula sets, correct unused test-split labels and1,488 positive-probability test predictions across the two directions and sparse refinement. Desktop/mobile browser checks loaded the figure and all three tables (2/6/2 rows), resolved local report links and found no script errors or page overflow. The desktop report and figure were visually inspected. The final model run took0.62 seconds locally; Colab units:0.
