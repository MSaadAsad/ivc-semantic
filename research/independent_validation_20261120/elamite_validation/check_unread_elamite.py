"""Scope, genuine gaps, picture support and exact source-context checks."""
import json

import open_rebus as O
import unread_elamite as U


def main():
    master={r['sign'] for r in O.R.read(O.BASE.parent/'translation_catalogue/results/all_163_sign_readings.csv')}
    rows=O.R.read(O.OUT/'unread_Elamite_rebus_candidates.csv')
    assert len(rows)==48 and len({r['sign'] for r in rows})==25
    assert all(r['sign'] not in master and r['canonical_sign'] not in master for r in rows)
    assert all(r['sign'] not in {'482','740','142','790'} for r in rows)
    assert U.noun_votes('door:3','door')==3
    assert U.noun_votes('ladder:2;abstract:1','roof')==0
    focus=O.R.read(O.OUT/'unread_focus_candidates.csv')
    assert {r['sign'] for r in focus}=={'621','362','572','360','202','484'}
    assert next(r for r in focus if r['sign']=='484')['drawing_support_filter']=='False'
    assert all(r['drawing_support_filter']=='True' for r in focus if r['sign']!='484')
    occurrences=O.R.read(O.OUT/'unread_candidate_occurrences.csv')
    assert len(occurrences)==len({(r['candidate_sign'],r['catalogue'],r['face_id']) for r in occurrences})==348
    assert {r['candidate_sign'] for r in occurrences}=={r['sign'] for r in rows}
    h=next(r for r in occurrences if r['candidate_sign']=='362' and r['catalogue']=='Lipi' and r['reference']=='H-345')
    assert h['sign_sequence']=='362-740-090' and h['existing_proposed_translation']=='Manager of the [362] house.'
    assert h['city']=='Harappa' and '4269550' in h['found_at']
    profiles=O.R.read(O.OUT/'unread_candidate_profiles.csv')
    p=next(r for r in profiles if r['sign']=='621' and r['catalogue']=='Lipi')
    assert p['face_records']=='18' and p['last_position_faces']=='13'
    summary=json.loads((O.OUT/'unread_Elamite_summary.json').read_text())
    assert summary['unresolved_sign_ids']==541 and summary['unresolved_signs_with_literal_anchors']==66
    assert summary['established_borrowings']==summary['validated_new_translations']==0
    print('PASS: 48 gap-candidate rows/25 unresolved IDs, all canonical values absent from key, six qualified focus signs, all348 contexts, original H-345 blank and location,621 position counts, zero claimed borrowings or full translations. Colab0.')


if __name__=='__main__':main()
