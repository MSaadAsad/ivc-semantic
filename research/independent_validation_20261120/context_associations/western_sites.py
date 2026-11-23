"""Recover published physical context without silently accepting specimen matches."""
import collections
import csv
import html
import json
from pathlib import Path
import re
import shutil

BASE=Path(__file__).resolve().parent
INPUT=BASE/'western_sites_inputs'
OUT=BASE/'results/western_sites'


def read(path):
    with path.open() as f:return list(csv.DictReader(f))


def write(name, rows):
    assert rows,name
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def norm(s):return re.sub('[^a-z0-9]','',s.lower())


def area(s):
    n=norm(s)
    if 'promenade' in n:return 'promenade'
    for a in ['southreservoir','eastreservoir','middletown','lowertown','annexe','bailey','castle']:
        if a in n:return a
    return ''


def depth(s):
    if not s or not re.search(r'\d',s):return ()
    return tuple(float(x.replace(' ','')) for x in re.findall(r'[+-]?\s*\d+(?:\.\d+)?',s))


def grid(s):
    # Tank1 is an area qualifier in one catalogue and part of the locus in the source.
    return norm(re.sub(r'(?i)Tank\s*1\s*,?','',s)).rstrip('-')


def accession_matches(source, old):
    a,b=norm(source),norm(old)
    return bool(a and b and (a==b or (a.isdigit() and re.findall(r'\d+',old)==[a])))


def sources():
    observations={r['source_serial']:r for r in read(INPUT/'dholavira_observations.csv')}
    rows=[]
    for r in read(INPUT/'dholavira2015_register.csv'):
        o=observations[r['source_serial']]
        rows.append(dict(**r,**{k:o[k] for k in ['attachment_category','source_qualification','observation_summary']}))
    assert len(rows)==61 and len(observations)==61
    counts=collections.Counter(r['accession'] for r in rows)
    for r in rows:
        r['duplicate_source_accession']=counts[r['accession']]>1
        r['catalogue_identity_accepted']=False
    write('dholavira_source_contexts.csv',rows)
    extra=read(INPUT/'other_fastening_records.csv')
    for r in extra:
        r.update(source_status='Preliminary2016 presentation; public text recovered; named specimen figures not independently recovered',
                 catalogue_identity_accepted=False,independently_identified_contents='')
    write('bagasra_shikarpur_source_contexts.csv',extra)
    return rows,extra


