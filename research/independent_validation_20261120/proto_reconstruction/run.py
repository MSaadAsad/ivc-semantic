"""Full-table historical lexical screen; no newly assigned Indus translations.

The independent unit is a proposed meaning pair, not every occurrence on a seal.
Reconstruction equality is assessed within source and ancestral level. Dating and
the accuracy of individual imported source transcriptions are not assumed.
"""
import argparse, ast, collections, csv, difflib, gzip, hashlib, itertools, json, re, unicodedata
from pathlib import Path

BASE=Path(__file__).resolve().parent; REPO=BASE.parents[2]
PUBLISHED={'Krishnamurti, 2003','Starostin, 2006-2013'}
PD='Proto-Dravidian'
def rows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rs,fields=None):
    rs=list(rs)
    if not rs and not fields:return
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def form(s):
    # Only editorial word/stem-boundary marks and explicit trailing homonym
    # indices are removed. Vowel length, H, accents, consonants and underscore
    # notation remain distinct. The dataset's lossy 'simplified' is never scored.
    s=unicodedata.normalize('NFC',s.strip())
    s=re.sub(r'\s+\d+$','',s).replace('*','').replace('-','')
    return re.sub(r'\s+','',s).strip()
def forms(s):
    return sorted({form(v) for v in re.split(r'[,;/]',s) if form(v)})
def concrete(f):
    return not re.search(r'V|[?()<>]|\.\.',f)
def sense_qualification(c,a,b,f):
    if not concrete(f):return 'Abstract or uncertain form; not a fully specified pronunciation'
    if c['sign']=='760' and not re.search(r'\b(?:son|daughter|child|infant|youth|young person|young one)\b',b['meaning'],re.I):
        return 'Young sprout does not establish the proposed human-child sense'
    if c['sign']=='892' and re.search(r'\bto bow\b',a['meaning'],re.I):return 'Verb bow is not the pictured weapon'
    if c['sign']=='220' and re.search(r'fish[- ]hook',a['meaning'],re.I):return 'Fish-hook is not the pictured fish'
    return 'No specified semantic or abstract-form exclusion; still requires source review'
def terms_rx(terms):
    terms=[t for t in terms if t.strip()]
    if not terms:raise ValueError('Empty concept list must not become an all-matching expression')
    return re.compile(r'(?<![a-z])(?:'+'|'.join(re.escape(t) for t in terms)+r')(?:s|ing|ed)?(?![a-z])',re.I)
def compact(rs):
    return ' | '.join(f"{r['reconstruction']} [{r['meaning']}; DEDR {r['number'] or 'unlinked'}; #{r['id_pdr']}]" for r in rs)
def edit_distance(a,b):
    previous=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        current=[i]
        for j,y in enumerate(b,1):current.append(min(current[-1]+1,previous[j]+1,previous[j-1]+(x!=y)))
        previous=current
    return previous[-1]
