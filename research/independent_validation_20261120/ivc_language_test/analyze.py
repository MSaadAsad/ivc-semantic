"""IVC-specific lexical portability, with language-specific meanings and witnesses.

Run with --cache PATH to the pinned Jambu source tree. Raw sources stay outside git.
This is a retrospective dictionary analysis, not a test of independently read signs.
"""
import argparse, ast, collections, csv, hashlib, itertools, json, re, unicodedata
from pathlib import Path

BASE=Path(__file__).resolve().parent
LANGS=['Tamil','Malayalam','Kannada','Telugu','Tulu','Kota','Toda','Kodagu',
       'Kolami','Naikri','Naiki','Parji','Gadaba','Gondi','Konda','Pengo','Manda',
       'Kui','Kuwi','Kurukh','Malto','Brahui']
NORTH=['Kurukh','Malto','Brahui']
TRANS=str.maketrans({'ʈ':'ṭ','ɖ':'ḍ','ɳ':'ṇ','ɲ':'ñ','ŋ':'ṅ','ː':'̄'})

def nfc(x):return unicodedata.normalize('NFC',x)
def form(x):
    x=nfc(x.lower().strip().translate(TRANS))
    x=re.split(r'\s*\(',x)[0]
    return x.strip(' -?*.,')
def variants(x):
    # Explicit headword alternatives only; no automatic conjugation or stem inference.
    return {form(y) for y in re.split(r'[,/]',re.split(r'\s*\(',x)[0]) if form(y)}
def meaning(gloss,terms):
    # Ignore source references and "see" cross-references, which are not definitions.
    gloss=re.split(r'\b(?:DED|DEDS|DEDR)\b',gloss)[0].lower()
    if re.match(r'^(?:see|cf\.)\s',gloss):return False
    return any(t and re.search(r'(?<![a-z])'+re.escape(t)+r'(?:s|ing|ed)?(?![a-z])',gloss) for t in terms)

def role(r,c,side):
    if not meaning(r['gloss'],c[side]):return False
    # A young shoot is not by itself a second sense 'young person / child'.
    if c['id']=='S760' and side=='b':
        return meaning(r['gloss'],['child','infant','anything young','youth'])
    # A verb 'wear a garland' is not a noun 'garland'. The source explicitly
    # questions the Tamil verb's existence; do not manufacture exact homophony.
    if c['id']=='S503' and side=='b' and r['gloss'].startswith('to wear'):return False
    # DEDR 49 Telugu actually gives accu-kaṭṭu sēyu, a compound predicate.
    if c['id']=='S615' and side=='b' and r['language']=='Telugu' and r['entry']=='49':return False
    return True
def edit1(a,b):
    if a==b:return True
    if min(len(a),len(b))<3 or abs(len(a)-len(b))>1:return False
    if len(a)==len(b):return sum(x!=y for x,y in zip(a,b))==1
    if len(a)>len(b):a,b=b,a
    return any(a==b[:i]+b[i+1:] for i in range(len(b)))
def writecsv(path,rows,fields=None):
    rows=list(rows)
    if not rows:return
    with path.open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def extract_malto(pdf):
    import fitz
    doc=fitz.open(pdf);out=[];current=None
    for pno in range(433,466):
        page=doc[pno]
        spans=[s for b in page.get_text('dict')['blocks'] for ln in b.get('lines',[]) for s in ln['spans'] if 57<s['bbox'][1]<550]
        for left,right in [(64,205),(221,360)]:
            ss=sorted([s for s in spans if left<=s['bbox'][0]<right],key=lambda s:(s['bbox'][1],s['bbox'][0]))
            lines=[]
            for s in ss:
                if lines and abs(s['bbox'][1]-lines[-1][0])<1.8:lines[-1][1].append(s)
                else:lines.append([s['bbox'][1],[s]])
            for _,ls in lines:
                ls.sort(key=lambda s:s['bbox'][0]);text=' '.join(s['text'] for s in ls)
                if text=='Glossary':continue
                new=abs(ls[0]['bbox'][0]-(64.8 if left==64 else 221.8))<2
                if new:
                    if current:out.append(current)
                    current={'text':text,'page':pno-5,'physical_page':pno+1}
                elif current:current['text']+=' '+text
    if current:out.append(current)
    rows=[]
    for i,x in enumerate(out):
        if '‘' not in x['text']:continue
        head,definition=x['text'].split('‘',1)
        head=re.sub(r'\[.*?\]','',head).strip()
        gloss=definition.split('’',1)[0]
        rows.append(dict(language='Malto',entry='',headword=head,gloss=gloss,
            citation=f'Kobayashi2017:p{x["page"]} (PDF {x["physical_page"]})',
            source='TGM2017.pdf',row=i+1,notes='Glossary text extraction; etymological origin unclassified.',flag='unclassified',linked=False))
    return rows,len(out)

