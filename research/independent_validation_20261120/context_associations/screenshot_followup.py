"""Recover complete proposed readings/findspots behind six screenshot contrasts.

Raw slash alternatives explain the screenshot's two inflated bangle counts.
This inventories evidence; it does not rerun previously completed association tests.
"""
import argparse,collections,csv,hashlib,html,json,re
from pathlib import Path
BASE=Path(__file__).resolve().parent
OUT=BASE/'results/screenshot_followup'
TARGETS={'790':('Bangle','BNGL'),'840':('Pair/pact','BNGL'),'838':('Bone (older proposal; later produce)','ROD'),
         '540':('Capacity measure','POT'),'440':('Earthen vessel / goblet/corner','POT'),'645':('Gold weight (proposal)','Gold')}
def rows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rs):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def eligible(r,t):return r['material']=='Gold' if t=='Gold' else r['object_type'].startswith('POT:') if t=='POT' else r['object_type']==t
def main(source):
    OUT.mkdir(exist_ok=True)
    raw={r['id']:r for r in rows(source)}
    lipi=[r for r in rows(BASE.parent/'translation_catalogue/results/all_inscriptions.csv') if r['catalogue']=='Lipi']
    matched=[];sites=[];summary=[];formulas=[]
    for sign,(label,typ) in TARGETS.items():
        pool=[r for r in lipi if eligible(r,typ)]
        sure=[r for r in pool if sign in r['sign_sequence'].split('-')]
        possible=[r for r in pool if sign in re.findall(r'(?<!\d)\d{3}(?!\d)',raw[r['face_id']]['text']) and r not in sure]
        for status,group in [('Unambiguous sign transcription (meaning remains proposed)',sure),('Alternative sign only; excluded from certain count',possible)]:
            for r in group:
                matched.append(dict(target_sign=sign,screenshot_label=label,match_status=status,
                    **{k:r[k] for k in ['face_id','object_identifier','reference','city','material','object_type','sign_sequence','existing_proposed_translation','current_163_key_literal_meanings','found_at','recorded_stratigraphy','excavation_number']},
                    raw_catalogue_transcription=raw[r['face_id']]['text']))
        summary.append(dict(sign=sign,label=label,target_faces=len(pool),target_object_ids=len({r['object_identifier'] for r in pool}),
            certain_sign_faces=len(sure),possible_additional_faces=len(possible),screenshot_count_including_alternatives=len(sure)+len(possible),
            certain_distinct_formulas=len({r['sign_sequence'] for r in sure}),
            certain_city_counts=dict(collections.Counter(r['city'] for r in sure))))
        for city in sorted({r['city'] for r in pool}):
            citypool=[r for r in pool if r['city']==city]
            hits=[r for r in sure if r['city']==city]
            sites.append(dict(sign=sign,label=label,site=city,target_faces=len(citypool),certain_hit_faces=len(hits),possible_additional_faces=sum(r['city']==city for r in possible),
                target_object_ids=len({r['object_identifier'] for r in citypool}),certain_hit_object_ids=len({r['object_identifier'] for r in hits}),
                certain_face_percent=100*len(hits)/len(citypool),references='; '.join(r['reference'] for r in hits)))
        for seq in sorted({r['sign_sequence'] for r in sure}):
            group=[r for r in sure if r['sign_sequence']==seq]
            formulas.append(dict(sign=sign,label=label,sign_sequence=seq,face_count=len(group),
                proposed_reading_versions=' | '.join(sorted({r['existing_proposed_translation'] for r in group})),
                references='; '.join(r['reference'] for r in group),cities='; '.join(sorted({r['city'] for r in group})),
                recorded_findspots=' | '.join(r['found_at'] for r in group)))
    assert [r['certain_sign_faces'] for r in summary]==[6,9,4,7,13,1]
    assert [r['screenshot_count_including_alternatives'] for r in summary]==[7,10,4,7,13,1]
    assert len(matched)==42 and len({r['face_id'] for r in matched})==41
    uncertain=[r for r in matched if r['match_status'].startswith('Alternative')]
    assert {r['reference'] for r in uncertain}=={'M-1644'} and len(uncertain)==2
    write('all_matching_readings_and_locations.csv',matched);write('within_site_frequencies.csv',sites);write('repeated_formulas.csv',formulas)
    payload=dict(summary=summary,match_rows=42,distinct_face_ids_including_uncertain=41,
        unambiguous_match_rows=40,ambiguous_specimen='M-1644: raw +840/790+, normalized ALT; one specimen, not two confirmations',
        statistical_tests_run=0,new_translations=0,metadata_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        limits='Descriptive face-level reconciliation of screenshot counts. 635 pottery faces are 629 object IDs; 42 rod faces are 41 object IDs. Meaning versions are retained; site counts are not a corrected test of geographical enrichment.')
    (OUT/'summary.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
    esc=html.escape
    page='''<!doctype html><meta charset="utf-8"><title>What do the matching inscriptions say?</title><style>body{font:16px/1.5 system-ui;color:#203644;margin:30px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #ccd7df;padding:9px;text-align:left;vertical-align:top}th{background:#eaf1f5}details{max-width:600px}a{color:#156292}.note{background:#fff1cb;padding:15px}.scroll{overflow-x:auto}</style><h1>What do the matching inscriptions say, and where were they found?</h1>
<p class="note"><b>The screenshot includes one ambiguous bangle under both 790 and 840.</b> M-1644 is recorded as “840 or 790,” normalized as ALT. Certain sign identifications give 6/50 and 9/50 faces, rather than 7/50 and 10/50. The 50 bangle faces represent 49 catalogue objects: M-1639 has two faces, neither carrying a target sign. All meanings remain proposals.</p>
<p>These are mostly short labels or repeated marks, not long translated sentences. The table preserves the existing English reading and exposes the current key's literal values separately. In particular, 838 has older bone/sesame proposals and a later produce reading; 440 has earlier received and later goblet/corner readings. A single reading version is not silently substituted into every sentence.</p>
<h2>Location frequencies, with the relevant local denominator</h2><p>Cells are certain sign-bearing catalogue objects / all catalogue objects of the relevant class at that site, merging multiple faces by object ID. The downloadable CSV also retains the face counts used in the screenshot. A zero does not establish historical absence. Uncertain M-1644 is excluded from positive counts here.</p><table><thead><tr><th>Sign / proposed meaning</th><th>Harappa</th><th>Mohenjo-daro</th><th>Other sites with a hit</th></tr></thead><tbody>'''
    for s in summary:
        selected=[r for r in sites if r['sign']==s['sign']]
        def at(city):
            rr=next((r for r in selected if r['site']==city),None)
            return str(rr['certain_hit_object_ids'])+'/'+str(rr['target_object_ids']) if rr else 'No target objects recorded'
        other='; '.join(r['site']+': '+str(r['certain_hit_object_ids'])+'/'+str(r['target_object_ids']) for r in selected if r['site'] not in {'Harappa','Mohenjo-daro'} and r['certain_hit_faces']) or 'None'
        page+='<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [s['sign']+' — '+s['label'],at('Harappa'),at('Mohenjo-daro'),other])+'</tr>'
    page+='''</tbody></table><h2>Patterns in the actual records</h2><ul><li><b>Goblet/corner 440:</b> all 12 Harappa pottery examples have the one-sign text 440. Seven are recorded at F Trench 43 and one at AB Trench 39N, all eight with phase C / period 3 fields; four have no detailed area. Among stamped pots specifically, 12/50 at Harappa carry 440 versus 0/22 at Mohenjo-daro. The thirteenth pottery example is a longer Mohenjo-daro graffito with an older “Received...” reading.</li><li><b>Capacity measure 540:</b> H-1740 and H-1742 both repeat 540-540 at F Trench 43, phase C / period 3. Four other pots have only 540; M-1379 has a longer “Month-Drum house” reading. This distribution crosses three cities.</li><li><b>Rod sign 838:</b> all four rods are in the DK/DKG areas of Mohenjo-daro. They repeat two formulas, each on two rods. Mohenjo-daro already supplies 32/42 rod faces in the catalogue; the four examples cannot alone establish a special city-level association.</li><li><b>Bangle and pair/pact:</b> certain examples occur at both Harappa and Mohenjo-daro. The local object frequencies are 2/7 versus 4/40 for 790, and 2/7 versus 7/40 for 840. More finds at Mohenjo-daro do not mean a higher local rate: it supplies 40 of the 49 bangle objects (41/50 faces).</li><li><b>Gold weight 645:</b> only M-2129 contributes; it is recorded at DK-E, Trench E1. There is no second positive gold specimen or multi-city comparison.</li></ul>
<p>Repeated formulas and common findspots may reflect production or administrative practices. They do not by themselves establish particular Dravidian words, a workshop's function, simultaneous deposition or stamping from one physical die. The local patterns above are descriptive; no new significance test was run.</p>
<p>Prior work is credited: <code>jobs/out/goods.md</code> already records six/nine bangles, four rod examples and twelve single-sign Harappa pot marks; <code>metrology_ledger.md</code> studies vessel marks; the continuation's earlier word/context screen covers many site and layer comparisons. This release supplies full translations/findspots and reconciles the screenshot, rather than claiming those associations were newly discovered.</p>
<h2>Every matching record</h2><p>42 sign–record rows, representing 40 certain matching faces plus one ambiguous bangle shown in both possible sign groups. Raw preservation and depth labels are retained; negative depths are not silently converted into a common chronology.</p><div class="scroll"><table><thead><tr><th>Sign / proposed label</th><th>Reference</th><th>Recorded signs</th><th>Existing proposed full reading</th><th>Found at</th><th>Recorded strata</th><th>Reading/source details</th></tr></thead><tbody>'''
    for r in matched:
        details='<details><summary>'+esc(r['match_status'])+'</summary><p>Raw: '+esc(r['raw_catalogue_transcription'])+'</p><p>Current key literal values: '+esc(r['current_163_key_literal_meanings'])+'</p><p>Object: '+esc(r['object_identifier']+'; '+r['object_type']+'; '+r['material'])+'</p></details>'
        page+='<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [r['target_sign']+' — '+r['screenshot_label'],r['reference'],r['sign_sequence'],r['existing_proposed_translation'],r['found_at'],r['recorded_stratigraphy']])+'<td>'+details+'</td></tr>'
    page+='</tbody></table></div><p><a href="all_matching_readings_and_locations.csv">All records CSV</a> · <a href="within_site_frequencies.csv">All site denominators CSV</a> · <a href="repeated_formulas.csv">Formula groups CSV</a> · <a href="summary.json">Counts and limits</a></p>'
    (OUT/'readings_and_locations.html').write_text(page)
    print(json.dumps(payload,ensure_ascii=False))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lipi-metadata',required=True);main(ap.parse_args().lipi_metadata)
