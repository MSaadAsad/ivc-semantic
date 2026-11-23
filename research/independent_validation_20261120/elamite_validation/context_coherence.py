"""One-candidate-at-a-time English gap fills and qualitative context review.

No semantic score, language identification or borrowing probability is calculated.
"""
import collections
import json
import re

import open_rebus as O

LABELS={'362':'royal court','621':'royal court','572':'royal court','360':'royal court',
        '202':'offspring/descendants','484':'protection'}


def fill(text,sign):
    replacement='['+LABELS[sign]+'?]'
    text=re.sub(r'\['+sign+r'\]',lambda _:replacement,text)
    text=re.sub(r'Name\([^()]*·'+sign+r'\)',lambda _:replacement,text)
    if sign=='621':
        text=text.replace('Barred-Tablet [registrar title]',replacement)
        text=re.sub(r'\bstored\b',lambda _:replacement,text,flags=re.I)
    if sign=='202':text=text.replace('Botanical[202]',replacement)
    return text


def assessment(sign,seq):
    following=[seq[i+1] for i,s in enumerate(seq[:-1]) if s==sign]
    if sign=='362':
        if ['362','740','090']==seq[-3:]:
            return 'compatible_institutional_gap','Court can qualify the proposed house/manager phrase. Temple, guild or another institution could also fit; no unique identification.'
        if '861' in following:
            return 'compatible_institutional_gap','Court plus proposed tribute is intelligible. Temple tribute is a rival English interpretation; no relation or Elamite sound is established.'
        if '740' in following:
            return 'compatible_but_incomplete','Court could qualify the proposed house; other words and relations remain uncertain.'
        return 'not_resolved','Unknown neighbours or damage prevent a clear interpretation; replacing the label alone does not explain the text.'
    if sign=='621':
        if len(seq)==1:return 'not_discriminating','A single sign does not distinguish court, registrar, stored or another function.'
        return 'institutional_alternative_not_unique','Court is compatible with a broad administrative interpretation. Stored/registrar and other institutional labels remain rivals; no for/of relation is supplied.'
    if sign=='202':
        if '400' in following:
            return 'compatible_kinship_gap','Offspring next to proposed junior is compatible with a person/kinship reading. Repeated and damaged versions are not independent semantic confirmations.'
        if '645' in following:
            return 'meaning_not_clarified','Offspring followed by proposed gold weight does not itself clarify the phrase; adding family-owned, inheritance or a personal-name interpretation would require evidence.'
        return 'not_resolved','The longer label sequence is not explained by inserting offspring; no kinship relation is recovered.'
    if sign=='484':
        if '400' in following:
            return 'agent_noun_not_established','Protection plus proposed junior is not automatically junior guard. Guard/protector would add an agent meaning absent from this candidate.'
        return 'no_clear_semantic_gain','Protection leaves name-like/unknown compounds and grammatical relations unresolved; roof identification is also weak.'
    if sign=='572':
        return 'compatible_but_not_specific','Court could be an institutional element before the proposed ward/house/manager frame; it does not outperform a generic institution or name label here.'
    return 'no_clear_semantic_gain','Court supplies no clear account of the varied count/opening/name-like contexts. The existing allowance/quantity interpretations are themselves provisional.'


def main():
    rows=[r for r in O.R.read(O.OUT/'unread_candidate_occurrences.csv') if r['candidate_sign'] in LABELS]
    out=[]
    for r in rows:
        sign=r['candidate_sign'];seq=r['sign_sequence'].split('-')
        kind,note=assessment(sign,seq)
        out.append(dict(**r,candidate_label=LABELS[sign],
                        illustrative_gap_fill=fill(r['existing_proposed_translation'],sign),
                        context_assessment=kind,assessment_reason=note,
                        assessment_scope='Retrospective qualitative reading of conditional English labels; not a validated semantic score.'))
    O.write('coherence_all_shortlisted_contexts.csv',out)
    counts=[]
    for sign in LABELS:
        for cat in ['Lipi','Mahadevan']:
            rr=[r for r in out if r['candidate_sign']==sign and r['catalogue']==cat]
            counts.append(dict(sign=sign,catalogue=cat,sign_face_rows=len(rr),unique_formulas=len({r['sign_sequence'] for r in rr})))
    O.write('coherence_scope_counts.csv',counts)
    summary=dict(shortlisted_signs=6,sign_catalogue_face_rows=len(out),
                 sign_formula_pairs=len({(r['candidate_sign'],r['sign_sequence']) for r in out}),
                 original_source_readings_preserved=True,one_candidate_changed_at_a_time=True,
                 inserted_relations_or_verbs=False,semantic_score_calculated=False,
                 control='Qualitative generic-institution rival for court; no blinded ratings or fresh predictions.',
                 finding='362 is the clearest conditional institutional fit; no demonstrated comparative or global coherence gain.',
                 new_validated_readings=0,colab_units=0)
    assert len(out)==127 and summary['sign_formula_pairs']==93
    assert fill('Manager of the [362] house.','362')=='Manager of the [royal court?] house.'
    assert fill('[360]-[362] house.','362')=='[360]-[royal court?] house.'
    assert fill('Stored of the house.','621')=='[royal court?] of the house.'
    assert all(r['existing_proposed_translation'] and r['found_at'] for r in out)
    assert any(r['candidate_sign']=='202' and r['reference']=='M-1762' and r['context_assessment']=='meaning_not_clarified' for r in out)
    (O.OUT/'coherence_review_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