def load(cache,malto):
    tree=ast.parse((cache/'data/dedr/abbrevs.py').read_text())
    dia=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='dialects' for t in x.targets))
    aliases={v[1]:k[1] for k,v in dia.items() if v[1]}
    aliases.update({'Tam':'Tamil','Mal':'Malayalam','OMal':'Malayalam','OTelugu':'Telugu','Kurux':'Kurukh','Brah':'Brahui'})
    # Resolve source dialect IDs before applying display names.
    def lang(x):
        for _ in range(3):
            y=aliases.get(x,x)
            if y==x:break
            x=y
        return x
    paths=[cache/'data/dedr/dedr_new.csv']+sorted((cache/'data/other/forms').glob('*.csv'))
    paths=[p for p in paths if p.name!='20230416-northern.csv']
    out=[];counts={}
    for p in paths:
        counts[p.name]=0
        for i,r in enumerate(csv.reader(p.open())):
            if len(r)!=15:raise ValueError((p,i,len(r)))
            l=lang(r[0])
            if l not in LANGS:continue
            counts[p.name]+=1
            eid=r[1][1:] if re.fullmatch(r'd\d+',r[1]) else ''
            notes=' | '.join(v for v in [r[6],r[8],r[9],r[14]] if v)
            flag='loan' if 'loanword' in r[14] else 'questioned' if '?' in r[8] else 'unmarked'
            # DEDR can place an explicit donor classification in its gloss,
            # rather than in the structured metadata. A mention of a related
            # borrowed word is not enough; this phrase labels the headword itself.
            if 'one of the tatsamas' in r[3].lower():
                flag='loan';notes+=' | DEDR explicitly labels this headword a tatsama (Sanskrit loan).'
            out.append(dict(language=l,entry=eid,headword=nfc(r[2]),gloss=nfc(r[3]),citation=r[7],source=p.name,row=i+1,notes=notes,flag=flag,linked=bool(eid)))
    # Two independently checked errors in the structured transcription. The
    # original DEDR text has separate Br. urā and ust, and bil id. (= bow).
    for r in out:
        if r['source']=='dedr_new.csv' and r['entry']=='5422' and r['gloss']=='in all':
            r['gloss']='bow';r['notes']+=' | Restored original DEDR id. = bow; structured gloss in all was spurious.'
        if r['source']=='dedr_new.csv' and r['language']=='Brahui':
            if r['entry']=='5422' and r['headword']=='bil':
                r['gloss']='bow';r['notes']+=' | Restored original DEDR id. = bow; structured gloss in all was spurious.'
            if r['entry']=='698' and r['headword']=='urā':
                r['gloss']='house, wife';r['flag']='questioned'
                r['notes']+=' | Split merged ust headword; DEDR alternatively assigns urā to 752.'
                out.append(dict(r,headword='ust',gloss='heart, mind, centre, inside, kernel',notes='Split from merged Br. urā; DEDR alternatively assigns ust to 645.',flag='questioned'))
    if malto:
        extra,total=extract_malto(malto);out+=extra;counts['TGM2017.pdf']=len(extra);counts['TGM2017_unquoted_entries']=total-len(extra)
    # Supplement records can inherit only an exact, same-language lexical identification,
    # never an etymon assigned from an English meaning. Keep the linkage explicit.
    anchors=collections.defaultdict(set)
    for r in out:
        if r['entry']:
            for v in variants(r['headword']):anchors[r['language'],v].add(r['entry'])
    additions=[]
    for r in out:
        if r['entry']:continue
        ids=set().union(*(anchors[r['language'],v] for v in variants(r['headword'])))
        for eid in ids:
            additions.append(dict(r,entry=eid,linked=True,notes=r['notes']+' | Exact headword linkage to DEDR; homonym ambiguity remains.',flag=r['flag']))
    return out,counts,additions

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,required=True);ap.add_argument('--malto',type=Path);args=ap.parse_args()
    claims=json.loads((BASE/'claims.json').read_text())['claims']
    rows,counts,links=load(args.cache,args.malto)
    results=BASE/'results';results.mkdir(exist_ok=True)
    index=collections.defaultdict(list);vocab=collections.defaultdict(list)
    for r in rows:
        vocab[r['language']].append(r)
        if r['entry']:index[r['language'],r['entry']].append(r)
    writecsv(results/'candidate_headword_links.csv',({k:v for k,v in r.items() if k!='linked'} for r in links))
    writecsv(results/'explicit_loan_records.csv',({k:v for k,v in r.items() if k!='linked'} for r in rows if r['flag']=='loan'))
    matrix=[];witness=[];family_witness=[];details=[];alternatives=[];vocab_pairs=[]
    for c in claims:
        for l in LANGS:
            aa=[r for eid in c['a_entries'] for r in index[l,eid] if r['flag']!='loan']
            bb=[r for eid in c['b_entries'] for r in index[l,eid] if r['flag']!='loan']
            for side,rr in [('A',aa),('B',bb)]:
                for r in rr:family_witness.append(dict(claim=c['id'],side=side,**{k:v for k,v in r.items() if k!='linked'}))
            ar=[r for r in aa if role(r,c,'a')]
            br=[r for r in bb if role(r,c,'b')]
            exact=[];near=[]
            for a,b in itertools.product(ar,br):
                for av,bv in itertools.product(variants(a['headword']),variants(b['headword'])):
                    if av==bv:exact.append((a,b,av,bv))
                    elif edit1(av,bv):near.append((a,b,av,bv))
            two=bool(ar and br) if c['kind'] in ('bridge','polysemy') else False
            target=br if c['b_entries'] else ar
            z=dict(claim=c['id'],sign=c['sign'],title=c['title'],kind=c['kind'],language=l,
                family_a=bool(aa),family_b=bool(bb),meaning_a=bool(ar),meaning_b=bool(br),
                target_meaning=bool(target),both_meanings=two,
                target_without_questioned=any(r['flag']!='questioned' for r in target),
                strict_complete=bool(exact),one_edit_complete=bool(exact or near),
                unmarked_strict=any(a['flag']!='questioned' and b['flag']!='questioned' for a,b,_,_ in exact))
            matrix.append(z)
            for side,rr in [('A',ar),('B',br)]:
                for r in rr:witness.append(dict(claim=c['id'],side=side,**{k:v for k,v in r.items() if k!='linked'}))
            for level,pairs in [('exact',exact),('one_edit_only',near)]:
                seen=set()
                for a,b,av,bv in pairs:
                    key=av,bv,a['entry'],b['entry'],a['gloss'],b['gloss']
                    if key in seen:continue
                    seen.add(key)
                    details.append(dict(claim=c['id'],language=l,level=level,a_form=av,b_form=bv,
                        a_entry=a['entry'],b_entry=b['entry'],a_gloss=a['gloss'],b_gloss=b['gloss'],a_source=a['citation'],b_source=b['citation'],flags=a['flag']+' / '+b['flag']))
            if l in NORTH:
                if c['kind'] in ('bridge','polysemy'):
                    va=collections.defaultdict(list);vb=collections.defaultdict(list)
                    for r in vocab[l]:
                        for side,vi in [('a',va),('b',vb)]:
                            if role(r,c,side):
                                for v in variants(r['headword']):vi[v].append(r)
                    for v in va.keys() & vb.keys():
                        a,b=va[v][0],vb[v][0]
                        vocab_pairs.append(dict(claim=c['id'],language=l,form=v,a_gloss=a['gloss'],b_gloss=b['gloss'],a_source=a['citation'],b_source=b['citation'],a_entry=a['entry'],b_entry=b['entry'],flags=a['flag']+' / '+b['flag']))
                # Whole-vocabulary synonyms: report alternatives; do not credit original roots.
                for side,terms in [('A',c['a']),('B',c['b'])]:
                    if not any(terms):continue
                    for r in vocab[l]:
                        if r['entry'] or not role(r,c,side.lower()):continue
                        alternatives.append(dict(claim=c['id'],side=side,**{k:v for k,v in r.items() if k!='linked'}))
    writecsv(results/'language_by_claim.csv',matrix)
    writecsv(results/'meaning_witnesses.csv',witness)
    writecsv(results/'family_witnesses.csv',family_witness)
    writecsv(results/'complete_pair_witnesses.csv',details)
    # Keep relevant attested replacements, deduplicating matched categories and source links.
    writecsv(results/'northern_synonyms.csv',alternatives)
    writecsv(results/'exploratory_northern_same_form.csv',vocab_pairs)
    inventory=[]
    for l in LANGS:
        rr=vocab[l];unique={(r['source'],r['row']) for r in rr}
        inventory.append(dict(language=l,source_records=len(unique),distinct_headword_strings=len({form(r['headword']) for r in rr}),
            dedr_families=len({r['entry'] for r in rr if r['entry']}),
            target_meanings=sum(x['target_meaning'] for x in matrix if x['language']==l),
            two_sided_meanings=sum(x['both_meanings'] for x in matrix if x['language']==l and x['kind'] in ('bridge','polysemy')),
            strict_complete=sum(x['strict_complete'] for x in matrix if x['language']==l),
            one_edit_complete=sum(x['one_edit_complete'] for x in matrix if x['language']==l)))
    writecsv(results/'language_summary.csv',inventory)
    categories=[]
    for c in claims:
        mm=[x for x in matrix if x['claim']==c['id']]
        for field in ['target_meaning','both_meanings','strict_complete']:
            yes=[x['language'] for x in mm if x[field]]
            categories.append(dict(claim=c['id'],title=c['title'],measure=field,count=len(yes),languages='; '.join(yes),unattested='; '.join(l for l in LANGS if l not in yes)))
    writecsv(results/'overlap_sets.csv',categories)
    repo=BASE.parents[2]
    master=list(csv.DictReader((repo/'work_data/key6a/master_lexicon_after_key6a.csv').open()))
    selected={c['sign']:c for c in claims}
    scope=[]
    for r in master:
        c=selected.get(r['sign'])
        scope.append(dict(sign=r['sign'],proposal_root=r['root_or_gloss'],source_lever=r['source_lever'],
            intact_tokens=r['intact_4163_tokens'],claim=c['id'] if c else '',
            status='scored representative' if c else 'excluded zero-token extension; eṇ not verified by eṭṭu' if r['sign']=='008' else 'not evaluated as a separate lexical claim in this representative panel',
            same_root_representatives='; '.join(x['id'] for x in claims if x['proposal_root']==r['root_or_gloss'])))
    writecsv(results/'key_scope.csv',scope)
    summary=dict(claims=len(claims),connections=sum(c['kind'] in ('bridge','polysemy') for c in claims),languages=len(LANGS),
        source_counts=counts,candidate_headword_links_unscored=len(links),unique_source_records=sum(x['source_records'] for x in inventory),
        caveats=['Not independently assigned Indus meanings.','Unattested does not mean absent from a language.',
            'Strict exact form is a conservative spelling criterion, not a reconstruction of Harappan phonology.',
            'One-edit is exploratory and does not establish a sound law.','Unmarked origin does not establish inheritance.',
            'Supplement exact-headword links are candidates only and are excluded from the primary score.',
            'Naiki and Naikri are kept separate as in the source; dialects are collapsed into their source language.'],
        inventory=inventory)
    (results/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
