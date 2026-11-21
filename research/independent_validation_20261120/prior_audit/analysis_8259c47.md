# Analysis of Cuuper22/ivc — work branch

Reviewed commit: [`8259c47fdf4a076f04029254f97c83f04abb139e`](https://github.com/Cuuper22/ivc/tree/8259c47fdf4a076f04029254f97c83f04abb139e), dated 19 November 2026. This is an analysis of the research and its implementation, with particular attention to Key #4. No repository fixes or remote changes were made.

## Assessment

The repository contains substantial, useful work on corpus organization, recurring sign sequences, positional classes, numeral contexts, and possible allographs. Its best results concern **which signs behave similarly and how inscriptions are organized**. I independently reproduced the committed allograph model's principal predictive scores exactly.

The stronger claim that 114 signs are sound-locked, producing a roughly 74% decipherment, does **not** follow from the implemented evaluations. The coverage metric measures membership in an assigned lexicon. Several statistical controls hold the interpretive choices fixed instead of reproducing the process that selected them. A global dictionary signal is repeatedly promoted into individual sign readings without an individual identification test. The language-family probabilities also depend on manually assigned likelihoods.

There is additionally a concrete counting error: the master merge removes unmapped Mahadevan signs before evaluating coverage, including the test for a completely covered inscription. Its quoted unseen percentage and fully covered face count are inflated.

This is a promising exploratory research corpus and hypothesis generator. At this commit, I would not present it as an independently validated phonetic decipherment.

## What I inspected and verified

I inspected the branch's top-level research books and project rules, the Key #2–#4 pipeline, the current master lexicon and corpus, allograph classification and evaluation code, grammar and metrology methods, negative controls, and reproduction configuration. I examined all five Key #4 reports and their principal scripts. The repository has 21,688 tracked files, including 12,950 under evidence and 6,049 under research; this was a focused deep review, not a claim to have read every source or photograph.

Checks actually run:

- Independently recomputed the master T5 counts from the committed CSVs, reproducing the stored filtered totals exactly.
- Recomputed coverage with every nonempty sign retained, exposing the unmapped-sign error and identifying all 40 falsely complete unseen faces.
- Re-evaluated the unmerged, pure-allograph, and allograph-plus-workshop models using the repository's selected scoring functions and committed clusters. Principal cross-validation and unseen scores matched the stored results exactly.
- Checked the syntax of all 575 top-level Python scripts under work_scripts using Python 3.11.13, the documented Python version.
- Examined per-sign shuffle probabilities for all 18 promoted Wave-2 signs.
- Recomputed sensitivity of the seven-family normalized likelihood score to its manually assigned inputs.
- Compared divisor compatibility for bases 12, 24, 36, and 60 using the committed cup-count distribution.
- Counted identical sign sequences shared by the nominally unseen intact subset and Lipi.
- Rebuilt the frontier bigram baseline and exhaustively permuted the labels of whole seals for the BMAC-versus-Gulf contrast.

I did not rerun every 5,000-shuffle study, the entire older research campaign, or all raw-data extraction. I did not independently authenticate every dictionary gloss, excavation reference, photograph transcription, or museum provenance. Numbers described below as reported, rather than reproduced, remain repository results.

## How the research system works

The main flow is:

1. Assemble Lipi and Mahadevan inscriptions, archaeological metadata, and crosswalks between sign catalogues.
2. Infer recurring positional roles and a clause grammar, FRAME v3.
3. Associate signs and phrases with physical object classes, locations, motifs, and potential numerical systems.
4. Search candidate language dictionaries for words connecting a proposed pictorial identity to a proposed functional meaning, including homophones and stem matches.
5. Extend readings through ligatures, operators, repeated contexts, and allograph clusters.
6. Merge the accepted sign inventories and count how much of the corpus they cover.

The supporting material is unusually extensive: scripts, intermediate CSVs, reports, a SQLite evidence database, negative experiments, and a diary. The main weakness is the transition from one evidential level to the next. A reliable positional class does not automatically establish a semantic category; a semantic association does not identify a particular word; an etymological word match does not establish that the Indus sign encoded that sound.

The word-free structural analysis can retain value even when a proposed word is wrong. These layers should have separate success criteria.

The five Key #4 levers also share inputs, earlier sign assignments, and much of their corpus. Their agreement is conditional support within one research system, rather than five independent confirmations. The master script directly imports inventories from #4A, #4B, and #4D; #4C and #4E provide claimed corroboration rather than separate sound inventories consumed by that merge.

## 1. Confirmed defect: unknown signs disappear from the master coverage calculation

The master merge creates tokens using an `isdigit()` filter. That retains mapped numeric catalogue IDs such as 740 but removes unmapped Mahadevan identifiers such as X82. Here, “numeric” describes the **identifier format**, not whether the sign is a numeral.

The same shortened token list is used for both coverage denominators and the `h == len(toks)` full-coverage test. Faces containing only unmapped signs disappear altogether. Mixed faces can be counted as completely covered despite containing unresolved signs.

Source: [master coverage evaluator](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4_master_merge.py).

### Corrected T5 coverage

These are lexicon-membership figures, not established translation accuracy.

| Metric | Committed master calculation | All signs retained |
|---|---:|---:|
| Unseen intact faces evaluated | 563 | 627 |
| Unseen tokens evaluated | 1,994 | 2,161 |
| Unseen tokens covered | 1,507 | 1,507 |
| Unseen token coverage | 75.58% | **69.74%** |
| Fully covered unseen faces | 244 | **204** |
| Fully covered unseen share | 43.34% | **32.54%** |
| Combined intact faces evaluated | 4,163 | 4,227 |
| Combined tokens evaluated | 15,203 | 15,370 |
| Combined tokens covered | 11,284 | 11,284 |
| Combined token coverage | 74.22% | **73.42%** |
| Fully covered combined faces | 1,776 | **1,736** |
| Fully covered combined share | 42.66% | **41.07%** |
| Fully covered combined faces of length ≥3 | 725 | **705** |

Lipi is unaffected: all its IDs in this slice pass the filter. The error is concentrated in the second catalogue, making the apparent out-of-sample improvement particularly misleading.

The unseen subset loses 167 tokens and 64 entire faces. Another 40 mixed faces become falsely complete. For example, Mahadevan face 94 is `740-X82-740`. The evaluator reduces it to `740-740` and counts it as fully covered.

**Fix:** preserve all identifiers; count every unresolved identifier as uncovered; require every original sign to be covered for face-level completeness. Assert that the evaluated intact subsets have 3,600 and 627 faces. If reporting mapped-only coverage, label it explicitly and report its excluded share beside it.

## 2. Coverage is not a test of decipherment accuracy

The master evaluator asks whether a sign ID belongs to a dictionary. It never checks whether that dictionary gives the sign the correct sound or meaning. Replacing every root with a random word while retaining the keys leaves all coverage figures unchanged.

The metric is useful as a measure of how broadly a hypothesis has assigned values. It cannot validate those values. The automatic increase from adding frequent signs or inheriting parent readings is guaranteed by the metric's definition.

The T5 dictionary has 114 entries, but these are heterogeneous: proposed lexical sounds, ordinary numerals, measures, allographs, and modifier descriptions. Its entries include bracketed or caged derivatives and the value `*24`, rather than a uniformly established set of 114 pronounced words. The baseline alone assigns local Dravidian forms to numeral signs. Recognition of a quantity does not independently establish how its users pronounced it.

For scale, choosing the 114 most frequent identifiers in the combined intact corpus covers **86.14%** of its tokens without supplying a single meaning. This is a descriptive frequency ceiling, not a proposed decoder; it demonstrates why coverage alone cannot evaluate correctness.

Better reporting would separate sign-identity coverage, proposed semantic coverage, proposed phonetic coverage, and externally validated readings. The current headline collapses them.

## 3. The Wave-2 aggregate result does not identify 18 individual sounds

The Wave-2 report gives an aggregate Dravidian stem-match result of 25/30 with P=0.00040 under its dictionary-shuffling null. There may be a real effect within that model. It does not establish which candidate word belongs to each sign, nor that each promoted sign is individually identified.

The output table's own per-sign probabilities are much weaker. Of the 18 signs promoted to “building on it”:

- Only **1/18** has stem-match shuffle probability below 0.05.
- Only **2/18** have exact-match shuffle probability below 0.05.
- **0/18** pass a simple 0.05/30 per-sign Bonferroni threshold on the stem metric.

Examples of the stored stem probabilities: 700 = 0.79104; 233 = 0.73905; 407 = 0.81804; 806 = 0.79424; 503 = 0.50110. A dictionary bridge of this general kind is common for those domains under the implemented null. These values do not mean the candidate words are necessarily false; they mean this individual test does not identify them.

The promoted roots, supporting prose, and statuses come from a manually written `AUDITED_WAVE2_TABLE`, then are copied into the output. The evaluator does not derive the 18 accepted assignments through a calibrated individual decision rule.

Sources: [Wave-2 implementation](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4b_bootstrap_wave2.py#L1233), [per-sign results](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_data/key4b/test4b1_top30_sign_table.csv).

**Required next test:** each proposed value must outperform alternative values for the same sign on facts that distinguish their meanings or phonetic behavior. An aggregate family score can rank a hypothesis; it cannot be distributed among all component assignments as a certificate.

## 4. The dictionary null does not include the interpretive search

The Wave-2 visual and functional keyword lists are manually specified. For example, the 503 comparison allows hill/mountain/peak/ridge/mound on the pictorial side and garland/necklace/string/bead/shell/dye/estate on the functional side. The script then finds compatible dictionary forms and compares the total with shuffled form-to-meaning assignments.

That tests the fixed keyword lists against a particular dictionary null. It does not test how often a researcher could find a winning list after trying alternative visual descriptions, functional categories, near-homophones, word families, or rescue attempts.

The “zero overlap” check is real but limited: it prevents literal shared words and selected prefixes between two English or German keyword lists. It does not make their concepts independent. Pairs such as sprout/child, knot/bundle, and woman/goddess are related concepts even with no literal word overlap.

The family comparison also includes several matching modes, subsets, audit lexicons, and redesigned tests. Dividing alpha by seven addresses seven family comparisons for a specified test. It does not account for all these other choices or earlier selection rounds. I cannot reconstruct an honest experiment-wide corrected P-value from the committed reports, and I would not invent one.

The strongest correction is to freeze sign descriptions and candidate domains before inspecting target-language matches, or rerun the entire selection process on decoys. The null should include the flexibility available to the actual researcher.

Source: [Wave-2 keyword specification and tests](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4b_bootstrap_wave2.py#L190).

## 5. “Proto-Dravidian” is stronger than what the lexicon builder reconstructs

The two-branch builder requires an etymological entry to be represented in multiple branches, then chooses a headword using a priority list starting with Tamil and pools glosses from selected daughter languages. It does not perform phonological reconstruction of a dated Proto-Dravidian form and its Bronze Age senses.

This can support testing vocabulary with broad Dravidian cognate distribution. It cannot by itself establish that the chosen Tamil-like form, the pooled sense, and the proposed homophony all coexisted in the relevant ancient language.

The “phoneme-preserving” Key #2 normalizer also folds vowel length; its stem mode removes selected endings under a common rule across families. These are model assumptions with linguistic consequences, not exact ancient sound correspondences. Later Key #4C normalization is coarser still, removing consonant diacritics and collapsing geminates.

Sources: [two-branch builder](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key2a_rebus_lock.py#L198), [normalization](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key2a_rebus_lock.py#L109). The underlying [Dravidian Etymological Dictionary](https://dsal.uchicago.edu/dictionaries/burrow/) is valuable source material; treating its cognate sets as already reconstructed phonetic assignments is the additional inference at issue.

## 6. The “93% Proto-Dravidian” posterior comes from assigned likelihoods

The typology scorer hardcodes a likelihood for each language-feature pair. Proto-Dravidian receives values such as 0.95 for several features and 0.98 for suffixing-only morphology. Competing families receive lower hand-assigned values. The program raises these probabilities to manually selected correlation weights, multiplies them, and normalizes over seven selected historical families.

I reproduced the normalized Dravidian score: **92.97%**. It is an output of those judgments, not an empirically calibrated probability that the Indus language was Proto-Dravidian.

Illustrative sensitivity checks, holding the rest of the model fixed:

| Input change | Normalized Dravidian share |
|---|---:|
| Original assigned likelihoods | 92.97% |
| Remove the suffixing-only feature, G7 | 80.93% |
| Remove G7 and the numerical-system feature, G5 | 52.77% |
| Move every assigned likelihood halfway toward 0.5 | 60.20% |

These are sensitivity exercises, not alternative estimates of the true language. They show that the precise headline percentage depends strongly on the judgment scale and a few disputed features.

Several measured premises are also interpretation-dependent: treating a frequent ending as a possessive marker is stronger than measuring final position; inferring an absence of linguistic prefixes from short sign sequences assumes how morphology is represented; a metrological base is not automatically the base of a spoken numeral system. The model omits unknown or extinct language families as explicit alternatives, so the normalized score cannot represent an open-world probability.

Source: [candidate likelihood matrix and posterior calculation](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/typo_02_grammar_fit.py#L544).

## 7. The unseen corpus is useful but has been reused and partly incorporated

Separating unpartnered Mahadevan objects is valuable. It reduces direct duplication of catalogued objects. It is not sufficient to establish that every later analysis has a fresh test set.

Specific observations:

- Wave-2 selects its top 30 signs using frequencies across Lipi **and** the unseen intact subset.
- It constructs an “unseen-replicated” sign subset using second-corpus odds ratios before testing that subset's lexical matches. This is a selected subgroup, not an untouched replication cohort.
- Key #4A builds distributional profiles from the combined intact corpus, then uses those profiles for operators and allograph judgments. Master inheritance from those judgments has consequently used the supposed test corpus.
- The same second corpus is repeatedly inspected across research waves and redesigns. Deterministic reruns preserve that adaptive history; they do not erase it.
- **107/627** unseen intact faces have exactly the same projected sign sequence as an intact Lipi face. The unseen subset has 456 distinct sequences. These can be different physical objects and still valid data, but they test a weaker form of generalization than entirely novel sequences.

The 107 count is not proof that those physical objects were duplicated or that the partner mapping is wrong. It identifies repeated formulas that should be distinguished from novel sequences in evaluation.

Sources: [Wave-2 corpus loading](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4b_bootstrap_wave2.py#L425), [combined Key #4A profiles](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4a_ligatures.py#L1294).

## 8. The allograph result is useful and reproducible, with two important limits

I reproduced these committed scores exactly, using the existing selected clusters:

| Model | Lipi five-fold Brown bits/sign | Second-corpus Brown bits/sign |
|---|---:|---:|
| Unmerged | 5.365408 | 5.488435 |
| Pure clusters | 5.301575 | 5.426405 |
| Pure + workshop clusters | 5.296701 | 5.409299 |

The unseen improvement is about **0.0791 bits/sign**, equivalent to roughly **5.3% lower perplexity**. This is real model behavior in the checked data. The implementation also evaluates the original uncollapsed target alphabet through an emission term, a useful protection against the trivial entropy reduction from merely shrinking an alphabet.

However:

**Cluster selection occurs before the cross-validation split.** The pipeline builds distributional profiles from all Lipi events, chooses and classifies candidate pairs, builds the clusters, and only then creates five folds in the prediction suite. The prediction counts are fit on training folds; the cluster discovery has already seen the validation data. A fully held-out five-fold evaluation must refit discovery inside each outer training fold. Frequency-matched random merges do not reproduce the learned model's selection advantage.

**Shared predictive behavior does not prove identical sound.** Two distinct commodities, titles, or functionally related signs can benefit from statistical pooling. Better prediction justifies a useful class or candidate merger. It does not alone justify allographic identity and inheritance of an exact phonetic reading. Conversely, workshop or regional allographs can differ in metadata distribution. The archaeological interpretation needs a separate, preferably blinded palaeographic assessment.

The second-corpus result is a stronger external check than the Lipi cross-validation, but it is affected by cross-catalogue projection and repeated use of that corpus. The repository recognizes part of this problem through a “both-in-new” subset, reporting a smaller effect and P≈0.0355. That sensitivity result is worth preserving rather than replacing with the largest z-score.

Sources: [classification and evaluation sequence](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4d_allographs.py#L1679), [prediction suite](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4d_allographs.py#L1218), [stored scores](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_data/key4d/perplexity_results.json).

## 9. The master merge leaves incompatible readings unresolved

The merge favors earlier tiers and inserts inherited values only when a key is absent. That prevents a newly inherited value from overwriting an earlier assignment, but it does not test whether those assignments are compatible.

Concrete examples:

- Key #4D's accepted workshop cluster groups **390, 405, and 407** as variants of the same tree sign. The master retains **390 = *tai** and **407 = *kōṭi**, with 405 inheriting the 390 interpretation. If 407 is the same sign, distinct sounds require an explicit polyphonic model; if it is a distinct sign, its allograph argument cannot simultaneously certify identity.
- The accepted cluster containing **025, 027, and 028** coexists with **027 = 9** and **028 = 10** in the extended-numeral tier. The master then lets 025 inherit 027's value. The cluster builder's numeral-conflict veto only knows its basic numeral set, so later extended values are not reconciled.

These conflicts do not prove which reading is correct. They show that a merged entry's “locked” status does not certify that its evidence is mutually consistent. Counting it as covered hides that unresolved problem.

Sources: [accepted clusters](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_data/key4d/verified_clusters_all.csv), [master lexicon](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_data/key4_master/master_locked_lexicon.csv), [limited conflict veto](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4d_allographs.py#L970).

**Fix:** represent sign identity, possible sound values, semantic values, and competing analyses separately. Reject or explicitly mark conflicting inheritance before counting a sign as established. Verify conflicts against the complete, current numeral table rather than a baseline subset.

## 10. The metrological distribution does not uniquely determine the claimed ladder

The committed cup-count distribution is `{1:9, 2:126, 3:183, 4:116, 6:3, 7:1}`. Thus 437/438 counts are divisors below 12. This is a notable distribution, especially the absence of five in the assigned cup contexts.

But the same **437/438 = 99.7717%** fit occurs for **24, 36, and 60**. The observed counts alone cannot select 12 over those larger common multiples. A maximum observed count is likewise not proof of a radix or carry boundary.

The later Chola comparison hardcodes the Indus ladder `(8,4,3)` and absolute capacities `[1.16,9.24,37.0,110.9]`, then compares historical systems with random ladders drawn from specified factor and scale pools. It does not independently estimate all those ratios in that comparison. The upstream export also includes manually specified ladder ratios and physical interpretations.

There is a physical lead worth pursuing: three cited whole-jar volumes divided by their stroke counts give similar volumes per stroke, about 9.2 L. I checked how the code uses these numbers, not the original vessel measurements. Three selected vessels and an assumed null over sorted uniform volumes do not establish the entire conversion ladder or the ancient names of its units. The 9.24 L estimate is an average derived from those values; later ladder capacities are mostly propagated ratios, not separate vessel measurements.

A convincing ladder needs repeated conversion or carry evidence, independently measured objects across rungs, uncertainty bounds, and explicit comparison with other bases and administrative mechanisms. A shared metrological ratio would still be evidence about a measurement convention before being evidence of a language family.

Sources: [cup distribution and exported ladder](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_data/met/unit_ladder.csv), [upstream ratio reasoning](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/met_01_ladder.py#L471), [historical comparison](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4c_sangam_epigraphy.py#L1428), [jar-volume calculation](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/met_03_physical.py#L160).

## 11. Sangam matches are conditional on the proposed readings and curated target list

Key #4C takes 19 existing Dravidian sign assignments, adds numeral roots, generates possible compound surfaces through several sandhi rules, and checks a manually assembled Tamil literary/epigraphic word list. It then compares matches with shuffled assignments and matched-size rival lists.

This is a useful consistency check conditional on the input map and target lexicon. It is not an independently transcribed Indus–Tamil bilingual. The target list includes Tamil Lexicon entries, later literary material, Chola usages, and directly attested early inscriptions; these differ in date and evidential status. A dictionary attestation is not automatically Bronze Age evidence.

A concrete matching problem appears in the output: **004-220**, proposed as four + fish, matches **nāḷmīṉ**, glossed as day-star or asterism. The normalizer removes the consonant distinction between the proposed numeral root `nal` and `nāḷ` in the target form. Even if the surface match is permitted by the algorithm, the numeral-four meaning does not establish a day-star reading. Such examples need semantic and historical phonological validation before being counted as a decoded compound.

The strongest new test would freeze a dated lexicon and permissible sound changes before evaluating previously unused inscriptions; it should report exact, phonologically justified, and permissive matches separately. A joint test should also rerun the original selection of the 19 values under the null.

Sources: [normalization and joins](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4c_sangam_epigraphy.py#L32), [curated entries](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4c_sangam_epigraphy.py#L258), [matched compounds](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_data/key4c/test4c1_compound_matches.csv).

## 12. Frontier results require whole-object controls and calibrated provenance claims

The frontier corpus and cuneiform prosopography are useful collections of potential evidence. The report distinguishes several null lexical tests, which is good practice.

Two headline claims need narrower interpretation:

**The BMAC bigram test uses nine transitions from three seals.** Seven of the transitions come from one eight-sign Gonur inscription. Treating these transitions as nine independent observations in a Fisher comparison or shuffling binary transition labels understates within-seal dependence. Whole-seal permutation or a hierarchical model is more appropriate. Matching square BMAC seals against round Gulf seals also does not eliminate shape/genre confounding; it is the very contrast that needs to be matched or modeled. A surviving difference could identify a textual tradition without identifying its spoken language.

I rebuilt the Mainland bigram baseline using the same site exclusions and reproduced the observed **8/9 BMAC versus 12/48 Gulf** counts. I then exhaustively reassigned three of the 19 whole seals to the BMAC group, retaining every seal's transitions together. Using the absolute difference in pooled transition-hit rates, **75 of 969** label allocations were at least as extreme as observed: **P = 0.07740**. This contrasts with the reported transition-level permutation P≈0.0004. The whole-seal result is an explicit sensitivity check under observational exchangeability, not a definitive adjusted P-value for every possible study design; shape and genre differences remain unresolved.

**The 96.37% Iranian Plateau placement is a model score.** It uses five manually selected binary features, a small Iranian sample, smoothing, equal regional priors, and a naive conditional-independence assumption. It also supplies the Mainland cylinder count as a hardcoded approximation of five. The posterior has not been shown to be calibrated on held-out seals of known origin. It should be presented as a tentative feature-based ranking, not a 96.37%-certain provenance determination.

An apparently mainland-like inscription abroad is valuable for testing geographical and functional distribution. Applying the same proposed dictionary to its signs does not create an external phonetic validation. The Gonur gloss is coherent conditional on the dictionary; the seal has no independent translation in this analysis against which that gloss is scored.

Source: [frontier baselines and tests](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4e_museum_archives.py#L1220), [bigram and provenance calculations](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4e_museum_archives.py#L1655).

## 13. The project's own negative controls remain important

The earlier decoy experiment found accepted words passing at **9/58** against decoys at **10/60**. A replay of the flexible research procedure reached **17/29** accepted words against **19/30** decoys. The README also reports a pure-dictionary rival-refit test falling to approximately z=0.69, P=0.258 after hand-selected glosses are removed.

These tests concern earlier word lists and do not automatically refute every newer Key #4 assignment. They demonstrate an important failure mode: the research procedure can produce persuasive external-looking support for wrong words belonging to the same functional class. Newer claims need to show that they overcome this specific failure mode.

The repository deserves credit for preserving these negative results. They are more informative for assessing semantic identification than the mere plausibility of an English gloss. The README currently puts new “locked” claims above older statements that exact sounds remain unestablished. Those statements need a single reconciled account of what evidence changed and which older failure modes were actually retested.

Sources: [decoy study](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/jobs/out/decoy_test.md), [README's negative-results discussion](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/README.md).

## 14. Reproducibility and maintenance need to catch up with the active research

The repository contains two overlapping systems: the older research/campaigns pipeline and the newer work_scripts/work_data investigations. The advertised reproduction workflow mainly checks the older system.

Confirmed engineering issues:

- The Reproduce workflow's path filters omit work_scripts, work_data, and jobs. A commit limited to the current Key #4 work need not trigger that workflow.
- Its sparse checkout also omits those directories, and its headline-number checker targets the older campaign. A green workflow would not establish the current README's latest numbers.
- The documented Python 3.11 environment cannot parse three work scripts: `counted_report_tables.py:19`, `abroad3_05_seals.py:33`, and `odd_3c_rescue.py:52`. These are f-string syntax incompatibilities. They are outside the principal Key #4 path, but the advertised “check every Python file” target would encounter them in a full checkout.
- Key #4C, Key #4D, and the master merge hardcode `/home/antigravity/Cuuper22/ivc`; other scripts derive the root dynamically. The hardcoded scripts need path adaptation to run from a normal checkout.
- Current work scripts use pandas, which is absent from the core requirements file. The core file explicitly describes the older research/embeddings/tools stack rather than the entire current work stack.
- A shared `/tmp/typo_lex` cache has no commit/content validation. `ensure_lexicons` checks file existence. An existing cache from another revision or checkout can be reused without proving its provenance.
- Some reports use local file URLs and stale count descriptions. For example, the allograph report's transition counts differ from the current JSON and the values I reproduced, despite matching the main predictive scores.

Sources: [CI workflow](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/.github/workflows/reproduce.yml), [Makefile](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/Makefile), [requirements](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/requirements.txt), [lexicon cache check](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/work_scripts/key4b_bootstrap_wave2.py#L78).

A portable entry point should build versioned derived data, record the input commit and selected settings, and run the current headline checks. This does not require discarding the exploratory scripts. It requires a small supported path through them.

## 15. The written research rules favor discovery over confirmation

The repository's AGENTS file explicitly permits inspecting all data, tuning after results, and reusing objects during exploration. It also directs agents to redesign negative tests and retain contradictory readings. Those practices can generate hypotheses quickly, provided exploratory findings are subsequently tested independently.

The difficulty is that the reporting layer often calls the resulting findings locked, verified, or proven before that independent stage exists. A deterministic rerun is not the missing confirmation: it reproduces the same choices and the same reuse of data.

This observation concerns the documented process, not the author's motives. I found no basis to conclude that the reproduced numbers were fabricated. The more defensible explanation for the gap is that successful exploration is being reported with the certainty of a confirmatory experiment.

Source: [research rules](https://github.com/Cuuper22/ivc/blob/8259c47fdf4a076f04029254f97c83f04abb139e/AGENTS.md).

## What is worth preserving

The corpus and its crosswalks make concrete comparisons possible. The emphasis on physical object context, sign order, recurring phrases, numeral series, and independent metadata is productive. The allograph scoring avoids a simplistic alphabet-shrinkage comparison, and its key numerical gains reproduce. The record of rechecks and failed hypotheses is useful. Several studies recognize copying, moulded batches, catalogue projection, and object-level deduplication as real issues.

These are foundations for a stronger project. The principal improvement is to make the claims match the measurement: statistical role, candidate meaning, candidate sound, and independent identification must remain distinct.

This distinction is also consistent with the older primary computational literature: [Yadav et al.'s n-gram analysis](https://arxiv.org/abs/0901.3017) studies sign-order regularities. A statistical model of ordered inscriptions can be useful without supplying a phonetic reading.

## A practical validation sequence

1. **Repair and rename the current metrics.** Preserve X identifiers, correct the README figures, and call the resulting measure assigned-value coverage. Add regression examples for `740-X82-740` and X-only faces.
2. **Resolve inventory contradictions.** Review 390/407 and the 025/027/028 cluster first. Make inherited sound values conditional on an unambiguous identity decision. Keep genuine alternatives visible.
3. **Freeze a validation package.** Fix the sign map, lexical sources, senses, permitted phonological operations, grammatical rules, primary outcomes, and exclusions before scoring a fresh dataset.
4. **Refit the full method under controls.** Null runs should include description choice, lexical search, candidate promotion, and any rescue step. For allographs, discover clusters inside outer training folds.
5. **Use the right sampling unit.** Keep faces of the same object, copies from a mould/batch, and closely related text families together where appropriate. Report novel-object and novel-sequence generalization separately.
6. **Test the difficult rivals.** Compare proposed words with alternatives in the same structural class, not merely arbitrary dictionary shuffles. Distinguish a cloth word from another commodity word, a particular title from another title, and a particular phonetic value from a semantic label.
7. **Calibrate the inference.** Run the frozen pipeline on known scripts with hidden readings. Measure how often it recovers correct sign values and falsely declares a wrong language family. Such a benchmark directly tests whether the procedure can decipher, rather than merely find structure.
8. **Seek a discriminating external bridge.** A bilingual, independently transcribed proper name, phonetic complement, or repeated conversion relation could force a choice between incompatible readings. It is not necessary to insist on one particular discovery; it is necessary that a wrong reading make a falsifiable prediction.

The next strongest result would be a small number of values that win these tests. A lower coverage percentage with demonstrated identification would be more persuasive than another large increase generated by assigning values to common signs.
