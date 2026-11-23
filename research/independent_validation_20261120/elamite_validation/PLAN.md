# Structured Elamite check

22 November 2026. This extends the already completed Elamite dictionary/rebus comparisons. The additional input is the DigitalPasts ALP-MEGA2024 structured CSV release, pinned in `inputs/source_files.json`. The source headers and sample rows were inspected before this plan; scores have not been calculated. This is retrospective exploratory research, not independent assignment of Indus meanings.

Use all six previously frozen panels, comprising 178 overlapping pair formulations, without altering concept patterns. The primary rebus panel remains the 48 fixed picture/meaning pairs. Ask whether Elamite words for the two concepts share a normalized form; retain the actual words and meanings for every witness. A missing concept is missing coverage, not a linguistic refutation.

Also test the 67 previously frozen root/concept claims, including 48 paired, nine literal and ten numerical claims. Use their unchanged proposed Dravidian forms, the target side for paired claims and the literal side otherwise. This asks whether a proposed form resembles an Elamite equivalent with the same meaning. It does not assign new Indus readings. Retain all 163 current signs in a scope inventory, with untested signs distinguished from tested cases. Repeated inscriptions are not independent lexical observations.

## Inputs and exclusions

Inspect all retrieved source categories. Admit noun, verb, adjective, other and unclassified rows to the common-vocabulary screen; exclude personal/geographical/divine names, magic and scribal errors. The personal-name file is above the connector file-size limit and is not needed for these tests. Verify retrieved bytes against published Git blob identifiers. Cache raw input outside the research repository and provide a pinned download script.

The release's English lexical hints are largely in `morphology`, not `semantics`. Do not treat every populated morphology field as a root or English definition. Remove only explicitly uppercase grammatical suffixes to recover a lexical head. Match whole lexical heads or separately listed comma/semicolon/slash senses against frozen patterns; do not count “bastard” as “star”, “mischief” as “chief”, “grain.handler” as “grain”, a month-name category as the word “month”, or a transliterated stem in the morphology field as a translated meaning. Preserve uncertain gloss flags.

Primary readable-form screening excludes transliterations with damage/uncertainty, determinative/compound dots, all-capital logograms or unexplained punctuation. Only hyphens, transliteration indices and accents are normalized; fold vowel length and repeated vowels across syllabic spelling. Retain consonant diacritics. A separate ASCII-folded sensitivity can collapse those distinctions. No undocumented consonant substitutions or arbitrary root stripping. Inflected spellings are not called independent reconstructed roots. Deduplicate identical form/lexical-head pairs.

Use four pools: all eligible common-vocabulary rows; the same excluding nonempty `cognate` flags; non-Achaemenid-attested unflagged rows; and Old-Elamite-labelled unflagged rows. A `cognate` flag is a source warning, not a complete loanword classification. Unflagged does not mean proven native. Old Elamite labels are broader than the mature Indus period and do not establish a third-millennium attestation for each word.

## Scoring and chance controls

Primary pool: unflagged rows across all source periods. Primary rebus score: number of fixed-48 claims with two different lexical heads sharing a consonant-preserving normalized form. Report whole-head coverage and explicit witnesses, including zero-coverage pairs. Compare with 9,999 target-side permutations and 9,999 form reassignments within part-of-speech/length strata. The other five frozen panels and three pools are sensitivity analyses. Do not count repeated senses of the same head as separate word support.

Primary direct-affinity score: average best normalized edit similarity between the unchanged proposed form(s) and same-meaning Elamite forms on covered claims. Also report exact-form hits. Use 9,999 permutations of target concepts among covered nonnumeral claims, with numerals permuted separately; retain full target synonym sets together. Report the actual number of covered claims and the unique concept/form coverage. This is spelling-based candidate screening; edit similarity is not an established historical sound correspondence. Exact consonant-preserving and ASCII results must be kept separate.

Correct the four primary p-values (rebus target, rebus sound, direct similarity, direct exact) together with Holm's procedure. Release all prespecified sensitivity results, without promoting the smallest p-value after inspecting them. An unrelated-language dictionary comparison may be reported descriptively if existing clean lexical pools are available, with coverage differences and selection limitations explicit; it does not replace the Elamite chance controls.

No Elamo-Dravidian historical sound-law test is claimed without an independently specified, source-verified correspondence table. McAlpin's prior comparisons are background, not fresh IVC evidence. No result here establishes that an Indus sign has its proposed meaning, or that Elamite–Dravidian common ancestry is true or false.

## Validation

Check source identity/counts, exclusion of named/logographic/damaged entries, exact whole-head semantics, non-reuse of duplicate form/head pairs, known synthetic matches/nonmatches and the two chance baselines. Run locally only if comfortably below the repository's two-minute compute limit; otherwise use the prescribed compute route. Report actual runtime and Colab usage.

## Subsequent scope correction

The user clarified that the objective is Elamite as an Indus language, not Elamite–Dravidian affinity. The direct-form comparison above is therefore off target for the requested objective. Its results are retained as an archive, not presented as an Elamite–IVC test. The rebus component is relevant only to the particular existing meaning-pair assignments, not to every possible Elamite reading. A full direct model must allow Elamite pronunciations and alternative semantic assignments, and predict inscriptions excluded from fitting. Existing repository QAP, grammar-fit and Linear-Elamite sound-transfer work must be credited before proposing an extension. No new numerical analysis was run for this correction.
