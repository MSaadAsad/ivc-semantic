"""Search the eight selected Elamite semantic bridges in 22 Dravidian sources.

No language-identification odds, borrowing direction or fresh reading is inferred.
"""
import argparse
import collections
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import time

import open_rebus as O

spec=importlib.util.spec_from_file_location('ivc_portability',O.BASE.parent/'ivc_language_test/analyze.py')
D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)
sys.path.insert(0,str(O.REPO/'work_scripts'))
import key2a_rebus_lock as K

# Fixed in COMPARISON_CONTACT_PLAN.md before the screen was scored.
CASES=[
 ('roof_protection',['roof'],['protection','protect','guard','shelter'],['ku-uk'],['ku-uk']),
 ('jar_enemy',['jar','jug','pot','pitcher','waterpot'],['enemy','foe'],['pi-ti'],['pi-ti-ir','piti']),
 ('gate_court',['gate','door','portal'],['royal court',"king's court",'palace'],['hi-el','hu-el'],['hi-el','hu-el']),
 ('gate_support',['gate','door','portal'],['support','aid','assistance'],['zi-ip'],['zi-ip']),
 ('seed_descendants',['seed'],['descendant','descendants','offspring','progeny'],['pa-ar'],['pa-ar']),
 ('staff_affection',['staff','sceptre','scepter','stick'],['affection','love'],['ha-at-ti'],['ha-ti']),
 ('cup_ear',['cup','bowl','goblet'],['ear'],['si-ir-ri'],['si-ri']),
 ('cup_true',['cup','bowl','goblet'],['true','correct','truth'],['si-ir-ri'],['si-ri']),
]


@functools.lru_cache(None)
def heads(gloss):
    if re.match(r'^(?:see|cf\.)\s',gloss.lower()):return frozenset()
    gloss=re.split(r'\b(?:DED|DEDS|DEDR)\b',gloss)[0]
    hh=set()
    for clause in K.clean_gloss_clauses(gloss):
        for part in re.split(r'\s*,\s*|\s*/\s*',clause):
            part=re.sub(r'^(?:(?:n|v|adj|adv)\.\s*|(?:a|an|the|to)\s+)+','',part.strip())
            if part:hh.add(part.strip(' .?!'))
    return frozenset(hh)


def matched(hh,terms):
    return sorted(h for h in hh if h in terms or h.endswith('s') and h[:-1] in terms)


def allowed_variant(v):
    return len(O.R.norm(v))>=2 and all(c.isalpha() or c in '-.\u0300\u0301\u0304\u0324\u0331' for c in v)


def form_rows(rows,terms):
    result=collections.defaultdict(list)
    for r in rows:
        mm=matched(heads(r['gloss']),terms)
        if not mm:continue
        for variant in D.variants(r['headword']):
            if allowed_variant(variant):
                result[O.R.norm(variant)].append(dict(**r,matched_heads='; '.join(mm),variant=variant))
    return result


def witness(case,language,channel,a,b,key):
    fields=['headword','gloss','source','row','entry','flag','citation','notes','matched_heads','variant']
    return dict(case=case,language=language,channel=channel,key=key,
                **{'picture_'+k:a[k] for k in fields},**{'target_'+k:b[k] for k in fields},
                same_source_record=(a['source'],a['row'])==(b['source'],b['row']),
                both_unmarked=a['flag']=='unmarked' and b['flag']=='unmarked')


