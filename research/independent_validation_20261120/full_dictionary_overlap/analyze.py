"""Full recoverable DEDR inventory: synonyms, shared groups and coverage controls.

Dictionary-group overlap is not semantic identity, a reconstructed genealogy, or
validation of the proposed Indus meanings. Python 3.9+, standard library only.
"""
import argparse
import bisect
import collections
import csv
import gzip
import hashlib
import json
import random
import re
from pathlib import Path

BASE=Path(__file__).resolve().parent
REPO=BASE.parents[2]
OUT=BASE/'results'
LANGS={'Ta':'Tamil','Ma':'Malayalam','Ka':'Kannada','Te':'Telugu','Tu':'Tulu',
       'Ko':'Kota','To':'Toda','Koḍ':'Kodagu','Kol':'Kolami','Nk':'Naikri','Pa':'Parji',
       'Ga':'Gadaba','Go':'Gondi','Konḍa':'Konda','Pe':'Pengo','Manḍ':'Manda',
       'Kui':'Kui','Kuwi':'Kuwi','Kur':'Kurukh','Malt':'Malto','Br':'Brahui'}
MARKERS=sorted(set(LANGS)|{'Kuṛ','Koṇḍa','Konḏa','Mand','Ir','PāKu','PālKu','ĀlKu','AlKu','Kurub','Bel','Kor'},key=len,reverse=True)
LM='|'.join(map(re.escape,MARKERS))
LABEL=re.compile(r'(?<!\w)('+LM+r')[.:]?\s+')
HEADER=re.compile(r'(?:^|(?<=[.;]))\s*(\d{1,4}[A-Za-z]?)\s*(?:\(\s*[a-z]\s*\)\s*)?(?=(?:'+LM+r')[.:]?\s)',re.M)
ALIASES={'Kuṛ':'Kur','Koṇḍa':'Konḍa','Konḏa':'Konḍa','Mand':'Manḍ'}
INPUTS=['work_data/lexicons/dedr/dedr_text.txt','work_data/lexicons/dedr/dedr_entries.tsv',
        'research/independent_validation_20261120/language_affinity/design.json',
        'research/independent_validation_20261120/language_overlap/panel.json']


def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')


