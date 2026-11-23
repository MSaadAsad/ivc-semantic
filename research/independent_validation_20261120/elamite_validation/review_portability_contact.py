"""Review the small portability witness list and extract prior comparative results."""
import json

import open_rebus as O


def main():
    witnesses=O.R.read(O.OUT/'contact_portability_witnesses.csv')
    reviewed=[]
    for r in witnesses:
        if r['case']=='staff_affection' and r['picture_entry']=='4034' and r['language']=='Tamil':
            decision='rejected_part_of_speech_error'
            reason='Tamil paṟṟu means stick / adhere as a verb in this clause, not a staff or sceptre.'
        elif r['case']=='gate_court' and r['picture_entry']==r['target_entry']=='5354' and r['language']=='Tamil':
            decision='accepted_shared_metonymy' if r['channel']=='equal_conservative_form' else 'same_etymon_variant_not_additional_bridge'
            reason='DEDR5354 explicitly gives doorway / gate and king\'s court. Three variant words and four near pairs are one recorded semantic family.'
        else:
            decision='requires_source_review';reason='Not covered by the present manual review; not promoted.'
        reviewed.append(dict(**r,review_decision=decision,review_reason=reason))
    O.write('contact_portability_review.csv',reviewed)
    assert len(reviewed)==8
    assert sum(r['review_decision']=='accepted_shared_metonymy' for r in reviewed)==3
    assert sum(r['review_decision']=='rejected_part_of_speech_error' for r in reviewed)==1
    # Record existing results without rerunning experiments or changing endpoints.
    old=O.R.read(O.BASE.parent/'expanded_rebus_test/results/summary.csv')
    selected=[r for r in old if r['panel'] in {'fixed48','auto51'} and r['language'] in {'Dravidian','Elamite'}
              and r['mode']=='phon_exact' and r['gate']=='distinct_entry' and r['channel']=='phonetic_plus_polysemy']
    fields=['panel','language','dictionary','entries','n_pairs','both_domains','hits','p_domain','p_entry_sound',
            'p_both_requirements','p_holm_primary7']
    O.write('prior_Dravidian_Elamite_results.csv',[{k:r[k] for k in fields} for r in selected])
    assert len(selected)==4
    leads=O.R.read(O.OUT/'open_rebus_curated_leads.csv')
    bycase={r['case']:r for r in O.R.read(O.OUT/'contact_portability_cases.csv')}
    priority={
      'roof_protection':('investigate discriminating meaning','king / chief','Verify a roof/protection word contemporary with the Indus period; independently distinguish royal title from protection in the same sign contexts.'),
      'jar_enemy':('alternative translation; weak loan lead at present','house','Establish that inscriptions concern enemies rather than households; explain -r encoding and attest the jug word early. A different proposed meaning alone is not borrowing evidence.'),
      'gate_court':('shared semantic bridge; low donor specificity','No unique representative Lipi mapping','The same gate/court extension is recorded in Tamil. Elamite hi-el/hu-el and Tamil vāyil/vācal/vāyal are not the same recovered Indus sound.'),
      'gate_support':('recover original source first','No unique representative Lipi mapping','Legacy royal-support gloss is truncated/tentative; verify its meaning, period and possible donor before proposing an Indus loan.'),
      'seed_descendants':('generic metaphor; low donor specificity','bangle at representative790; youth/scion at760','The narrow Dravidian screen did not recover this exact bridge. A seed/offspring metaphor by itself does not identify an Elamite donor.'),
      'staff_affection':('Akkadian-confounded; weak sound bridge','smith / older ruler','Elamite sceptre entry carries cognate flag ḫaṭṭu; ORACC records Akkadian haṭṭu/ḫa-at-ti for sceptre/staff. Verify donor and gemination; do not label uniquely Elamite.'),
      'cup_ear':('late uncertain lexical source; low priority','Alternative interpretation of a cup/jar picture','Verify bowl sense, consonant distinction and early ear attestation; current target gloss is Achaemenid.'),
      'cup_true':('late uncertain lexical source; low priority','Alternative interpretation of a cup/jar picture','Same uncertainties as cup/ear; true/correct is a separate proposed meaning, not a second confirming inscription.'),
    }
    ledger=[]
    for r in leads:
        status,current,next_step=priority[r['id']]
        accepted=sorted({x['language'] for x in reviewed if x['case']==r['id'] and x['review_decision']=='accepted_shared_metonymy'})
        ledger.append(dict(case=r['id'],meaning_bridge=r['title'],representative_sign=r['lipi'],
                           Cuper_comparison=current,Dravidian_raw_exact_languages=bycase[r['id']]['exact_languages'],
                           Dravidian_reviewed_exact_languages='; '.join(accepted),
                           Elamite_dates=r['dates'],Elamite_limitations=r['limits'],
                           contact_research_status=status,next_discriminating_evidence=next_step,
                           borrowing_demonstrated=False))
    O.write('nonoverlap_loan_research_ledger.csv',ledger)
    summary=dict(automatic_exact_directions=2,reviewed_shared_directions=1,
                 shared_direction='gate_court',shared_DEDR_entry='5354',shared_language='Tamil',
                 same_meaning_normalized_Elamite_Dravidian_form_witnesses=0,
                 false_positive_removed='staff_affection / paṟṟu / DEDR4034: verb stick, not noun staff',
                 seven_other_directions_status='No reviewed exact bridge recovered under the fixed semantic heads; not proof of language absence or Elamite uniqueness.',
                 implication='Shared metonymy reduces donor specificity. Non-overlap identifies competing meanings to test, not loanwords.',
                 established_Indus_loanwords=0,posterior_language_odds=None,colab_units=0)
    (O.OUT/'contact_review_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