def crosswalk(source,extra):
    metadata=read(INPUT/'existing_catalogue_subset.csv')
    tagged=[r for r in metadata if r['site']=='Dholavira' and r['type'].startswith('TAG')]
    objects=collections.defaultdict(list)
    for r in tagged:objects[r['id'].split('.')[0]].append(r)
    readings={r['face_id']:r for r in read(BASE.parent/'translation_catalogue/results/all_inscriptions.csv') if r['catalogue']=='Lipi'}
    candidates=[]
    for s in source:
        for oid,faces in objects.items():
            m=faces[0]
            exact=accession_matches(s['accession'],m['excavation-idno'])
            same_area=bool(area(s['source_area']) and area(s['source_area'])==area(m['area-section']))
            same_grid=bool(grid(s['source_grid']) and grid(s['source_grid'])==grid(m['block-house']))
            sd,md=depth(s['source_depth']),depth(m['depth'])
            same_depth=bool(sd and sd==md and s['depth_unit']=='cm' and 'cm' in m['depth'])
            if exact:level='exact_accession_candidate'
            elif same_area and same_grid and same_depth:level='area_grid_depth_candidate'
            elif same_area and same_depth:level='area_depth_only_candidate'
            elif same_area and same_grid and (not sd or not md):level='area_grid_depth_missing_candidate'
            elif same_depth and not area(m['area-section']):level='depth_only_area_missing_candidate'
            else:continue
            for face in faces:
                rr=readings.get(face['id'],{})
                candidates.append(dict(source_record=s['source_record'],source_accession=s['accession'],
                                       attachment_category=s['attachment_category'],source_qualification=s['source_qualification'],
                                       source_observation=s['observation_summary'],source_area=s['source_area'],
                                       source_grid=s['source_grid'],source_depth=s['source_depth'],source_period=s['source_period'],
                                       corpus_object_id=oid,corpus_face_id=face['id'],candidate_basis=level,
                                       exact_accession_match=exact,area_matches=same_area,grid_matches=same_grid,depth_matches=same_depth,
                                       corpus_area=face['area-section'],corpus_grid=face['block-house'],corpus_depth=face['depth'],
                                       corpus_recorded_accession=face['excavation-idno'],
                                       corpus_raw_sign_text=face['text'],
                                       existing_sign_sequence=rr.get('sign_sequence',face['text']),
                                       existing_proposed_reading=rr.get('existing_proposed_translation',''),
                                       current_proposed_meanings=rr.get('current_163_key_literal_meanings',''),
                                       accepted_as_same_object=False,independent_validation_eligible=False,
                                       reason='Context agreement is a candidate crosswalk; no accession or diagnostic specimen-photo identity confirmation.',
                                       source_url=s['source_url'],printed_pages=s['printed_pages']))
    # Keep a source/corpus collision explicit (e.g. two Castle objects at320cm).
    source_by_object=collections.defaultdict(set)
    for r in candidates:source_by_object[r['corpus_object_id']].add(r['source_record'])
    for r in candidates:r['source_candidates_for_this_corpus_object']=len(source_by_object[r['corpus_object_id']])
    write('candidate_context_crosswalk.csv',candidates)
    extra_joins=[]
    for s in extra:
        matches=[m for m in metadata if m['site']==s['site'] and accession_matches(s['accession'],m['excavation-idno'])]
        extra_joins.append(dict(source_record=s['source_record'],site=s['site'],accession=s['accession'],
                                attachment_category=s['attachment_category'],exact_accession_matches=len(matches),
                                current_catalogue_face_ids='; '.join(m['id'] for m in matches),
                                new_sign_transcription='',status='Physical observation added; no existing inscription joined' if not matches else 'Accession candidate needs specimen verification'))
    write('named_fastening_join_results.csv',extra_joins)
    dho_records=[]
    for oid,faces in objects.items():
        dho_records.append(dict(corpus_object_id=oid,face_ids='; '.join(m['id'] for m in faces),
                                old_type='; '.join(sorted({m['type'] for m in faces})),
                                old_area=faces[0]['area-section'],old_grid=faces[0]['block-house'],old_depth=faces[0]['depth'],
                                source_candidates='; '.join(sorted(source_by_object[oid])),
                                existing_sign_sequences=' | '.join(readings.get(m['id'],{}).get('sign_sequence',m['text']) for m in faces),
                                newly_accepted_context='',newly_transcribed_signs=''))
    write('all_existing_dholavira_tag_objects.csv',dho_records)
    return candidates,extra_joins,dho_records


def table(rows,columns):
    return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+html.escape(title)+'</th>' for k,title in columns)+'</tr></thead><tbody>'+''.join(
        '<tr>'+''.join('<td>'+html.escape(str(r.get(k,'')))+'</td>' for k,title in columns)+'</tr>' for r in rows)+'</tbody></table></div>'