def main(cache_root):
    started=time.monotonic()
    manifest=json.loads((D.BASE/'sources.json').read_text());cache=cache_root/manifest['commit']
    # Reuse the pinned source corpus; verify every consumed tabular/alias file.
    consumed=['data/dedr/dedr_new.csv','data/dedr/abbrevs.py']
    consumed += [str(p.relative_to(cache)) for p in sorted((cache/'data/other/forms').glob('*.csv')) if p.name!='20230416-northern.csv']
    indexed={r['path']:r for r in manifest['files']}
    for p in consumed:assert hashlib.sha256((cache/p).read_bytes()).hexdigest()==indexed[p]['sha256'],p
    malto=cache_root/'TGM2017.pdf'
    m=next(x for x in manifest['additional_sources'] if Path(x['path']).name=='TGM2017.pdf')
    assert hashlib.sha256(malto.read_bytes()).hexdigest()==m['sha256']
    rows,source_counts,_=D.load(cache,malto)
    vocab={l:[r for r in rows if r['language']==l] for l in D.LANGS}
    detail=[];witnesses=[];contacts=[];meaning_inventory=[]
    for case,a_terms,b_terms,el_a,el_b in CASES:
        for language in D.LANGS:
            aa=form_rows(vocab[language],a_terms);bb=form_rows(vocab[language],b_terms)
            exact=set(aa)&set(bb)
            unmarked={k for k in exact if any(r['flag']=='unmarked' for r in aa[k]) and any(r['flag']=='unmarked' for r in bb[k])}
            near=[]
            for a in aa:
                for b in bb:
                    if a==b or min(len(a),len(b))<4 or abs(len(a)-len(b))>1 or O.onset(a)!=O.onset(b):continue
                    if O.R.distance(a,b)==1:near.append((a,b))
            for channel,kk in [('equal_conservative_form',[(k,k) for k in sorted(exact)]),('one_edit_conservative_form',sorted(near))]:
                for a,b in kk:
                    for x in aa[a]:
                        for y in bb[b]:witnesses.append(witness(case,language,channel,x,y,a+' / '+b))
            for side,index,elforms in [('picture',aa,el_a),('target',bb,el_b)]:
                for word in elforms:
                    key=O.R.norm(word)
                    for r in index.get(key,[]):
                        contacts.append(dict(case=case,language=language,side=side,Elamite_form=word,
                                             compared_key=key,**{k:r[k] for k in ['headword','gloss','source','row','entry','flag','citation','notes','matched_heads']},
                                             interpretation='Same-meaning normalized spelling witness only; no borrowing, ancestry or Indus value established.'))
                for key,rr in index.items():
                    for r in rr:meaning_inventory.append(dict(case=case,side=side,language=language,key=key,
                                                               **{k:r[k] for k in ['headword','gloss','source','row','entry','flag','matched_heads']}))
            detail.append(dict(case=case,language=language,source_records=len(vocab[language]),
                               picture_forms=len(aa),target_forms=len(bb),both_meanings=bool(aa and bb),
                               exact_form_keys='; '.join(sorted(exact)),exact_bridge=bool(exact),
                               unmarked_exact_keys='; '.join(sorted(unmarked)),unmarked_exact_bridge=bool(unmarked),
                               conservative_one_edit_pairs=len(near),
                               interpretation='Selected Elamite meaning-pair portability; not a test of the whole Indus language.'))
    O.write('contact_portability_by_language.csv',detail)
    O.write('contact_portability_witnesses.csv',witnesses,['case','language','channel','key']+['picture_'+x for x in ['headword','gloss','source','row','entry','flag','citation','notes','matched_heads','variant']]+['target_'+x for x in ['headword','gloss','source','row','entry','flag','citation','notes','matched_heads','variant']]+['same_source_record','both_unmarked'])
    contact_fields=['case','language','side','Elamite_form','compared_key','headword','gloss','source','row','entry','flag','citation','notes','matched_heads','interpretation']
    O.write('contact_same_meaning_form_witnesses.csv',contacts,contact_fields)
    O.write('contact_semantic_inventory.csv',meaning_inventory)
    combined=[]
    for case,*_ in CASES:
        rr=[r for r in detail if r['case']==case]
        combined.append(dict(case=case,covered_languages='; '.join(r['language'] for r in rr if r['both_meanings']),
                             exact_languages='; '.join(r['language'] for r in rr if r['exact_bridge']),
                             unmarked_exact_languages='; '.join(r['language'] for r in rr if r['unmarked_exact_bridge']),
                             near_only_languages='; '.join(r['language'] for r in rr if not r['exact_bridge'] and r['conservative_one_edit_pairs']),
                             same_meaning_form_contacts=sum(r['case']==case for r in contacts)))
    O.write('contact_portability_cases.csv',combined)
    summary=dict(source_rows=len({(r['source'],r['row']) for r in rows}),lexical_records=len(rows),
                 record_count_note='One Brahui source record is split into two lexical records by the existing checked correction.',
                 languages=len(D.LANGS),source_counts=source_counts,
                 language_counts={l:len(v) for l,v in vocab.items()},cases=len(CASES),case_language_cells=len(detail),
                 cases_with_any_Dravidian_exact_bridge=sum(bool(r['exact_languages']) for r in combined),
                 cases_with_any_unmarked_exact_bridge=sum(bool(r['unmarked_exact_languages']) for r in combined),
                 same_meaning_normalized_form_witnesses=len(contacts),
                 witness_rows=len(witnesses),normalization='conservative whole forms; consonant doubling and distinctions preserved',
                 hypothesis_odds_calculated=False,loanwords_established=0,
                 design='Elamite-selected eight-case portability / contact-lead screen, not a balanced language contest.',
                 runtime_seconds=round(time.monotonic()-started,2),colab_units=0)
    (O.OUT/'contact_portability_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,default=O.REPO.parent/'ivc-language-sources')
    main(ap.parse_args().cache)
