"""Collect existing readings, retaining catalogue identity and recorded findspots.

Run before the reconstruction comparison. No new fluent translations are invented.
"""
import argparse, collections, csv, hashlib, html, json, re, subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
URL = 'https://github.com/MSaadAsad/ivc-semantic/blob/research/independent-validation-2026-11-20/'

def rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def write(path, data, fields=None):
    data = list(data)
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(data[0]), lineterminator='\n')
        w.writeheader(); w.writerows(data)

def known(s):
    return bool(s and re.sub(r'[\s?–—-]', '', str(s)).lower() not in ('', 'unknown', 'none', 'na', 'n/a'))

def build(metadata):
    out = BASE / 'results'; out.mkdir(parents=True, exist_ok=True)
    corpus_path = 'work_data/reader_v3/corpus_soundfree_readings.csv'
    corpus = rows(REPO / corpus_path)
    lipi = {r['id']: r for r in rows(metadata)}
    mah = {str(i): r for i, r in enumerate(rows(REPO / 'work_data/mahadevan_parsed.csv'))}
    by_reference=collections.defaultdict(list)
    by_object=collections.defaultdict(list)
    for r in corpus:
        key=(r['catalogue'],r['id'])
        if r['catalogue']=='Lipi':
            by_reference[lipi[r['id']]['cisi']].append(key)
            by_object[r['id'].split('.')[0]].append(key)
        else:
            by_reference['Mah '+mah[r['id']]['textnum']].append(key)
    def resolve_reference(ref, seq=''):
        keys=by_reference.get(ref,[])
        if len(keys)>1 and seq:
            exact=[k for k in keys if next(r['signs'] for r in corpus if (r['catalogue'],r['id'])==k)==seq]
            if exact: return exact
            return []
        return keys
    archived = []; by_key = collections.defaultdict(list); source_counts = collections.Counter()
    sequence_readings = collections.defaultdict(list)

    def add(key, source, rownum, english='', sounds='', signs='', status='', kind='recorded reading'):
        a = dict(catalogue=key[0], face_id=key[1], reading_kind=kind,
                 source_path=source, source_row=rownum, source_url=URL+source,
                 proposed_english=english, proposed_sounds=sounds, sign_sequence=signs,
                 source_status=status)
        archived.append(a); by_key[key].append(a); source_counts[source] += 1

    # Every corpus observation remains a distinct row. Paired catalogues are not
    # treated as independent physical objects or silently merged by text identity.
    for i,r in enumerate(corpus, 2):
        add((r['catalogue'],r['id']),corpus_path,i,r['soundfree_reading'],'',r['signs'],
            'structural labels; not a spoken-language translation','structural reading')
    for i,r in enumerate(mah.values(), 2):
        add(('Mahadevan',str(i-2)),'work_data/mahadevan_parsed.csv',i,r['gloss'],'',r['reading_lipi'],
            'structural interpretation','structural reading')

    # Discover all object/face English exports in work_data, including earlier
    # registers and selected examples. Sign dictionaries are handled separately.
    csv_paths=sorted((REPO/'work_data').rglob('*.csv'))+sorted((REPO/'work_scripts').rglob('*.csv'))
    for p in csv_paths:
        data = rows(p)
        if not data: continue
        source = str(p.relative_to(REPO)); fields = data[0]
        if 'english_reading' in fields and 'catalogue' in fields:
            for i,r in enumerate(data,2):
                add((r['catalogue'],r['id']),source,i,r['english_reading'],r['proto_dravidian'],r.get('raw_signs',r['signs']),
                    'unknown Mahadevan signs present' if r.get('has_unmapped_mahadevan_x')=='True' else 'source key fully assigned')
        elif 'english' in fields and 'face_id' in fields and 'signs' in fields:
            for i,r in enumerate(data,2):
                add(('Lipi',r['face_id']),source,i,r['english'],r.get('sounds',''),r['signs'],r.get('grade_strict',r.get('grade','')))
                if r.get('old_english'):
                    add(('Lipi',r['face_id']),source,i,r['old_english'],'',r['signs'],'earlier English preserved in old_english field','earlier reading')
        elif 'english' in fields and 'src' in fields and 'id' in fields:
            for i,r in enumerate(data,2):
                keys=resolve_reference(r['id'],r.get('text','')) or [('Unresolved reference',r['id'])]
                for key in keys: add(key,source,i,r['english'],r.get('sounds',''),r.get('text',''),r.get('grade',''))
        elif 'english' in fields and 'obj' in fields:
            for i,r in enumerate(data,2):
                keys=by_object.get(r['obj'],[]) or [('Unresolved object',r['obj'])]
                for key in keys: add(key,source,i,r['english'],r.get('sounds',''),r.get('signs_ce',r.get('text','')),'object-level reading; may span faces','object-level reading')
        elif 'gloss' in fields and 'catalogue' in fields and 'id' in fields:
            for i,r in enumerate(data,2): add((r['catalogue'],r['id']),source,i,r['gloss'],'',r.get('signs',''),'existing literal roots','literal reading')
        elif 'gloss' in fields and 'reading_order_text' in fields and 'id' in fields:
            for i,r in enumerate(data,2): add(('Lipi',r['id']),source,i,r['gloss'],'',r['reading_order_text'],'structural interpretation','structural reading')
        elif 'id' in fields and 'cisi' in fields and ('english' in fields or 'gloss' in fields):
            for i,r in enumerate(data,2):
                add(('Lipi',r['id']),source,i,r.get('english',r.get('gloss','')),r.get('sounds',''),r.get('text',''),
                    'earlier interpretation retained verbatim','recorded reading' if 'english' in fields else 'structural reading')
        elif 'gloss' in fields and 'cisi' in fields and 'cat' in fields:
            for i,r in enumerate(data,2):
                ref=r['cisi'] if r['cat']=='L' else ('Mah '+re.sub(r'^(?:Mah\s+)?M?', '',r['cisi']))
                for key in resolve_reference(ref,r.get('text','')) or [('Unresolved reference',ref)]:
                    add(key,source,i,r['gloss'],r.get('sound',''),r.get('text',''),'earlier star reading')
                    archived[-1].update(source_city=r['site'],source_reference=r['cisi'])
        elif source=='work_data/abroad2/foreign_read_whole.csv':
            for i,r in enumerate(data,2): add(('Lipi',r['id']),source,i,r['reading'],'',r['text'],'earlier foreign-object interpretation')
        elif 'museum_or_lipi_id' in fields and ('gloss' in fields or 'gloss_19_locked' in fields):
            for i,r in enumerate(data,2):
                m=re.search(r'Lipi\s+(\d+\.\d+)',r['museum_or_lipi_id'])
                keys=[('Lipi',m[1])] if m and m[1] in lipi else resolve_reference(r['museum_or_lipi_id'],r.get('seq_ordered',''))
                if not keys: keys=[('Frontier',r['fid'])]
                for key in keys:
                    add(key,source,i,r.get('gloss',r.get('gloss_19_locked','')),'',r.get('seq_ordered',''),r.get('inscribed_status',''),'frontier literal reading')
                    archived[-1].update(source_city=r['site'],source_reference=r['museum_or_lipi_id'])
        elif 'english_reading' in fields and 'signs' in fields:
            for i,r in enumerate(data,2): sequence_readings[r['signs']].append((source,i,r['english_reading'],r.get('proto_dravidian',''),'existing formula reading'))
        elif 'pdrav_reading' in fields and 'signs' in fields:
            for i,r in enumerate(data,2): sequence_readings[r['signs']].append((source,i,r.get('gloss',''),r['pdrav_reading'],'existing formula roots'))
    tests_path = 'research/independent_validation_20261120/results/inscription_tests_60.csv'
    for i,r in enumerate(rows(REPO/tests_path),2):
        add((r['catalogue'],r['catalogue_id']),tests_path,i,r['literal_proposed_senses'],r['literal_frozen_roots'],r['exact_sequence'],'unvalidated literal proposal','literal reading')
    for r in corpus:
        for source,i,eng,sounds,kind in sequence_readings[r['signs']]:
            add((r['catalogue'],r['id']),source,i,eng,sounds,r['signs'],'formula applied only to an identical recorded sequence',kind)

    proposals = json.loads((BASE.parent/'frozen/proposals.json').read_text())
    lex = {r['sign']:r for r in proposals}
    seen = set(); result=[]
    priorities = ['work_data/key6b/decoded_2262_corpus.csv','work_data/key5b/decoded_1776_corpus.csv',
                  'work_data/corpus_english3.csv','work_data/corpus_english2.csv','work_data/corpus_english.csv']
    counts = collections.Counter(); sites=collections.defaultdict(collections.Counter)
    for r in corpus:
        key=(r['catalogue'],r['id']); assert key not in seen; seen.add(key)
        raw = lipi.get(r['id'],{}) if key[0]=='Lipi' else mah.get(r['id'],{})
        assert raw, key
        variants=by_key[key]
        best=next((v for p in priorities for v in variants if v['source_path']==p),None)
        if best is None:
            best=next((v for v in variants if v['proposed_sounds']), variants[0])
        if key[0]=='Lipi':
            reference = raw['cisi'] if known(raw['cisi']) else 'Lipi-'+r['id']
            object_id='Lipi:'+r['id'].split('.')[0]
            context={k:raw.get(v,'') for k,v in dict(excavation_area='area-section',block_or_house='block-house',room_or_grid='room-grid',depth_recorded='depth',period_recorded='period',phase_recorded='phase',chronology_recorded='time',excavation_number='excavation-idno',material='material',object_type='type',preservation='preservation',region='region').items()}
            meta_source='research/data/open_prototype/lipi/metadata_filtered.csv'
        else:
            reference='Mahadevan '+raw['textnum']+' / line '+raw['sideline']
            object_id='Mahadevan text:'+raw['textnum']
            context=dict(excavation_area=raw['locus'],block_or_house='',room_or_grid='',
                         depth_recorded=raw['level'],period_recorded='',phase_recorded='',chronology_recorded='',
                         excavation_number='',material='',object_type=raw['cls'],preservation='',region='')
            meta_source='work_data/mahadevan_parsed.csv'
        hascontext=any(known(context[x]) for x in ['excavation_area','block_or_house','room_or_grid','depth_recorded','excavation_number'])
        context_status='Recorded findspot fields available' if hascontext else 'Detailed findspot not recorded in supplied catalogue'
        if key[0]=='Mahadevan' and hascontext: context_status='Mahadevan locus/level codes; interpretation not expanded'
        toks=r['signs'].split('-') if r['signs'] else []
        recognized=[t for t in toks if t in lex]; unknown=[t for t in toks if t not in lex]
        literal=' ; '.join(t+'='+lex[t]['short_gloss'] if t in lex else (t or '[empty segment]')+'=[unassigned]' for t in toks)
        roots=' ; '.join(t+'='+lex[t]['root_or_gloss'] if t in lex else (t or '[empty segment]')+'=[unassigned]' for t in toks)
        interpreted=[v for v in variants if v['proposed_sounds'] or v['reading_kind']=='literal reading']
        status='Full proposed sign assignment' if toks and not unknown else ('Partial proposed sign assignment' if recognized else 'No proposed 163-key assignment')
        counts[status]+=1; sites[r['site']][status]+=1
        rec=dict(catalogue=key[0],face_id=key[1],reference=reference,object_identifier=object_id,
                 city=r['site'],existing_proposed_translation=best['proposed_english'],
                 existing_proposed_sounds=best['proposed_sounds'],existing_reading_source=best['source_path'],
                 existing_reading_source_row=best['source_row'],existing_reading_status=best['source_status'],
                 current_163_key_literal_meanings=literal,current_163_key_roots=roots,
                 assignment_status=status,assigned_sign_tokens=len(recognized),total_sign_tokens=len(toks),
                 unassigned_signs='; '.join(unknown),sign_sequence=r['signs'],
                 intact_as_recorded=r['intact'],paired_in_other_catalogue=r['partnered'],
                 structural_reading=r['soundfree_reading'],existing_language_reading_records=len(interpreted),
                 archived_reading_records=len(variants),context_status=context_status,**context,
                 context_source=meta_source,context_source_url=URL+meta_source,
                 reading_validated=False)
        result.append(rec)
    record_by_key={(r['catalogue'],r['face_id']):r for r in result}
    for a in archived:
        rec=record_by_key.get((a['catalogue'],a['face_id']))
        a['city']=rec['city'] if rec else a.get('source_city','Not resolved')
        a['reference']=rec['reference'] if rec else a.get('source_reference',a['face_id'])
        for field in ['excavation_area','block_or_house','room_or_grid','depth_recorded','period_recorded','context_status']:
            a[field]=rec[field] if rec else 'Not resolved from supplied source'
        a.pop('source_city',None); a.pop('source_reference',None)
    extras=[a for a in archived if (a['catalogue'],a['face_id']) not in seen]
    write(out/'all_inscriptions.csv',result)
    write(out/'all_existing_reading_versions.csv',archived)
    if extras: write(out/'reading_records_outside_main_corpus.csv',extras)
    signrows=[]
    for p in proposals:
        uses=[r for r in result if p['sign'] in r['sign_sequence'].split('-')]
        signrows.append(dict(sign=p['sign'],proposed_root=p['root_or_gloss'],proposed_meaning=p['short_gloss'],
                             proposal_source=p['source_lever'],evidence_note=p['evidence_note'],
                             catalogue_face_records=len(uses),cities='; '.join(sorted({r['city'] for r in uses}))))
    write(out/'all_163_sign_readings.csv',signrows)
    cityrows=[dict(city=s,catalogue_face_records=sum(c.values()),**{k:c[k] for k in counts}) for s,c in sorted(sites.items())]
    write(out/'by_city.csv',cityrows)
    summary=dict(catalogue_face_records=len(result),catalogues=dict(collections.Counter(r['catalogue'] for r in result)),
                 cities=len(sites),assignment_counts=dict(counts),archived_reading_records=len(archived),
                 existing_language_reading_faces=sum(r['existing_language_reading_records']>0 for r in result),
                 detailed_context_available=sum('not recorded' not in r['context_status'] for r in result),
                 reading_records_outside_main_corpus=len(extras),sources=dict(source_counts),
                 source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
                 metadata_sha256=hashlib.sha256(Path(metadata).read_bytes()).hexdigest(),
                 count_unit='catalogue face/line records; paired catalogues and repeated objects are retained, not independent artifacts',
                 caution='All translations remain proposals. Zero unassigned signs is a mapping-completeness count, not evidence of decipherment.')
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    (out/'workbook_data.json').write_text(json.dumps(dict(inscriptions=result,signs=signrows,cities=cityrows,summary=summary),ensure_ascii=False))
    make_html(result,summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2))

