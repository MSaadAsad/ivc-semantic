"""Compare fixed meanings and etyma; never equate spelling identity with cognacy."""
import argparse
import collections
import csv
import gzip
import hashlib
import json
import math
import random
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
EXT = BASE / 'external/dravlex'
OUT = BASE / 'results'
LANGS = {'Ta':'Tamil','Ma':'Malayalam','Ka':'Kannada','Te':'Telugu','Tu':'Tulu',
         'Ko':'Kota','To':'Toda','Koḍ':'Kodagu','Kol':'Kolami','Nk':'Naikri','Pa':'Parji',
         'Ga':'Gadaba','Go':'Gondi','Konḍa':'Konda','Pe':'Pengo','Manḍ':'Manda',
         'Kui':'Kui','Kuwi':'Kuwi','Kur':'Kurukh','Malt':'Malto','Br':'Brahui'}
MARKERS = sorted(set(LANGS)|{'Kuṛ','Koṇḍa','Ir','PāKu','PālKu','ĀlKu','AlKu','Kurub','Bel','Kor'}, key=len,reverse=True)
LM = '|'.join(map(re.escape,MARKERS))
LABEL = re.compile(r'(?<!\w)('+LM+r')\.?\s+')
GLUED = re.compile(r'(?<=[.;])\s+(\d{1,4}[a-z]?)(?:\s*\([a-z]\))?\s+(?=(?:'+LM+r')\.?\s)')
MAJOR = ('Ta','Ma','Ka','Te')
SEED = 20261121


