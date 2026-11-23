"""Compare the four representative sign hypotheses and substitute labels in texts.

This is a reference exercise, not an Elamite parser or translation validator.
"""
import collections
import json

import open_rebus as O

VALUES={
    '482':('protection','king / chief / leadership','related authority theme; different lexical meaning'),
    '740':('enemy','house','different'),
    '142':('affection','smith; older candidate variants include ruler / king','different'),
    '790':('descendants','bangle','different'),
}


def main():
    master={r['sign']:r for r in O.R.read(O.BASE.parent/'translation_catalogue/results/all_163_sign_readings.csv')}
    leads={r['lipi']:r for r in O.R.read(O.OUT/'open_rebus_curated_leads.csv') if r['lipi']}
    comparison=[]
    for sign,(target,label,overlap) in VALUES.items():
        m=master[sign];lead=leads[sign]
        comparison.append(dict(sign=sign,picture=lead['title'].split(' → ')[0],
                               Elamite_candidate=target,Cuper_proposal_label=label,
                               Cuper_raw_meaning=m['proposed_meaning'],Cuper_raw_root=m['proposed_root'],
                               Cuper_source=m['proposal_source'],semantic_overlap=overlap,
                               lead_id=lead['id'],Elamite_limitations=lead['limits'],
                               status='Neither reading independently established; comparison of proposals.'))
    O.write('same_sign_meaning_comparison.csv',comparison)
    inscriptions=[r for r in O.R.read(O.BASE.parent/'translation_catalogue/results/all_inscriptions.csv') if r['catalogue']=='Lipi']
    complete=[];tail=[]
    for r in inscriptions:
        seq=r['sign_sequence'].split('-')
        if len(seq)>=2 and set(seq)<=VALUES.keys():
            complete.append(dict(**{k:r[k] for k in ['catalogue','face_id','reference','sign_sequence','city',
                                                      'found_at','material','object_type','existing_proposed_translation']},
                                 candidate_English_labels=' — '.join(VALUES[s][0] for s in seq),
                                 implied_relations_supplied=False,Elamite_grammar_validated=False,
                                 status='Candidate English-label substitution only; not an Elamite translation.'))
        if any(seq[i:i+2]==['482','740'] for i in range(len(seq)-1)):tail.append(r)
    O.write('candidate_label_sequences.csv',complete)
    summary=dict(representative_signs=4,identical_same_sign_meanings=0,
                 semantic_scope='Four representative sign assignments, not all words of either language.',
                 fully_candidate_labelled_Lipi_faces=len(complete),
                 unique_multi_sign_formulas=len({r['sign_sequence'] for r in complete}),
                 formulas=dict(collections.Counter(r['sign_sequence'] for r in complete)),
                 ordered_482_740_Lipi_faces=len(tail),ordered_482_740_unique_formulas=len({r['sign_sequence'] for r in tail}),
                 validated_Elamite_translations=0,grammar_test_run=False,
                 note='Existing catalogue wording can predate the current master proposal. No connecting English words, verbs or class endings were inferred.',
                 colab_units=0)
    assert len(complete)==4 and summary['unique_multi_sign_formulas']==3
    assert summary['formulas']=={'482-740':2,'142-740':1,'740-790':1}
    assert all(not r['Elamite_grammar_validated'] and not r['implied_relations_supplied'] for r in complete)
    (O.OUT/'meaning_comparison_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