def make_html(data, summary):
    # Standalone local catalogue: no network, server, libraries or hidden records.
    fields=['reference','city','existing_proposed_translation','existing_proposed_sounds','assignment_status',
            'excavation_area','block_or_house','room_or_grid','depth_recorded','period_recorded',
            'phase_recorded','material','object_type','sign_sequence','current_163_key_literal_meanings',
            'context_status','existing_reading_source','face_id','catalogue']
    payload=json.dumps([{k:r[k] for k in fields} for r in data],ensure_ascii=False).replace('</','<\\/')
    page='''<!doctype html><meta charset="utf-8"><title>Indus inscription catalogue</title>
<style>body{font:16px Arial,sans-serif;color:#172638;background:#f6f8fa;margin:32px}h1{font-size:30px}p{max-width:1100px;line-height:1.5}input,select,button{font:inherit;padding:10px;margin:0 12px 12px 0}input{width:420px}table{border-collapse:collapse;background:white;width:100%;font-size:14px}th,td{text-align:left;padding:12px;vertical-align:top;border-bottom:1px solid #dce2e7;min-width:100px}th{background:#233c53;color:white;position:sticky;top:0}td:nth-child(3){min-width:350px}td:nth-child(4){min-width:250px}.scroll{overflow:auto;max-height:72vh}#count{font-weight:bold}</style>
<h1>Indus inscriptions: proposed readings and findspots</h1>
<p>All CATALOGUE_COUNT catalogue face/line records. Translations are existing proposals, not established readings. Repeated texts, different faces and paired catalogue entries remain visible. Excavation fields are reproduced from the catalogues; missing context has not been guessed. “Full proposed sign assignment” means that every token has a label in the 163-sign key.</p>
<input id="q" placeholder="Search meanings, reference, signs or excavation context"><select id="city"><option value="">Every city</option></select><select id="status"><option value="">Every assignment status</option></select><button id="prev">Previous</button><button id="next">Next</button><p id="count"></p><div class="scroll"><table><thead><tr>HEADERS</tr></thead><tbody id="body"></tbody></table></div>
<script>const records=PAYLOAD, fields=FIELDS;let page=0,filtered=records;const size=100;
const el=id=>document.getElementById(id);for(const key of ['city','status']){let f=key==='status'?'assignment_status':key;for(const v of [...new Set(records.map(r=>r[f]))].sort()){let o=document.createElement('option');o.value=v;o.textContent=v;el(key).appendChild(o)}}
function draw(){const q=el('q').value.toLowerCase(),city=el('city').value,status=el('status').value;filtered=records.filter(r=>(!city||r.city===city)&&(!status||r.assignment_status===status)&&(!q||Object.values(r).join(' ').toLowerCase().includes(q)));page=Math.min(page,Math.max(0,Math.ceil(filtered.length/size)-1));el('body').replaceChildren();for(const r of filtered.slice(page*size,(page+1)*size)){const tr=document.createElement('tr');for(const f of fields){const td=document.createElement('td');td.textContent=r[f]||'Not recorded';tr.appendChild(td)}el('body').appendChild(tr)}el('count').textContent=`${filtered.length.toLocaleString()} records; page ${page+1} of ${Math.max(1,Math.ceil(filtered.length/size))}`;el('prev').disabled=page===0;el('next').disabled=(page+1)*size>=filtered.length}
for(const id of ['q','city','status'])el(id).addEventListener('input',()=>{page=0;draw()});el('prev').onclick=()=>{page--;draw()};el('next').onclick=()=>{page++;draw()};draw();</script>'''
    headers=''.join('<th>'+html.escape(k.replace('_',' ').title())+'</th>' for k in fields)
    page=page.replace('CATALOGUE_COUNT',str(len(data))).replace('HEADERS',headers).replace('PAYLOAD',payload).replace('FIELDS',json.dumps(fields))
    (BASE/'results/catalogue.html').write_text(page)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lipi-metadata',required=True)
    build(ap.parse_args().lipi_metadata)