def read(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def dump(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


def table(name,rows):
    if not rows:
        return
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def top(text,pos):
    return text[:pos].count('(')==text[:pos].count(')')


def dictionary_entries():
    entries={}
    for line in (REPO/'work_data/lexicons/dedr/dedr_entries.tsv').read_text().splitlines():
        eid,text=line.split('\t',1)
        cuts=[m for m in GLUED.finditer(text) if top(text,m.start()) and not
              re.search(r'(?:s\.v\.|cf\.|nos?\.|see)\s*$',text[max(0,m.start()-18):m.start()],re.I)]
        chunks=[(eid,text[:cuts[0].start()] if cuts else text)]
        chunks += [(m.group(1),text[m.end():cuts[i+1].start() if i+1<len(cuts) else len(text)]) for i,m in enumerate(cuts)]
        for eid,txt in chunks:
            if len(txt)>len(entries.get(eid,'')):entries[eid]=txt
    result={}
    for eid,text in entries.items():
        # Stop before top-level cross-references, not before cognate language text.
        stops=[m.start() for m in re.finditer(r'\b(?:[Cc]f\.|s\.v\.)\s*\d|DED\(S|\bDEN\b|Previous Page|\s/\s',text) if top(text,m.start())]
        main=text[:min(stops)] if stops else text
        labels=[m for m in LABEL.finditer(main) if top(main,m.start())]
        segments={}
        for i,m in enumerate(labels):
            lang={'Kuṛ':'Kur','Koṇḍa':'Konḍa'}.get(m.group(1),m.group(1))
            segment=main[m.end():labels[i+1].start() if i+1<len(labels) else len(main)].strip()
            segments.setdefault(lang,segment)
        result[eid]=dict(text=main,langs=set(segments),segments=segments)
    return result


def exact_paired(a,b):
    n=a+b
    if n==0:return 1.0
    return min(1.0,2*sum(math.comb(n,k) for k in range(min(a,b)+1))/2**n)


def dravlex(panel):
    forms=read(EXT/'cldf/forms.csv'); judgments=read(EXT/'cldf/cognates.csv')
    names={r['ID']:r['Name'] for r in read(EXT/'cldf/parameters.csv')}
    langs=[r['ID'] for r in read(EXT/'cldf/languages.csv')]
    f_by={r['ID']:r for r in forms}
    by_cell=collections.defaultdict(list);by_form=collections.defaultdict(list)
    for f in forms:by_cell[(f['Language_ID'],f['Parameter_ID'])].append(f)
    for c in judgments:by_form[c['Form_ID']].append(c)
    anchors=[];scores=[];witnesses=[]
    for p in panel:
        hits=[c for c in judgments if f_by[c['Form_ID']]['Parameter_ID']==p['concept'] and
              re.search(r'(?<!\d)'+re.escape(p['dedr'])+r'[a-z]?(?!\d)',c['Comment'])]
        classes={c['Cognateset_ID'] for c in hits}
        if p.get('manual_class'):classes.add(p['manual_class'])
        anchors.append(dict(concept=p['concept'],meaning=names[p['concept']],dedr=p['dedr'],root=p['root'],
                            cognate_classes=';'.join(sorted(classes)),annotation_witnesses=len(hits),
                            manual_anchor=bool(p.get('manual_class')),scorable=bool(classes)))
        for c in hits:
            witnesses.append(dict(concept=p['concept'],dedr=p['dedr'],class_id=c['Cognateset_ID'],form_id=c['Form_ID'],
                                  language=f_by[c['Form_ID']]['Language_ID'],form=f_by[c['Form_ID']]['Form'],comment=c['Comment']))
        for lang in langs:
            ff=by_cell[(lang,p['concept'])]
            for exclude_loans in (False,True):
                matched=[]
                for f in ff:
                    if exclude_loans and f['Loan'].lower()=='true':continue
                    cc=[c for c in by_form[f['ID']] if c['Doubt'].lower()!='true' and c['Cognateset_ID'] in classes]
                    if cc:matched.append(f)
                scores.append(dict(language=lang,concept=p['concept'],meaning=names[p['concept']],dedr=p['dedr'],root=p['root'],
                    exclude_flagged_loans=exclude_loans,scorable=bool(classes),manual_anchor=bool(p.get('manual_class')),
                    recorded=bool(ff),matched=bool(classes and matched),matched_forms=';'.join(f['Form'] for f in matched),
                    all_recorded_forms=';'.join(f['Form'] for f in ff),
                    flagged_loan_forms=';'.join(f['Form'] for f in ff if f['Loan'].lower()=='true'),
                    recorded_classes=';'.join(sorted({c['Cognateset_ID'] for f in ff for c in by_form[f['ID']]}))))
    summaries=[]
    for exclude_loans in (False,True):
        for omit_manual in (False,True):
            for lang in langs:
                ss=[s for s in scores if s['language']==lang and s['exclude_flagged_loans']==exclude_loans
                    and s['scorable'] and (not omit_manual or not s['manual_anchor'])]
                summaries.append(dict(language=lang,exclude_flagged_loans=exclude_loans,omit_manual_anchor=omit_manual,
                    concepts=len(ss),recorded=sum(s['recorded'] for s in ss),matches=sum(s['matched'] for s in ss)))
    # Paired exact tests across *all* language pairs, then Holm; descriptive, selected panel.
    ss=[s for s in scores if s['exclude_flagged_loans'] and s['scorable']]
    matrices={lg:{s['concept']:s for s in ss if s['language']==lg} for lg in langs}
    contrasts=[]
    for i,a in enumerate(langs):
        for b in langs[i+1:]:
            common=[c for c in matrices[a] if matrices[a][c]['recorded'] and matrices[b][c]['recorded']]
            aw=sum(matrices[a][c]['matched'] and not matrices[b][c]['matched'] for c in common)
            bw=sum(matrices[b][c]['matched'] and not matrices[a][c]['matched'] for c in common)
            contrasts.append(dict(a=a,b=b,common=len(common),a_only=aw,b_only=bw,p_two_sided=exact_paired(aw,bw)))
    running=0.0
    for k,r in enumerate(sorted(contrasts,key=lambda r:r['p_two_sided'])):
        running=max(running,min(1.0,(len(contrasts)-k)*r['p_two_sided']));r['p_holm']=running
    table('dravlex_anchors.csv',anchors);table('dravlex_annotation_witnesses.csv',witnesses)
    table('dravlex_concept_scores.csv',scores);table('dravlex_summary.csv',summaries);table('dravlex_paired_contrasts.csv',contrasts)
    return dict(lexemes=len(forms),languages=len(langs),concepts=len(names),panel_concepts=len(panel),
                scorable_concepts=sum(a['scorable'] for a in anchors),anchors=anchors,summary=summaries,
                holm_significant_pairs=sum(c['p_holm']<.05 for c in contrasts))


def fixed_etyma_overlap(entries,panel):
    old=json.loads((BASE.parent/'language_affinity/design.json').read_text())
    sources=collections.defaultdict(list)
    for p in old['fixed_claimed_pairs']:
        for side in ['a_eid','b_eid']:sources[p[side]].append('bridge_sign_'+p['sign'])
    for p in panel:sources[p['dedr']].append('basic_'+p['concept'])
    target=set(sources)
    assert target<=set(entries),sorted(target-set(entries))
    cells=collections.defaultdict(list)
    # Exactly match attestation patterns of four literary languages; key selected there.
    def cell(e):return ''.join('1' if lg in e['langs'] else '0' for lg in MAJOR)
    for eid,e in entries.items():
        if eid not in target:cells[cell(e)].append(eid)
    needs=collections.Counter(cell(entries[eid]) for eid in target)
    assert all(len(cells[c])>=n for c,n in needs.items())
    rng=random.Random(SEED); nperm=4999
    null={lg:[] for lg in LANGS}
    for _ in range(nperm):
        draw=[eid for c,n in sorted(needs.items()) for eid in rng.sample(cells[c],n)]
        for lg in LANGS:null[lg].append(sum(lg in entries[eid]['langs'] for eid in draw))
    result=[];witness=[]
    for lg,name in LANGS.items():
        observed=sum(lg in entries[eid]['langs'] for eid in target)
        values=sorted(null[lg]);mean=sum(values)/nperm
        result.append(dict(control='major_pattern',code=lg,language=name,target_etyma=len(target),attested_target_etyma=observed,
            background_etyma=sum(lg in e['langs'] for eid,e in entries.items() if eid not in target),
            background_total=len(entries)-len(target),matched_expected=mean,
            matched_q025=values[int(.025*(nperm-1))],matched_q975=values[int(.975*(nperm-1))],
            excess_over_matched=observed-mean,ratio_to_matched=observed/mean if mean else None,
            conditional_p_upper=(1+sum(v>=observed for v in values))/(nperm+1)))
        for eid in sorted(target,key=lambda x:(int(re.match(r'\d+',x)[0]),x)):
            witness.append(dict(eid=eid,code=lg,language=name,attested=lg in entries[eid]['langs'],
                sources=';'.join(sorted(set(sources[eid]))),raw_language_segment=entries[eid]['segments'].get(lg,'')))
    strata_rows=[dict(control='major_pattern',code='all',stratum=c,target_n=n,available_controls=len(cells[c])) for c,n in sorted(needs.items())]
    all_null={'major_pattern:'+lg:v for lg,v in null.items()}
    # Stronger sensitivity: account for general breadth outside the focal language.
    # Exclude all three northern languages from the breadth count, so the northern
    # comparisons share the same controls and are not conditioned on one another.
    for index,(lg,name) in enumerate(LANGS.items()):
        breadth_langs=set(LANGS)-set(MAJOR)-{'Br','Kur','Malt',lg}
        def broad_cell(e):
            n=len(e['langs'] & breadth_langs)
            return cell(e)+':'+str(0 if n==0 else 1 if n<=3 else 2)
        pools=collections.defaultdict(list)
        for eid,e in entries.items():
            if eid not in target:pools[broad_cell(e)].append(eid)
        counts=collections.Counter(broad_cell(entries[eid]) for eid in target)
        assert all(len(pools[c])>=n for c,n in counts.items()),(lg,counts)
        local=random.Random(SEED+index+1);values=[]
        for _ in range(nperm):
            draw=[eid for c,n in sorted(counts.items()) for eid in local.sample(pools[c],n)]
            values.append(sum(lg in entries[eid]['langs'] for eid in draw))
        observed=sum(lg in entries[eid]['langs'] for eid in target)
        values.sort();mean=sum(values)/nperm
        result.append(dict(control='major_pattern_plus_breadth',code=lg,language=name,target_etyma=len(target),
            attested_target_etyma=observed,background_etyma=sum(lg in e['langs'] for eid,e in entries.items() if eid not in target),
            background_total=len(entries)-len(target),matched_expected=mean,
            matched_q025=values[int(.025*(nperm-1))],matched_q975=values[int(.975*(nperm-1))],
            excess_over_matched=observed-mean,ratio_to_matched=observed/mean if mean else None,
            conditional_p_upper=(1+sum(v>=observed for v in values))/(nperm+1)))
        all_null['major_pattern_plus_breadth:'+lg]=values
        strata_rows += [dict(control='major_pattern_plus_breadth',code=lg,stratum=c,target_n=n,available_controls=len(pools[c])) for c,n in sorted(counts.items())]
    running=0.0
    for k,r in enumerate(sorted(result,key=lambda r:r['conditional_p_upper'])):
        running=max(running,min(1.0,(len(result)-k)*r['conditional_p_upper']));r['p_holm_all42']=running
    table('fixed_etyma_summary.csv',result);table('fixed_etyma_witnesses.csv',witness)
    table('matching_strata.csv',strata_rows)
    (OUT/'matched_null_counts.json.gz').write_bytes(gzip.compress(
        json.dumps(all_null,separators=(',',':')).encode(),mtime=0))
    # A failed rebus pair can be unobserved even if one side is represented.
    pair_rows=[]
    for lg,name in LANGS.items():
        aa=sum(lg in entries[p['a_eid']]['langs'] for p in old['fixed_claimed_pairs'])
        bb=sum(lg in entries[p['b_eid']]['langs'] for p in old['fixed_claimed_pairs'])
        both=sum(lg in entries[p['a_eid']]['langs'] and lg in entries[p['b_eid']]['langs'] for p in old['fixed_claimed_pairs'])
        pair_rows.append(dict(language=name,pairs=len(old['fixed_claimed_pairs']),a_present=aa,b_present=bb,both_present=both))
    table('fixed_pair_coverage.csv',pair_rows)
    return dict(numbered_entries=len(entries),target_etyma=len(target),matched_draws=nperm,seed=SEED,
                matching='Major-language presence pattern; sensitivity additionally matches breadth in 0, 1-3, 4+ other languages, excluding focal and all northern languages. Target entries excluded from controls. These are dictionary-selection diagnostics, not ancient-language tests.',
                results=result,pair_coverage=pair_rows)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    inputs=[BASE/'panel.json',BASE.parent/'language_affinity/design.json',
            REPO/'work_data/lexicons/dedr/dedr_entries.tsv',REPO/'work_data/key6a/master_lexicon_after_key6a.csv']
    provenance=json.loads((EXT/'provenance.json').read_text())
    inputs += [EXT/r['path'] for r in provenance['files']]+[EXT/'provenance.json']
    if args.freeze:dump(BASE/'inputs.json',{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    for p,h in json.loads((BASE/'inputs.json').read_text()).items():
        assert hashlib.sha256((REPO/p).read_bytes()).hexdigest()==h,p
    OUT.mkdir(exist_ok=True)
    panel=json.loads((BASE/'panel.json').read_text())['concepts']
    summary=dict(dravlex=dravlex(panel),dedr=fixed_etyma_overlap(dictionary_entries(),panel))
    dump(OUT/'summary.json',summary)
    print('DravLex:')
    for r in summary['dravlex']['summary']:
        if r['exclude_flagged_loans'] and not r['omit_manual_anchor']:print(r)
    print('DEDR northern overlap:')
    for r in summary['dedr']['results']:
        if r['code'] in ('Br','Kur','Malt','Ta','Ma','Ka','Te'):print(r)


if __name__=='__main__':main()
