#!/usr/bin/env python3
"""Freeze upstream proposals without importing its executable analysis modules."""
import ast, csv, hashlib, json, subprocess
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
def rows(p):
    with p.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))
def literal(name, file):
    tree=ast.parse((REPO/file).read_text())
    return ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)))
def main():
    lex=rows(REPO/'work_data/key6a/master_lexicon_after_key6a.csv')
    meta=literal('SIGN_META','work_scripts/key6b_readings_key5_atlas.py')
    roles={r['sign']:r['v3_class'] for r in rows(REPO/'work_data/fv3/classes_v3.csv')}
    shapes={r['lipi_wells_number']:r['shape_description'] for r in rows(REPO/'work_data/sign_shapes.csv')}
    freq={r['sign']:int(r['intact_4163_tokens']) for r in lex}
    selected=[r['sign'] for r in sorted(lex,key=lambda r:(-freq[r['sign']],r['sign']))[:35]]
    for s in '060 550 845 142 595 482 335 171 480 350 540 923 850'.split():
        if s not in selected: selected.append(s)
        if len(selected)==45: break
    out=[]
    for r in lex:
        s=r['sign']; m=meta.get(s)
        out.append(dict(r, short_gloss=m[1] if m else r['evidence_note'], semantic_class=m[2] if m else 'UNCLASSIFIED_NEW', semantic_domain=m[4] if m else 'Unclassified new', structure_class=roles.get(s,'UNKNOWN'), shape=shapes.get(s,''), selected_for_sign_review=s in selected))
    config={'base_commit':'727dfd411a4faa44d193d204757540d45c7b139b','date':'2026-11-20','seed':20261120,'selected_signs':selected,'semantics_source':'Key6B SIGN_META literal only; newer signs retain exact Key6A proposal and remain unclassified for compressed prediction','hypothesis_status':'Retrospective frozen application; not a blind holdout or preregistration','targets':['seal','mtab','ctab','tag','pot','rod'],'n_permutations':5000,'rival_vocabulary_count':199,'folds':5,'C':1.0,'input_sha256':{p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in ['work_data/key6a/master_lexicon_after_key6a.csv','work_data/reader_v3/corpus_soundfree_readings.csv','work_data/sem/objects_lipi.csv','work_data/sem/objects_mah_new.csv','work_scripts/key6b_readings_key5_atlas.py']}}
    (BASE/'frozen/proposals.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    (BASE/'frozen/design.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
    print('Frozen',len(out),'signs;',len(selected),'review signs')
if __name__=='__main__': main()