def main(source):
    out=BASE/'results';out.mkdir(parents=True,exist_ok=True)
    raw=rows(source); assert len(raw)==15629
    assert len({r['id_pdr'] for r in raw})==len(raw)
    corrections=json.loads((BASE/'source_corrections.json').read_text())['corrections']
    for r in raw:
        r['original_number']=r['number'];r['source_link_correction']=''
        for fix in corrections:
            if r['id_pdr']==fix['id_pdr']:
                assert r[fix['field']]==fix['original'];r[fix['field']]=fix['corrected']
                r['source_link_correction']=fix['reason']+' '+fix['source_url']
    by_number=collections.defaultdict(list)
    for r in raw:
        r['_forms']=forms(r['reconstruction'])
        by_number[r['number']].append(r)
    reps=json.loads((BASE.parent/'ivc_language_test/claims.json').read_text())['claims']
    rep_by_sign={r['sign']:r for r in reps}
    panels=json.loads((BASE.parent/'expanded_rebus_test/cases.json').read_text())['panels']
    inventory=[]
    for panel,cs in panels.items():
        for i,c in enumerate(cs,1):
            rep=rep_by_sign.get(c['sign'],{}) if panel=='fixed48' else {}
            inventory.append(dict(claim_id=f'{panel}:{i:03}',panel=panel,sign=c['sign'],
                title=c['title'],picture_pattern=c['a_en'],target_pattern=c['b_en'],
                picture_etyma=';'.join(rep.get('a_entries',[])),target_etyma=';'.join(rep.get('b_entries',[])),
                source_path=c['source'],scope='cited etyma and unchanged meanings' if rep else 'unchanged meanings; unrestricted dictionary etyma'))
    write(out/'all_existing_pair_recipes.csv',inventory)
    candidate_rows=[]; level_rows=[]; witnesses=[]; cells_by_claim=collections.defaultdict(list)
    group_keys=sorted({(r['reference'],r['source_classification']) for r in raw})
    group_rows={key:[r for r in raw if (r['reference'],r['source_classification'])==key] for key in group_keys}
    claim_cache={}
    for c in inventory:
        arx=re.compile(c['picture_pattern'],re.I); brx=re.compile(c['target_pattern'],re.I)
        ae=set(c['picture_etyma'].split(';'))-{''};be=set(c['target_etyma'].split(';'))-{''}
        aa=[r for r in raw if (not ae or r['number'] in ae) and arx.search(r['meaning'])]
        bb=[r for r in raw if (not be or r['number'] in be) and brx.search(r['meaning'])]
        claim_cache[c['claim_id']]=(aa,bb)
        for side,rs in [('picture',aa),('target',bb)]:
            for r in rs:candidate_rows.append(dict(claim_id=c['claim_id'],panel=c['panel'],sign=c['sign'],title=c['title'],side=side,**{k:v for k,v in r.items() if not k.startswith('_')}))
        for reference,level in group_keys:
            a=[r for r in aa if (r['reference'],r['source_classification'])==(reference,level)]
            b=[r for r in bb if (r['reference'],r['source_classification'])==(reference,level)]
            hits=[]
            for x,y in itertools.product(a,b):
                overlap=set(x['_forms'])&set(y['_forms'])
                for f in sorted(overlap):
                    w=dict(claim_id=c['claim_id'],panel=c['panel'],sign=c['sign'],title=c['title'],
                        reference=reference,ancestral_level=level,comparison_form=f,
                        picture_record=x['id_pdr'],target_record=y['id_pdr'],picture_etymon=x['number'],target_etymon=y['number'],
                        picture_form=x['reconstruction'],target_form=y['reconstruction'],
                        picture_gloss=x['meaning'],target_gloss=y['meaning'],
                        picture_attestation_level=x['evidence_classification'],target_attestation_level=y['evidence_classification'],
                        both_attestation_flags_at_source_level=x['evidence_verdict']=='supported at level' and y['evidence_verdict']=='supported at level',
                        match_kind='same reconstructed record covers both domains' if x['id_pdr']==y['id_pdr'] else ('same etymon with two reconstructed records' if x['number']==y['number'] else 'distinct etyma; equal recorded reconstruction'),
                        qualification=sense_qualification(c,x,y,f),
                        qualified=concrete(f) and sense_qualification(c,x,y,f).startswith('No specified'),
                        validation='lexical screen; source transcription and exact word senses require review')
                    hits.append(w); witnesses.append(w)
            status=('Equal recorded reconstruction' if hits else 'Both meanings recorded; forms differ' if a and b else 'Picture meaning only' if a else 'Target meaning only' if b else 'Neither meaning recorded')
            rec=dict(claim_id=c['claim_id'],panel=c['panel'],sign=c['sign'],title=c['title'],reference=reference,
                ancestral_level=level,picture_records=len(a),target_records=len(b),equal_form_witnesses=len(hits),
                strict_attestation_witnesses=sum(h['both_attestation_flags_at_source_level'] for h in hits),
                qualified_equal_witnesses=sum(h['qualified'] for h in hits),
                qualified_attestation_witnesses=sum(h['qualified'] and h['both_attestation_flags_at_source_level'] for h in hits),
                status=status,picture_reconstructions=compact(a),target_reconstructions=compact(b))
            level_rows.append(rec);cells_by_claim[c['claim_id']].append(rec)
    write(out/'all_pair_level_results.csv',level_rows)
    write(out/'all_pair_reconstruction_candidates.csv',candidate_rows)
    write(out/'equal_form_witnesses.csv',witnesses)
    summaries=[]
    for c in inventory:
        cc=cells_by_claim[c['claim_id']]
        old=[x for x in cc if x['reference'] in PUBLISHED]
        pd=[x for x in old if x['ancestral_level']==PD]
        other=[x for x in old if x['ancestral_level']!=PD]
        samepd=any(x['equal_form_witnesses'] for x in pd)
        sub=any(x['equal_form_witnesses'] for x in other)
        if samepd:status='Equal forms in an older-source Proto-Dravidian record'
        elif sub:status='Equal forms recorded only at a subgroup level in this screen'
        elif any(x['picture_records'] and x['target_records'] for x in old):status='Both meanings recorded together; no exact reconstruction equality'
        else:status='Incomplete two-sided reconstruction coverage'
        summaries.append(dict(**c,published_PD_equal=samepd,
            published_PD_equal_with_both_attestation_flags=any(x['strict_attestation_witnesses'] for x in pd),
            qualified_published_PD_equal=any(x['qualified_equal_witnesses'] for x in pd),
            qualified_published_PD_equal_attestation_flags=any(x['qualified_attestation_witnesses'] for x in pd),
            published_subgroup_equal=sub,
            compiler_new_PD_equal=any(x['equal_form_witnesses'] for x in cc if x['reference'] not in PUBLISHED and x['ancestral_level']==PD),
            assessment=status,PD_evidence=' || '.join(x['reference']+': '+x['status']+' — '+x['picture_reconstructions']+' <> '+x['target_reconstructions'] for x in pd),
            equal_subgroups='; '.join(sorted({x['ancestral_level'] for x in other if x['equal_form_witnesses']})),
            dated_to_Indus_period=False,sign_meaning_validated=False))
    write(out/'pair_summary.csv',summaries)
    differences=[]
    for c in inventory:
        aa,bb=claim_cache[c['claim_id']]
        for ref in sorted(PUBLISHED):
            candidates=[]
            for a,b in itertools.product(aa,bb):
                if a['reference']!=ref or b['reference']!=ref or a['source_classification']!=PD or b['source_classification']!=PD:continue
                for af,bf in itertools.product(a['_forms'],b['_forms']):
                    if not concrete(af) or not concrete(bf):continue
                    d=edit_distance(af,bf)
                    candidates.append((d,a['id_pdr'],b['id_pdr'],af,bf,a,b))
            if candidates:
                minimum=min(x[0] for x in candidates)
                for d,aid,bid,af,bf,a,b in candidates:
                    if d!=minimum:continue
                    changes='; '.join(f'{tag}: {af[i:j] or "∅"} → {bf[k:l] or "∅"}' for tag,i,j,k,l in difflib.SequenceMatcher(None,af,bf).get_opcodes() if tag!='equal')
                    differences.append(dict(claim_id=c['claim_id'],panel=c['panel'],sign=c['sign'],title=c['title'],reference=ref,
                        picture_form=a['reconstruction'],target_form=b['reconstruction'],picture_meaning=a['meaning'],target_meaning=b['meaning'],
                        picture_record=aid,target_record=bid,minimum_written_form_edits=d,written_differences=changes,
                        interpretation='Transcription diagnostic only; edit count is not a phonological model or a date. Differences may reflect length, morphology, uncertain reconstruction or transcription conventions.'))
    write(out/'nearest_PD_form_differences.csv',differences)
    # Direct meanings in the 67-representative catalogue remain a separate
    # concept-coverage check, not additional two-sided rebus successes.
    direct=[]
    for c in reps:
        if c['kind'] in ('bridge','polysemy'):continue
        side='b' if any(t.strip() for t in c['b']) else 'a'
        rx=terms_rx(c[side]); allowed=set(c[side+'_entries'])
        hits=[r for r in raw if (not allowed or r['number'] in allowed) and rx.search(r['meaning'])]
        for r in hits:direct.append(dict(sign=c['sign'],title=c['title'],kind=c['kind'],**{k:v for k,v in r.items() if not k.startswith('_')}))
    write(out/'direct_meaning_reconstructions.csv',direct)
    # All homophonous pairs in the entire larger table, including forms absent
    # from the present key. Different sources/levels never form one pair.
    hom_groups=collections.defaultdict(list)
    for r in raw:
        for f in r['_forms']: hom_groups[(r['reference'],r['source_classification'],f)].append(r)
    discoveries=[]
    for (ref,level,f),rs in sorted(hom_groups.items()):
        for a,b in itertools.combinations(rs,2):
            if not a['number'] or not b['number'] or a['number']==b['number'] or a['meaning']==b['meaning']:continue
            discoveries.append(dict(reference=ref,ancestral_level=level,comparison_form=f,
                first_record=a['id_pdr'],second_record=b['id_pdr'],first_etymon=a['number'],second_etymon=b['number'],
                first_form=a['reconstruction'],second_form=b['reconstruction'],first_meaning=a['meaning'],second_meaning=b['meaning'],
                first_attestation_level=a['evidence_classification'],second_attestation_level=b['evidence_classification'],
            published_source=ref in PUBLISHED,fully_specified_form=concrete(f),existing_Indus_reading=False))
    write(out/'full_table_equal_form_pairs.csv',discoveries)
    proposed_signs={p['sign'] for p in json.loads((BASE.parent/'frozen/proposals.json').read_text())}
    anchor_candidates=[]; anch_seen=set()
    # New alternatives must share a reconstructed form with a recorded picture
    # meaning from an existing recipe. All other meanings remain exploratory.
    for c in inventory:
        if c['sign'] not in proposed_signs:continue
        aa,_=claim_cache[c['claim_id']]
        current_targets=[re.compile(x['target_pattern'],re.I) for x in inventory if x['sign']==c['sign']]
        for a in aa:
            if a['reference'] not in PUBLISHED:continue
            for f in a['_forms']:
                for b in hom_groups[(a['reference'],a['source_classification'],f)]:
                    if not a['number'] or not b['number'] or a['number']==b['number']:continue
                    if any(rx.search(b['meaning']) for rx in current_targets):continue
                    if not concrete(f):continue
                    if c['sign']=='892' and re.search(r'\bto bow\b',a['meaning'],re.I):continue
                    if c['sign']=='220' and re.search(r'fish[- ]hook',a['meaning'],re.I):continue
                    key=(c['sign'],a['id_pdr'],b['id_pdr'],f)
                    if key in anch_seen:continue
                    anch_seen.add(key)
                    anchor_candidates.append(dict(sign=c['sign'],picture_recipe=c['title'],
                        reference=a['reference'],ancestral_level=a['source_classification'],comparison_form=f,
                        picture_record=a['id_pdr'],alternative_record=b['id_pdr'],picture_etymon=a['number'],alternative_etymon=b['number'],
                        picture_form=a['reconstruction'],alternative_form=b['reconstruction'],
                        picture_meaning=a['meaning'],alternative_meaning=b['meaning'],
                        discovery_status='Exploratory dictionary alternative; not a new translation or validation',
                        new_ancient_evidence=False))
    write(out/'new_picture_anchored_alternatives.csv',anchor_candidates)
    # Apply sign-level findings to every corpus observation. Repeated occurrences
    # describe reach only; they never multiply the number of lexical successes.
    tree=ast.parse((REPO/'work_scripts/key6b_readings_key5_atlas.py').read_text())
    meta=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SIGN_META' for t in n.targets)))
    proposals=json.loads((BASE.parent/'frozen/proposals.json').read_text())
    fixed_by_sign={x['sign']:x for x in summaries if x['panel']=='fixed48'}
    all_by_sign=collections.defaultdict(list)
    for x in summaries:all_by_sign[x['sign']].append(x)
    sign_rows=[];root_links=[];component_rows=[]
    direct_by_sign=collections.defaultdict(list)
    for r in direct:direct_by_sign[r['sign']].append(r)
    nums={'oru':'001','iru':'002','mū':'003','nāl':'004','ai':'005','aṟu':'006','ēḻ':'007','eṇ':'008','oṉpatu':'025','pattu':'028','paṉṉiru':'055'}
    component_etyma=collections.defaultdict(set)
    def proposed_pieces(root):
        root=re.sub(r'\[(?:BRACKET|ROOF|CAGE)\]','',root)
        ss=re.findall(r'\*([^\s*/~\[\](),]+)',re.split(r'\s*\[',root)[0])
        return sorted({form(bit) for word in ss for bit in word.split('-') if bit and not bit.isdigit() and not re.fullmatch('[A-Z]+',bit)})
    for c in reps:
        for bit in proposed_pieces(c['proposal_root']):component_etyma[bit].update(c['a_entries']+c['b_entries'])
    shape_rows={r['lipi_wells_number']:r['shape_description'] for r in rows(REPO/'work_data/sign_shapes.csv')}
    for p in proposals:
        s=p['sign'];family=meta.get(s,('',)*4)[3] if s in meta else ''
        family_rep=family.split('_')[0] if family else ''
        m=re.match(r'\*([^\s/\[()]+)',p['root_or_gloss']); simple=m[1] if m else ''
        rep=s if s in rep_by_sign else (family_rep if family_rep in rep_by_sign else nums.get(simple,''))
        pair=fixed_by_sign.get(rep);others=all_by_sign.get(s,[])
        aa=direct_by_sign.get(rep,[])
        if pair:
            status=pair['assessment'];pdhit=pair['qualified_published_PD_equal'];attested=pair['qualified_published_PD_equal_attestation_flags']
            if pair['published_PD_equal'] and not pdhit:status='Apparent equality excluded by the semantic or unspecified-form review'
        elif aa:status='Direct meaning coverage; no two-sided pun tested';pdhit=False;attested=False
        else:status='Compound, variant or word value without a representative two-sided test';pdhit=False;attested=False
        allowed=set(re.findall(r'(?:DEDR|DIRECT)\s+(\d{1,4}[a-z]?)\b',p['evidence_note']))
        if rep in rep_by_sign:
            rc=rep_by_sign[rep];allowed.update(rc['a_entries']);allowed.update(rc['b_entries'])
        exact_proposal_forms={form(x) for x in re.findall(r'\*([^\s*/~\[\](),]+)',re.split(r'\s*\[',p['root_or_gloss'])[0])}
        linked=[]
        for r in raw:
            reason='cited DEDR etymon' if r['number'] in allowed else ('exact proposed full form; meaning not automatically verified' if exact_proposal_forms & set(r['_forms']) else '')
            if reason:
                linked.append(r)
                root_links.append(dict(sign=s,proposed_meaning=p['short_gloss'],proposal_root=p['root_or_gloss'],link_basis=reason,**{k:v for k,v in r.items() if not k.startswith('_')}))
        pieces=proposed_pieces(p['root_or_gloss']); pieces_linked=0;component_ids=set()
        for bit in pieces:
            component_matches=[]
            for r in raw:
                reason='explicit component: cited etymon family' if r['number'] in component_etyma[bit] else ('explicit component: same recorded form; meaning unverified' if bit in r['_forms'] else '')
                if reason:
                    component_matches.append(r);component_ids.add(r['id_pdr'])
                    component_rows.append(dict(sign=s,proposal_root=p['root_or_gloss'],proposed_component=bit,link_basis=reason,**{k:v for k,v in r.items() if not k.startswith('_')}))
            pieces_linked+=bool(component_matches)
        sign_rows.append(dict(sign=s,proposed_meaning=p['short_gloss'],proposed_root=p['root_or_gloss'],shape=shape_rows.get(s,''),
            representative_sign=rep,representative_pair=pair['title'] if pair else '',assessment=status,
            published_PD_equal_pair=pdhit,published_PD_equal_pair_attestation_flags=attested,
            additional_existing_pair_recipes=len(others),linked_reconstruction_records=len(linked),
            explicit_components='; '.join(pieces),explicit_components_count=len(pieces),components_with_lexical_links=pieces_linked,
            component_reconstruction_records=len(component_ids),
            published_PD_linked_records=sum(r['reference'] in PUBLISHED and r['source_classification']==PD for r in linked),
            caveat='Variant/compound links describe component vocabulary, not proof of the full reading; etymon links do not establish every English sense.'))
    write(out/'all_163_sign_results.csv',sign_rows)
    write(out/'all_163_reconstruction_links.csv',root_links)
    write(out/'all_explicit_component_links.csv',component_rows)
    sr={r['sign']:r for r in sign_rows}
    catalogue=rows(BASE.parent/'translation_catalogue/results/all_inscriptions.csv')
    per_ins=[]
    for r in catalogue:
        toks=r['sign_sequence'].split('-') if r['sign_sequence'] else []
        signs=set(toks)&set(sr)
        strict=[s for s in sorted(signs) if sr[s]['published_PD_equal_pair']]
        checked=[s for s in sorted(signs) if sr[s]['representative_pair']]
        additional=[s for s in sorted(signs) if any(x['qualified_published_PD_equal'] for x in all_by_sign.get(s,[]))]
        per_ins.append(dict(catalogue=r['catalogue'],face_id=r['face_id'],reference=r['reference'],city=r['city'],
            existing_proposed_translation=r['existing_proposed_translation'],sign_sequence=r['sign_sequence'],
            excavation_area=r['excavation_area'],block_or_house=r['block_or_house'],room_or_grid=r['room_or_grid'],depth_recorded=r['depth_recorded'],
            PD_equal_pair_signs='; '.join(strict),PD_equal_pair_meanings='; '.join(sr[s]['proposed_meaning'] for s in strict),
            existing_pair_tested_signs='; '.join(checked),
            signs_with_additional_PD_equal_recipes='; '.join(additional),
            component_linked_signs='; '.join(s for s in sorted(signs) if sr[s]['components_with_lexical_links']),
            distinct_current_signs=len(signs),distinct_PD_equal_pair_signs=len(strict),
            every_current_sign_has_PD_equal_pair=bool(signs) and len(strict)==len(signs) and len(signs)==len(set(toks)),
            all_words_dated_to_Indus_period=False,translation_independently_validated=False,
            interpretation='Lexical findings propagated to recorded occurrences; no inscription has acquired an independently validated translation.'))
    write(out/'all_inscriptions_reconstruction_screen.csv',per_ins)
    panels_summary=[]
    for name in panels:
        ss=[s for s in summaries if s['panel']==name]
        panels_summary.append(dict(panel=name,recipes=len(ss),sign_ids=len({s['sign'] for s in ss}),
            published_PD_equal=sum(s['published_PD_equal'] for s in ss),
            published_PD_equal_attestation_flags=sum(s['published_PD_equal_with_both_attestation_flags'] for s in ss),
            qualified_published_PD_equal=sum(s['qualified_published_PD_equal'] for s in ss),
            qualified_published_PD_equal_attestation_flags=sum(s['qualified_published_PD_equal_attestation_flags'] for s in ss),
            published_subgroup_equal=sum(s['published_subgroup_equal'] for s in ss),
            incomplete_two_sided=sum(s['assessment']=='Incomplete two-sided reconstruction coverage' for s in ss)))
    write(out/'panel_summary.csv',panels_summary)
    source_counts=collections.Counter((r['reference'],r['source_classification']) for r in raw)
    write(out/'source_level_inventory.csv',[dict(reference=k[0],ancestral_level=k[1],records=v) for k,v in sorted(source_counts.items())])
    summary=dict(source_url='https://zenodo.org/records/22682542',source_version='1.2',
        source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),source_records=len(raw),
        unique_linked_DEDR_etyma=len({r['number'] for r in raw if r['number']}),
        source_PD_records=sum(r['source_classification']==PD for r in raw),
        published_PD_records=sum(r['source_classification']==PD and r['reference'] in PUBLISHED for r in raw),
        existing_pair_recipes=len(inventory),candidate_sign_ids=len({c['sign'] for c in inventory}),
        current_signs=len(sign_rows),current_signs_with_reconstruction_links=sum(bool(s['linked_reconstruction_records']) for s in sign_rows),
        current_signs_with_component_links=sum(bool(s['components_with_lexical_links']) for s in sign_rows),
        total_explicit_components=sum(s['explicit_components_count'] for s in sign_rows),
        explicit_components_with_lexical_links=sum(s['components_with_lexical_links'] for s in sign_rows),
        panels=panels_summary,full_table_equal_form_pairs=len(discoveries),
        published_PD_equal_form_pairs=sum(x['published_source'] and x['ancestral_level']==PD for x in discoveries),
        picture_anchored_alternatives=len(anchor_candidates),
        published_PD_picture_anchored_alternatives=sum(x['ancestral_level']==PD for x in anchor_candidates),
        corpus_records_screened=len(per_ins),corpus_records_with_at_least_one_PD_equal_pair=sum(bool(x['distinct_PD_equal_pair_signs']) for x in per_ins),
        dating='No absolute date inferred from a reconstruction label.',
        independence='Older lexical reconstructions predate Cuper key; original proposed sign meanings remain selected hypotheses.',
        interpretation='A full-table lexical screen, not newly performed historical reconstruction, sound-law dating, or independent decipherment.')
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    (out/'pair_summary.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2)+'\n')
    (out/'input_table.csv.gz').write_bytes(gzip.compress(Path(source).read_bytes(),mtime=0))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);main(ap.parse_args().source)