def table(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def unpaired_parens(text):
    stack=[];bad=[]
    for i,c in enumerate(text):
        if c=='(':stack.append(i)
        elif c==')':
            if stack:stack.pop()
            else:bad.append(i)
    bad+=stack;bad.sort();chars=list(text)
    for i in bad:chars[i]=' '
    return ''.join(chars),[dict(offset=i,char=text[i],context=text[max(0,i-35):i+45].strip()) for i in bad]


def top(text,pos):return text[:pos].count('(')==text[:pos].count(')')


def make_entries():
    raw=(REPO/INPUTS[0]).read_text()
    candidates=[m for m in HEADER.finditer(raw) if not re.search(
        r'(?:cf\.|s\.v\.|nos?\.|see)\s*$',raw[max(0,m.start()-18):m.start()],re.I)]
    # The printed dictionary is numerically ordered. Longest nondecreasing ID
    # sequence rejects wrapped cross-reference lines while retaining repeated
    # headers/subparts and inline entries. No lexical outcome enters selection.
    tails=[];indices=[];previous=[]
    for i,m in enumerate(candidates):
        n=int(re.match(r'\d+',m.group(1))[0]);k=bisect.bisect_right(tails,n)
        previous.append(indices[k-1] if k else -1)
        if k==len(tails):tails.append(n);indices.append(i)
        else:tails[k]=n;indices[k]=i
    i=indices[-1];chosen=[]
    while i!=-1:chosen.append(i);i=previous[i]
    chosen.reverse();marks=[candidates[i] for i in chosen]
    chunks=collections.defaultdict(list)
    for i,m in enumerate(marks):
        chunks[m.group(1)].append(raw[m.end():marks[i+1].start() if i+1<len(marks) else len(raw)])
    fallback=[]
    # Preserve an explicitly numbered TSV row when full-text header recovery
    # misses it; never let a longer glued TSV row replace full-text segments.
    for line in (REPO/INPUTS[1]).read_text().splitlines():
        eid,text=line.split('\t',1)
        if eid not in chunks:chunks[eid].append(text);fallback.append(eid)
    entries={};repair_log=[]
    for eid,parts in chunks.items():
        segments=collections.defaultdict(list);questioned=set();notes=[]
        for part_no,text in enumerate(parts):
            text,repairs=unpaired_parens(text)
            repair_log += [dict(eid=eid,part=part_no,**r) for r in repairs]
            stops=[m.start() for m in re.finditer(r'\b(?:[Cc]f\.|s\.v\.)\s*\d|\bDED(?:\b|\(S)|\bDEN\b|Previous Page|\s/\s',text) if top(text,m.start())]
            main=text[:min(stops)] if stops else text
            labels=[m for m in LABEL.finditer(main) if top(main,m.start())]
            for i,m in enumerate(labels):
                lang=ALIASES.get(m.group(1),m.group(1))
                segment=main[m.end():labels[i+1].start() if i+1<len(labels) else len(main)].strip()
                if segment and segment not in segments[lang]:segments[lang].append(segment)
                if re.search(r'\?\s*$',main[max(0,m.start()-5):m.start()]):questioned.add(lang)
            if text[len(main):].strip():notes.append(text[len(main):].strip())
        entries[eid]=dict(segments={k:' || '.join(v) for k,v in segments.items()},
                          langs=set(segments),questioned=questioned,notes=' || '.join(notes),
                          source='tsv_fallback' if eid in fallback else 'full_text',parts=len(parts))
    table('parenthesis_repairs.csv',repair_log)
    table('rejected_header_candidates.csv',[dict(eid=m.group(1),offset=m.start(),context=raw[max(0,m.start()-35):m.end()+90])
          for i,m in enumerate(candidates) if i not in set(chosen)])
    return entries,dict(header_candidates=len(candidates),accepted_chunks=len(marks),groups=len(entries),
                        tsv_fallback_ids=fallback,unpaired_parentheses=len(repair_log))


def target_set():
    old=json.loads((REPO/INPUTS[2]).read_text());panel=json.loads((REPO/INPUTS[3]).read_text())['concepts']
    sources=collections.defaultdict(set)
    for p in old['fixed_claimed_pairs']:
        for k in ('a_eid','b_eid'):sources[p[k]].add('sign '+p['sign'])
    for p in panel:sources[p['dedr']].add('concept '+p['concept'])
    return sources


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    if args.freeze:dump(BASE/'inputs.json',{p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in INPUTS})
    for p,h in json.loads((BASE/'inputs.json').read_text()).items():assert hashlib.sha256((REPO/p).read_bytes()).hexdigest()==h,p
    OUT.mkdir(exist_ok=True);entries,metadata=make_entries();targets=target_set()
    assert set(targets)<=set(entries),set(targets)-set(entries)
    presence=[]
    for eid,e in sorted(entries.items(),key=lambda x:(int(re.match(r'\d+',x[0])[0]),x[0])):
        presence.append(dict(eid=eid,source=e['source'],parts=e['parts'],languages=' '.join(lg for lg in LANGS if lg in e['langs']),
            questioned_languages=' '.join(sorted(e['questioned'])),n_languages=len(e['langs']&set(LANGS)),
            fixed_target=eid in targets,context=e['segments'].get('Ta',next(iter(e['segments'].values()),''))[:500]))
    table('all_group_presence.csv',presence)
    pairs=[]
    for a,an in LANGS.items():
        for b,bn in LANGS.items():
            aa={eid for eid,e in entries.items() if a in e['langs']};bb={eid for eid,e in entries.items() if b in e['langs']}
            pairs.append(dict(a=an,b=bn,a_groups=len(aa),b_groups=len(bb),shared=len(aa&bb),
                              fraction_of_a=len(aa&bb)/len(aa),jaccard=len(aa&bb)/len(aa|bb)))
    table('all_language_pair_overlap.csv',pairs)
    catalogue=[]
    for eid,e in entries.items():
        if 'Br' in e['langs']:
            catalogue.append(dict(eid=eid,brahui=e['segments']['Br'],questioned='Br' in e['questioned'],
                comparative_context=e['segments'].get('Ta',next(iter(e['segments'].values()))),
                other_languages=' '.join(lg for lg in LANGS if lg!='Br' and lg in e['langs']),
                fixed_target=eid in targets,target_sources=';'.join(sorted(targets.get(eid,[]))),
                notes=e['notes']))
    table('brahui_full_inventory.csv',catalogue)
    witnesses=[];target_counts=[]
    for lg,name in LANGS.items():
        for eid in sorted(targets,key=lambda x:int(re.match(r'\d+',x)[0])):
            e=entries[eid]
            witnesses.append(dict(language=name,code=lg,eid=eid,attested=lg in e['langs'],
                questioned=lg in e['questioned'],segment=e['segments'].get(lg,''),
                sources=';'.join(sorted(targets[eid]))))
        target_counts.append(dict(language=name,code=lg,groups=sum(lg in e['langs'] for e in entries.values()),
                                 target_groups=sum(lg in entries[eid]['langs'] for eid in targets),total_targets=len(targets)))
    table('fixed_target_witnesses.csv',witnesses);table('fixed_target_counts.csv',target_counts)
    # Full Brahui dictionary inventory compared with equally broad groups.
    # This diagnoses co-documentation, not a model of linguistic descent.
    br={eid for eid,e in entries.items() if 'Br' in e['langs']};nperm=1999;controls=[];nulls={};exact_controls=[]
    unq={eid for eid in br if 'Br' not in entries[eid]['questioned']}
    table('brahui_unquestioned_overlap.csv',[dict(language=name,code=lg,brahui_groups=len(br),
        shared_all=sum(lg in entries[eid]['langs'] for eid in br),unquestioned_brahui_groups=len(unq),
        shared_unquestioned=sum(lg in entries[eid]['langs'] for eid in unq)) for lg,name in LANGS.items()])
    for index,(lg,name) in enumerate(LANGS.items()):
        if lg=='Br':continue
        other=set(LANGS)-{'Br',lg}
        exact_pools=collections.defaultdict(list)
        for eid,e in entries.items():
            if eid not in br:exact_pools[len(e['langs']&other)].append(eid)
        eligible=[eid for eid in br if exact_pools[len(entries[eid]['langs']&other)]]
        expected=sum(sum(lg in entries[k]['langs'] for k in exact_pools[len(entries[eid]['langs']&other)])/
                     len(exact_pools[len(entries[eid]['langs']&other)]) for eid in eligible)
        observed=sum(lg in entries[eid]['langs'] for eid in eligible)
        unq_eligible=[eid for eid in eligible if eid in unq]
        unq_expected=sum(sum(lg in entries[k]['langs'] for k in exact_pools[len(entries[eid]['langs']&other)])/
                        len(exact_pools[len(entries[eid]['langs']&other)]) for eid in unq_eligible)
        unq_observed=sum(lg in entries[eid]['langs'] for eid in unq_eligible)
        exact_controls.append(dict(language=name,code=lg,all_brahui_groups=len(br),eligible_brahui_groups=len(eligible),
            excluded_no_controls=len(br)-len(eligible),shared_eligible=observed,
            exact_breadth_expected=expected,ratio=observed/expected if expected else None,
            unquestioned_eligible=len(unq_eligible),unquestioned_shared=unq_observed,unquestioned_expected=unq_expected,
            unquestioned_ratio=unq_observed/unq_expected if unq_expected else None))
        def cell(e):
            n=len(e['langs']&other)
            return 0 if n<=3 else 1 if n<=7 else 2
        needs=collections.Counter(cell(entries[eid]) for eid in br);pools=collections.defaultdict(list)
        for eid,e in entries.items():
            if eid not in br:pools[cell(e)].append(eid)
        assert all(len(pools[c])>=n for c,n in needs.items()),(lg,needs)
        rng=random.Random(20261120+index);values=[]
        for _ in range(nperm):
            draw=[eid for c,n in sorted(needs.items()) for eid in rng.sample(pools[c],n)]
            values.append(sum(lg in entries[eid]['langs'] for eid in draw))
        obs=sum(lg in entries[eid]['langs'] for eid in br);values.sort();mean=sum(values)/nperm
        controls.append(dict(language=name,code=lg,brahui_groups=len(br),shared=obs,matched_expected=mean,
            ratio=obs/mean if mean else None,q025=values[int(.025*(nperm-1))],q975=values[int(.975*(nperm-1))],
            p_upper=(1+sum(v>=obs for v in values))/(nperm+1)))
        nulls[lg]=values
    running=0.0
    for i,r in enumerate(sorted(controls,key=lambda r:r['p_upper'])):
        running=max(running,min(1.0,(len(controls)-i)*r['p_upper']));r['p_holm20']=running
    table('brahui_breadth_matched_controls.csv',controls)
    table('brahui_exact_breadth_standardization.csv',exact_controls)
    (OUT/'null_counts.json.gz').write_bytes(gzip.compress(json.dumps(nulls,separators=(',',':')).encode(),mtime=0))
    dump(OUT/'summary.json',dict(parser=metadata,brahui_groups=len(br),unquestioned_brahui_groups=len(unq),target_counts=target_counts,
         brahui_overlap=[p for p in pairs if p['a']=='Brahui'],controls=controls,exact_breadth=exact_controls,
         note='Dictionary-group attestations, including synonyms, shifted senses and questioned comparisons. Not all attestations preserve a target meaning or prove inheritance.'))
    print('Parsed',len(entries),'groups;',len(br),'with Brahui; wrote complete 21-language comparisons.')
    for r in controls:
        if r['code'] in ('Ta','Ma','Ka','Te','Kur','Malt'):print(r)


if __name__=='__main__':main()
