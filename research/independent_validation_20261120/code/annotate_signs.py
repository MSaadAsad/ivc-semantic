#!/usr/bin/env python3
"""Explicit inferential judgments, kept separate from measured observations."""
import json
import validate as v
NOTES={
'740':('Strong terminal/classifying function; household/genitive sense unresolved','Link independent objects to households established without reading seals; compare a terminal-classifier model.'),
'002':('Two-stroke quantity notation plausible; slot/category uses require separation; sound unestablished','Find independently counted quantities, including contexts distinguishing the short and tall two-stroke signs.'),
'700':('Quantity-associated function plausible; cup, ration and unit remain rivals','Predict independently measured vessel capacities or ration quantities; test other bases and container classes.'),
'032':('Two-stroke quantity notation plausible; name compounds can fix its value','Compare independent quantities and formulaic/name contexts against short two-stroke sign 002.'),
'033':('Three-stroke quantity notation plausible; spoken form unestablished','Predict external quantities and distinguish literal amount from fixed ordinal or formula element.'),
'400':('Strong object/terminal association; junior or subordinate is a weak specific inference','Predict externally recorded rank/status after length, city, artifact type and workshop controls.'),
'220':('Fish-shaped sign plausible; star, clan and spoken value unestablished','Find independent astral association or a forced syllabic/bilingual correspondence excluding fish commodity/emblem.'),
'240':('Modified-fish class plausible; rays/bright-star reading unestablished','Show the modification predicts an independently identified semantic contrast, without choosing its Dravidian word.'),
'520':('Ending/classifier function plausible; chief and spear sound unestablished','Predict independent office/status evidence against another title, name ending or artifact-series marker.'),
'390':('Counted item or administrative category plausible; textile sense remains a hypothesis','Predict fibres/residues on new associated packages against botanical and institutional alternatives.'),
'861':('Heading/quantity-associated role plausible; exact share or weight unresolved','Recover independent weight/share relations and distinguish them from an institution/heading classifier.'),
'003':('Three-stroke numerical interpretation plausible; phonetic word unvalidated','Test externally known quantities rather than counting how many strokes are drawn alone.'),
'001':('Single-stroke numerical interpretation plausible; ordinal/name uses remain possible','Demonstrate independent cardinal relations in contexts where single-stroke use is not a fixed formula.'),
'820':('Quantity/heading role plausible; quarter is not established by wheel rebus','Predict exact independent quarter conversions and compare nonfractional unit and institution models.'),
'235':('Modified-fish grouping plausible; bright-star is speculative','Use independent imagery or complements to distinguish bright, roofed, institutional and name variants.'),
'031':('Single tall-stroke count interpretation plausible; sound unestablished','Compare independently known amounts and fixed-name usage with the short-stroke series.'),
'060':('Connector/medial role plausible; in/of and its sound unresolved','Test an independently segmented relation that separates locative, genitive, title connector and classifier.'),
'590':('Container/bundle or administrative identifier plausible; textile bale unresolved','Predict new package contents or bundle marks, excluding general commodity and institutional alternatives.'),
'741':('Graphic relation to 740 plausible; one-house semantics unestablished','Show the added stroke predicts an independently counted institution/unit rather than a different vessel or class.'),
'615':('Replicated copper-tablet association strong under this model; loom/plot unresolved','Distinguish textile workshop, land registry, commodity and tablet-series outcomes on new contextual evidence.'),
'705':('Quantity/measure-related use plausible; ship and exact capacity unresolved','Predict new unit conversions and maritime function separately; do not let one ambiguous word satisfy both.'),
'176':('Administrative/category function plausible; tribute/tax unresolved','Specify an outcome unique to taxation versus ownership, licensing, allocation or institutional identity.'),
'817':('Distributional relationship to 861 testable; inherited share sound unvalidated','Source-authenticate graphic identity and test interchangeable versus contrasting quantitative values.'),
'090':('Human/person or ending role plausible; manager/agent not identified','Use independent agency/ownership links to distinguish a person marker from a specific office.'),
'233':('Fish-variant/name role plausible; dawn/split-star word unestablished','Test a modification-specific semantic prediction outside the dictionary bridge.'),
'034':('Four tall strokes suggest numerical role; exact spoken form unestablished','Compare independent cardinal quantities, units and fixed fish/name constructions.'),
'415':('Directional modifier/compound behavior plausible; branch/control word unresolved','Predict a distinct modifier meaning on new objects; name modifier and office qualifier remain rivals.'),
'920':('Heading/calendar hypothesis testable; moon-to-month sense unestablished','Predict dates or independently known periodicity rather than a recurring opener alone.'),
'405':('Possible relation to tree-sign family; shared textile value unvalidated','Verify graphically and quantitatively whether it contrasts with or substitutes for 390 and 407.'),
'407':('Copper-tablet association strong; new-cloth is not thereby identified','Test new textile evidence against commodity, estate, workshop and botanical readings.'),
'806':('Agricultural/commodity hypothesis plausible; millet specifically unestablished','Predict independently identified crop remains or residues against other grain/plant and institutional alternatives.'),
'798':('Recurring institutional/name relation plausible; bound-guild is speculative','Seek independent multi-party or corporate linkage, compared with a proper-name or generic classifier.'),
'255':('Pictorial/emblem interpretation possible; principal/first depends on unverified rebus','Test independent ordinal/status relations against crocodile emblem and tablet-series interpretations.'),
'803':('Relationship to 806 is testable; inherited millet meaning unvalidated','Confirm allography and independently identify crop/commodity distinctions.'),
'100':('Personal/tag/title role possible; head/chief sound and sense unresolved','Predict independent office/status evidence, separating name tag from rank.'),
'550':('Place/institution or opener hypothesis plausible; district not established','Predict independent geographical jurisdiction against institution and name-heading alternatives.'),
'845':('Copper-tablet association strong; tax word unestablished','Find an external feature that distinguishes tax from commodity, ritual token, workshop and series class.'),
'142':('Replicated copper-tablet association strong; staff-holder/blacksmith alternatives unresolved','Predict independent metallurgical or office context with staff imagery and language dictionaries withheld.'),
'595':('Copper-tablet association in second corpus survives; tax-marked bale unresolved','Test new commodity/series and fiscal outcomes that distinguish hatching from a tax modifier.'),
'482':('Modifier/ending association possible; king is a weak specific inference','Predict independent rank evidence and compare institution and name-suffix assignments.'),
'335':('Quantity/unit-chain hypothesis plausible; named grain-bin unit unvalidated','Predict independently measured conversions involving this sign, including a rival unit or container model.'),
'171':('Weight/load or unit hypothesis plausible; standard and sound unestablished','Predict independently measured weights or quantities beyond stroke adjacency.'),
'480':('Measure/container hypothesis plausible; exact unit unresolved','Test independent measured capacities/weights and a nonunit commodity classifier.'),
'350':('Enclosure/settlement/pastoral hypotheses open; watchman or cattle-yard unestablished','Predict independently recorded settlement, animal or office context under same-role alternatives.'),
'540':('Vessel/quantity hypothesis plausible; drum-derived capacity word unestablished','Predict new capacities or vessel marks against drum emblem, commodity and generic unit readings.')}
def main():
    rows=v.read('research/independent_validation_20261120/results/sign_evidence_45.csv');assert set(NOTES)==set(v.SIGNS)
    for r in rows:r['confidence'],r['required_discriminator']=NOTES[r['sign']]
    v.csvout('sign_evidence_45.csv',rows)
    (v.BASE/'frozen/analyst_sign_judgments.json').write_text(json.dumps({'status':'Retrospective interpretive judgments, not blinded semantic assignments','notes':NOTES},ensure_ascii=False,indent=2)+'\n')
    cols=['sign','proposed_root','strongest_supporting_observation','strongest_counterevidence','alternatives','confidence','required_discriminator'];lines=['# Evidence and alternatives for 45 signs','','All numeric evidence is extracted without phonetic readings. The frozen proposed roots are hypotheses. Interpretive judgments were made after seeing the project and are not independent blinded semantic assignments. Full 540-contrast and max-T outputs accompany this table.','','| Sign | Proposed root | Supporting observation | Counterevidence / limit | Alternatives | Calibrated assessment | Discriminating evidence needed |','|---|---|---|---|---|---|---|']
    for r in rows:lines.append('| '+' | '.join(str(r[k]).replace('|',' / ').replace('\n',' ') for k in cols)+' |')
    (v.BASE/'reports/sign_evidence.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