def report(source,extra,candidates,extra_joins,old,summary):
    rows=[]
    for s in source:
        matches=[c for c in candidates if c['source_record']==s['source_record']]
        readings=' | '.join(c['corpus_face_id']+' ['+c['existing_sign_sequence']+']: '+c['existing_proposed_reading'] for c in matches)
        link='; '.join(sorted({c['candidate_basis'] for c in matches})) or 'No context candidate recovered'
        cells=[s['source_record'],s['accession'],s['attachment_category'].replace('_',' '),s['source_qualification'].replace('_',' '),
               s['source_area']+'; '+s['source_grid']+'; stratum '+s['source_stratum']+'; '+(s['source_depth']+' '+s['depth_unit'] if s['source_depth'] else 'depth unrecorded'),
               s['observation_summary'],link,readings or 'No existing reading joined',
               'Duplicate accession in source; entries52/61 kept separate' if s['duplicate_source_accession'] else '']
        rows.append('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in cells)+'</tr>')
    box=[r for r in candidates if r['source_accession']=='4608']
    textile=[r for r in candidates if r['source_accession']=='20502']
    highlights=table(box+textile,[('source_accession','Source accession'),('attachment_category','Physical observation'),
                                ('corpus_face_id','Candidate existing face'),('existing_sign_sequence','Existing signs'),
                                ('existing_proposed_reading','Existing proposed reading'),('candidate_basis','Why considered')])
    provenance=[dict(issue='Source accession43884 appears twice',handling='Keep entries52 and61 separate: different locations and periods. No invented correction.'),
                dict(issue='Source introduction and period counts disagree',handling='Register contains61 entries; introduction mentions60/61 and remaining59 after four uncertain. Preserve per-entry table periods; no chronological hypothesis scored.'),
                dict(issue='Conference functional study versus excavation register',handling='Both concern61 Dholavira specimens, but no demonstrated specimen-level population crosswalk; do not silently treat them as identical datasets.'),
                dict(issue='Bagasra/Shikarpur named figures',handling='Public conference text supplies the four labels. PDF/figure retrieval was blocked; no claimed visual reading of those specific signs.'),
                dict(issue='AncientPortsAntiques PDF filename',handling='Downloaded file is secondary commentary, not the original ASI report. Its proposed metalworking decipherments are not used.')]
    write('source_issues.csv',provenance)
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dholavira and western-site context expansion</title><style>
body{font:17px/1.55 system-ui,sans-serif;color:#253647;background:#faf8f2;max-width:1260px;margin:40px auto;padding:0 24px}h1{font-size:36px;line-height:1.2}h2{margin-top:40px}a{color:#0e647b}.callout{background:#e1eeea;border-left:5px solid #287d70;padding:20px}.scroll{overflow:auto}table{border-collapse:collapse;background:white;font-size:14px;width:100%}td,th{border:1px solid #d3dcd6;padding:10px;text-align:left;vertical-align:top}th{background:#e9eee7}.wide{min-width:1800px}input{font:inherit;padding:10px;margin:16px 0;width:100%;box-sizing:border-box}.note{color:#576773;font-size:14px}[hidden]{display:none!important}@media(max-width:600px){body{padding:0 16px}h1{font-size:28px}}</style>
<h1>Published physical context recovered for Dholavira, Bagasra and Shikarpur</h1><p>23 November2026 · local continuation; no GitHub push</p>
<div class="callout"><b>Added61 Dholavira register entries and four named fastening observations.</b> These are published archaeological context records. No new sign transcription has been added. No source/corpus specimen match is silently accepted as proven.</div>
<h2>What is actually new here?</h2><p>The existing dataset has69 Dholavira tag/sealing objects represented by76 encoded faces. This expansion recovers the individual reverse-side observations, accessions, excavation locations, strata, depths and qualified attachment interpretations from Bisht2015's full sealing register. The61 source entries contain60 distinct accession strings because43884 appears twice. They are not61 independently new inscriptions.</p>
<p>The2016 functional presentation supplies61 as an aggregate count and four explicitly named examples from other sites. It does not, in the recovered public text, provide the accession-level crosswalk needed to assign every functional category to a current inscription. The earlier excavation register supplies additional object-level evidence; the two61-item populations are not presumed identical.</p>
<h2>Useful candidate links: a box and a textile-backed fragment</h2>'''+highlights+'''
<p>The box candidate agrees on Bailey, XH34 and45cm; the textile candidate agrees on South Reservoir,48×45×4 and312cm. Their existing metadata omit the original accession. These are candidate crosswalks, not independently authenticated identities. The source's textile observation does not mean cloth was the commodity or that sign604 means cloth. It currently remains unread in the frozen key.</p>
<h2>Bagasra and Shikarpur: four context records, no joined inscriptions</h2>'''+table(extra_joins,[('site','Site'),('accession','Source specimen'),('attachment_category','Recorded fastening'),('exact_accession_matches','Exact catalogue matches'),('status','Addition')])+'''
<p>“Wall peg” does not by itself prove a door function. String/rope traces do not establish textile contents. Original specimen figures were not recovered for these four examples, so no signs are read from them here.</p>
<h2>How the crosswalk is handled</h2><p>Exact source accessions are searched first. Other candidates are retained with their actual agreement level: area+grid+depth, area+depth only, or lower resolution. Cases sharing only a depth or a general area do not receive definitive object labels. Multiple source candidates for one corpus object remain separate. Published classifications are not trained on proposed translations; object identity is a separate unresolved question.</p>
<h2>All61 Dholavira source entries</h2><p>Proposed readings below belong to candidate existing objects and remain conditional on their crosswalk. Missing interpretations and source ambiguities are retained. “Featureless” is not automatically called a token.</p><input id="search" aria-label="Search source and candidate records" placeholder="Search accession20502, textile, box, a sign, or a proposed meaning"><p id="count"></p><div class="scroll"><table class="wide" id="records"><thead><tr><th>Source record</th><th>Accession</th><th>Attachment observation</th><th>Qualification</th><th>Recorded location; grid; stratum; depth</th><th>Source observation (paraphrase)</th><th>Candidate basis</th><th>Existing proposed reading — conditional link</th><th>Source issue</th></tr></thead><tbody>'''+''.join(rows)+'''
</tbody></table></div><h2>Source issues preserved</h2>'''+table(provenance,[('issue','Issue'),('handling','Handling')])+'''
<h2>Files and sources</h2><p><a href="dholavira_source_contexts.csv">All61 source contexts</a> · <a href="candidate_context_crosswalk.csv">All candidate links and existing readings</a> · <a href="all_existing_dholavira_tag_objects.csv">All69 existing tag objects</a> · <a href="bagasra_shikarpur_source_contexts.csv">Four named fastening records</a> · <a href="named_fastening_join_results.csv">Their join results</a> · <a href="summary.json">Exact counts and test status</a> · <a href="protocol.md">Scope and matching rules</a></p><p>Primary register: <a href="https://www.scribd.com/document/262316120/Excavations-at-Dholavifra-1989-2005-RS-Bisht-2015">Bisht2015, §8.2.4, printed pp309–329</a>. Functional observations: <a href="https://www.researchgate.net/publication/323548480_Administrative_clay_sealing_technology_from_the_Indus_site_of_Dholavira_Gujarat_India_Preliminary_observations">Frenez, Prabhakar and Bisht2016, preliminary presentation</a>. The sources were already published; their explicit import and candidate crosswalk are the continuation. Colab units:0.</p>
<script>const rows=[...document.querySelectorAll('#records tbody tr')],search=document.querySelector('#search');function apply(){let n=0;for(const r of rows){r.hidden=!r.textContent.toLowerCase().includes(search.value.toLowerCase());n+=!r.hidden;}document.querySelector('#count').textContent=n+' of61 source entries shown';}search.addEventListener('input',apply);apply();</script></html>'''
    for old,new in {'Added61':'Added 61','November2026':'November 2026','dataset has69':'dataset has 69','by76':'by 76',
                    'The61':'The 61','contain60':'contain 60','because43884':'because 43884','not61':'not 61',
                    'The2016':'The 2016','supplies61':'supplies 61','two61':'two 61','XH34':'XH 34','and45cm':'and 45 cm',
                    'and312cm':'and 312 cm','sign604':'sign 604','All61':'All 61','All69':'All 69','accession20502':'accession 20502',
                    'Bisht2015':'Bisht 2015','Bisht2016':'Bisht 2016','pp309–329':'pp 309–329','units:0':'units: 0',
                    "n+' of61":"n+' of 61"}.items():page=page.replace(old,new)
    (OUT/'western_sites.html').write_text(page)
    shutil.copy2(BASE/'WESTERN_SITES_PLAN.md',OUT/'protocol.md')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source,extra=sources();candidates,extra_joins,old=crosswalk(source,extra)
    exact=[r for r in candidates if r['exact_accession_match']]
    strong=[r for r in candidates if r['candidate_basis']=='area_grid_depth_candidate']
    summary=dict(dholavira_source_entries=len(source),dholavira_distinct_accession_strings=len({r['accession'] for r in source}),
                 named_other_site_context_records=len(extra),existing_dholavira_tag_objects=len(old),existing_dholavira_encoded_faces=sum(len(r['face_ids'].split('; ')) for r in old),
                 candidate_source_face_links=len(candidates),source_entries_with_candidates=len({r['source_record'] for r in candidates}),
                 existing_objects_with_candidates=len({r['corpus_object_id'] for r in candidates}),
                 area_grid_depth_candidate_source_entries=len({r['source_record'] for r in strong}),
                 area_grid_depth_candidate_existing_objects=len({r['corpus_object_id'] for r in strong}),
                 exact_accession_candidate_links=len(exact),newly_verified_specimen_joins=0,new_sign_transcriptions=0,
                 named_other_site_exact_catalogue_matches=sum(r['exact_accession_matches'] for r in extra_joins),
                 semantic_validation_tests_run=0,independently_identified_contents=0,colab_units=0,
                 addition='Published source-context records and explicitly provisional links; no new transcribed inscriptions or confirmed object joins.')
    assert len(source)==61 and len(extra)==4 and len(old)==69
    assert all(not r['accepted_as_same_object'] for r in candidates)
    assert not any(r['newly_transcribed_signs'] for r in source+extra)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    report(source,extra,candidates,extra_joins,old,summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
