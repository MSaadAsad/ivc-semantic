#!/usr/bin/env python3
"""Prepare unscored blinded evidence/reading materials, with a separate key.

Preparation is complete; no independent panel has yet annotated these materials.
"""
import csv,json,random
from collections import Counter
import validate as v

def main():
    rng=random.Random(v.SEED+99); signs=v.SIGNS[:];rng.shuffle(signs); labels={s:'G%03d'%(i+1) for i,s in enumerate(signs)}
    contrasts=v.read('research/independent_validation_20261120/results/all_sign_artifact_contrasts.csv')
    tables=v.read('research/independent_validation_20261120/results/sign_evidence_45.csv')
    cards=[]
    for r in sorted(tables,key=lambda r:labels[r['sign']]):
        s=r['sign']; counts=[{k:c[k] for k in ['catalogue','target','a','b','c','d']} for c in contrasts if c['sign']==s]
        cards.append({'blind_sign':labels[s],'geometry_description':r['shape'],'intact_tokens':int(r['intact_tokens']),'initial_tokens':int(r['initial_tokens']),'final_tokens':int(r['final_tokens']),'possible_stroke_adjacent_tokens':int(r['numeral_adjacent_tokens']),'artifact_count_tables':counts,'instructions':'Assign at most a broad function from archaeological/distributional evidence. Give multiple alternatives. Do not use language dictionaries or proposed readings. Record which observation could distinguish alternatives. Do not equate administrative object association with tax or title.'})
    (v.BASE/'frozen/blinded_evidence_cards.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2)+'\n')
    readings=v.read('research/independent_validation_20261120/results/inscription_tests_60.csv'); rivals=json.loads((v.BASE/'frozen/rival_vocabularies.json').read_text());donors=rivals[0]['donor_by_sign']; tasks=[];key=[]
    for row in readings:
        for genuine in (True,False):
            seq=v.tok(row['exact_sequence']); chosen=next((r['donor_by_sign'] for r in rivals if any(v.LEX[r['donor_by_sign'][s]]['root_or_gloss']!=v.LEX[s]['root_or_gloss'] for s in seq)), donors); literal=' ; '.join(v.LEX[s if genuine else chosen[s]]['root_or_gloss'] for s in seq)
            tasks.append({'candidate_id':'','literal_values':literal,'required_response':'State one precise external archaeological prediction and the strongest alternative. Rate grammatical/compositional support 0–4 and identify every supplied assumption. Fluency alone does not count. No outcome has yet been scored.'}); key.append({'test_id':row['test_id'],'proposed_mapping':genuine,'identical_to_proposal':all(v.LEX[chosen[s]]['root_or_gloss']==v.LEX[s]['root_or_gloss'] for s in seq) if not genuine else True})
    order=list(range(len(tasks)));rng.shuffle(order);out=[];outkey=[]
    for i,j in enumerate(order):
        tasks[j]['candidate_id']='B%03d'%(i+1);out.append(tasks[j]);outkey.append(dict(candidate_id=tasks[j]['candidate_id'],**key[j]))
    with (v.BASE/'frozen/blinded_reading_tasks.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator="\n");w.writeheader();w.writerows(out)
    (v.BASE/'frozen/blind_key_do_not_give_raters.json').write_text(json.dumps({'sign_key':{x:s for s,x in labels.items()},'reading_key':outkey},indent=2)+'\n')
    v.save('blinded_materials_status.json',{'cards':len(cards),'reading_tasks':len(out),'raters_recruited':0,'ratings_observed':0,'strictly_identical_decoy_sequences':sum(k['identical_to_proposal'] for k in outkey if not k['proposed_mapping']),'independence':'No claim of blinding accomplished; prepared materials must be reviewed by a curator. Geometry can reveal sign identity to familiar experts. Full artifacts/contexts need separate source authentication.'})
    print('Prepared',len(cards),'cards and',len(out),'unscored reading tasks')
if __name__=='__main__':main()
