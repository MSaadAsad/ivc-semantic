"""Show the other inscriptions on bangles/pots at the discussed findspots.

An inventory, not a new significance test. Missing context and unknown signs
are retained; absence of a recorded rice sign is not an absence of rice contents.
"""
import collections,csv,hashlib,html,json,re
from pathlib import Path
BASE=Path(__file__).resolve().parent;OUT=BASE/'results/same_context'
GROUPS=[
 ('Bangles: Mohenjo-daro MN area','bangle','Mohenjo-daro','MN-',''),
 ('Bangles: Mohenjo-daro HR area','bangle','Mohenjo-daro','HR-',''),
 ('Bangles: Mohenjo-daro DK area','bangle','Mohenjo-daro','DK-',''),
 ('Bangles: Mohenjo-daro DKG (S)','bangle','Mohenjo-daro','DKG. (S)',''),
 ('Bangles: Mohenjo-daro SD area','bangle','Mohenjo-daro','SD-',''),
 ('Bangles: Harappa E area','bangle','Harappa','E-',''),
 ('All pots: Harappa F Trench 43','pot','Harappa','FTrench 43',''),
 ('Stamped pots only: Harappa F Trench 43','pot','Harappa','FTrench 43','POT:T:s'),
 ('Pots: Mohenjo-daro MN area','pot','Mohenjo-daro','MN-',''),
 ('Pots: Mohenjo-daro SD area','pot','Mohenjo-daro','SD-',''),
 ('Pots: Harappa E Trench 36','pot','Harappa','ETrench 36',''),
 ('Pots: Harappa AB Trench 39N','pot','Harappa','ABTrench 39N','')]
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rs):
 with (OUT/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def main():
 OUT.mkdir(exist_ok=True)
 source=BASE.parent/'translation_catalogue/results/all_inscriptions.csv'
 faces=[r for r in rows(source) if r['catalogue']=='Lipi' and (r['object_type']=='BNGL' or r['object_type'].startswith('POT:'))]
 byobj=collections.defaultdict(list)
 for r in faces:byobj[r['object_identifier']].append(r)
 objects=[]
 for oid,group in byobj.items():
  first=group[0];tok=set(s for r in group for s in r['sign_sequence'].split('-'))
  def combine(k):return ' | '.join((r['face_id']+': ' if len(group)>1 else '')+r[k] for r in group)
  objects.append(dict(object_identifier=oid,face_ids='; '.join(r['face_id'] for r in group),reference=first['reference'],
   kind='bangle' if first['object_type']=='BNGL' else 'pot',city=first['city'],area_as_recorded=first['excavation_area'],
   object_type=first['object_type'],material=first['material'],sign_sequence=combine('sign_sequence'),
   existing_proposed_translation=combine('existing_proposed_translation'),current_key_literal_values=combine('current_163_key_literal_meanings'),
   found_at=first['found_at'],recorded_stratigraphy=first['recorded_stratigraphy'],
   proposed_bangle_sign_790='790' in tok,proposed_pair_sign_840='840' in tok,
   proposed_rice_sign_215_or_216=bool(tok&{'215','216'}),proposed_measure_sign_540='540' in tok,
   proposed_goblet_sign_440='440' in tok,
   contains_unassigned_signs=any(r['unassigned_signs'] for r in group),
   older_english_mentions_rice=any(re.search(r'\brice\b',r['existing_proposed_translation'],re.I) for r in group)))
 assert len(faces)==685 and len(objects)==678
 assert collections.Counter(r['kind'] for r in objects)=={'bangle':49,'pot':629}
 write('all_bangle_and_pot_objects.csv',objects)
 members=[];groups=[];profiles=[];sets=[]
 for label,kind,city,area,typ in GROUPS:
  selected=[r for r in objects if r['kind']==kind and r['city']==city and r['area_as_recorded']==area and (not typ or r['object_type']==typ)]
  groups.append(dict(group=label,objects=len(selected),with_bangle_word=sum(r['proposed_bangle_sign_790'] for r in selected),
   with_pair_word=sum(r['proposed_pair_sign_840'] for r in selected),with_rice_sign=sum(r['proposed_rice_sign_215_or_216'] for r in selected),
   with_measure_540=sum(r['proposed_measure_sign_540'] for r in selected),with_goblet_440=sum(r['proposed_goblet_sign_440'] for r in selected),
   scope='Same recorded excavation area/trench; not demonstrated same room, deposit, workshop or date',
   subtype_filter=typ or 'All recorded subtypes'))
  for r in selected:members.append(dict(group=label,**r))
  for (seq,reading),n in collections.Counter((r['sign_sequence'],r['existing_proposed_translation']) for r in selected).items():
   profiles.append(dict(group=label,sign_sequence=seq,existing_proposed_translation=reading,objects=n))
  sets.append((label,selected))
 write('all_selected_context_members.csv',members);write('context_summary.csv',groups);write('context_reading_profiles.csv',profiles)
 summary=dict(total_bangle_and_pot_faces=len(faces),catalogue_object_ids=len(objects),bangles=49,pots=629,
  distinct_objects_in_selected_contexts=len({r['object_identifier'] for r in members}),context_memberships=len(members),
  rice_sign_pots=[r['reference'] for r in objects if r['kind']=='pot' and r['proposed_rice_sign_215_or_216']],
  bangle_with_older_rice_measure_reading=[r['reference'] for r in objects if r['kind']=='bangle' and r['older_english_mentions_rice']],
  groups=groups,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
  statistical_tests_run=0,new_translations=0,
  interpretation_limits=['Proposed readings retained verbatim; unknown signs remain visible.',
   'Rice sign presence, older English rice wording and measured rice contents are different variables.',
   'Selected context groups overlap: the 22 stamped F Trench 43 pots are a subset of the 38 total pots.',
   'Same recorded area does not establish contemporaneity or physical proximity within the area.',
   'Absence of a proposed sign does not establish a concept was absent, particularly in incomplete or unassigned texts.'])
 assert summary['rice_sign_pots']==['M-1599']
 assert summary['bangle_with_older_rice_measure_reading']==['H-2574']
 bylabel={r['group']:r for r in groups}
 assert bylabel['Bangles: Mohenjo-daro MN area']['objects']==8
 assert bylabel['Stamped pots only: Harappa F Trench 43']['objects']==22
 assert bylabel['All pots: Harappa F Trench 43']['objects']==38
 assert bylabel['Pots: Mohenjo-daro SD area']['objects']==1
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
 esc=html.escape
 page='''<!doctype html><meta charset="utf-8"><title>Other readings on the same objects at the same locations</title><style>body{font:16px/1.5 system-ui;color:#203644;max-width:1450px;margin:30px auto;padding:0 20px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #ccd7df;padding:9px;text-align:left;vertical-align:top}th{background:#eaf1f5}.note{background:#fff1cb;padding:15px}details{margin:20px 0}summary{font-weight:bold;cursor:pointer}a{color:#156292}.scroll{overflow-x:auto}</style>
<h1>What do the other bangles and pots at those locations say?</h1><p class="note"><b>The local vocabulary is mixed.</b> Bangles at the same recorded area carry proposed tax, measure, thread and sale words as well as bangle/pair marks. Pots in the same trench carry numerals, star marks, vessel marks and a longer house formula. This does not identify contents or establish the proposed translations.</p>
<h2>Three distinctions that matter</h2><ul><li><b>Rice wording is not a rice sign.</b> H-1740/H-1742 at F Trench 43 read 540-540, earlier translated “Two rice measures.” Their text has the measure sign twice; neither has proposed rice sign 215/216. H-2574 is a bangle with an older “[lost sign], rice measure” reading.</li><li><b>The actual proposed rice-sign pot is M-1599:</b> 480-175-215, at Mohenjo-daro SD (excavation SD 2976). Its older sentence leaves 215 unresolved. It is the only pot assigned exactly SD- in this catalogue, so there is no same-area pot comparison group. Other Mohenjo-daro pots are city-level comparisons.</li><li><b>Same area is not the same deposit.</b> MN and DK are broad areas. F Trench 43 is a more specific recorded trench, but common phase C / period 3 still does not identify a single deposit or workshop. No new statistical test is claimed.</li></ul>
<h2>Useful local comparisons</h2><p><b>Mohenjo-daro MN bangles:</b> eight objects: two containing 790, one containing 840, and five with neither recorded sign. The latter include M-1632 “Grain-Tax/Cut Star Goblet/Corner,” M-1633 “Sail, kalam, portion,” M-1635 “[631], thread,” M-1638 “Sale, [250],” and M-1637 “Sale/Price 1.”</p>
<p><b>Harappa F Trench 43 stamped pots:</b> 22 objects, all recording phase C / period 3. Two have 540-540; seven have standalone 440; four have 416 “Port/Double-Branch”; four have 013 “3”; two have 033-220 “Three-Star”; one has 220 “Star”; one reads “two shares: Four”; and one reads “two shares: of the Horn-Assembly-Elder house.” None contains proposed rice sign 215/216. The whole trench inventory has 38 pots, including 16 graffiti-bearing records, so 22 is the subtype comparison rather than the whole trench count.</p>
<p><b>Mohenjo-daro MN pots:</b> M-2003 has an older “Ship-Quarter-Millet house” reading (current sign 831 proposal: paddy/ear of paddy), M-2004 reads “Five kalam; [lost sign],” and M-1436 reads “Horn.” Only M-2003 and M-2004 are the same stamped-pot subtype; all three share the broad recorded area.</p>
<p>These contrasts allow us to examine hypotheses about names, affiliations, measures or administrative marks. They do not establish those functions: interpreting every sign as a label for the carrier or its contents would require additional assumptions. The recorded mixture also does not by itself falsify a proposed word, since that word might occur in a name or another construction.</p>
<p><a href="all_bangle_and_pot_objects.csv">All 678 bangle/pot object records</a> · <a href="all_selected_context_members.csv">Every record in the selected contexts</a> · <a href="context_reading_profiles.csv">Repeated readings and counts</a> · <a href="context_summary.csv">Group counts</a> · <a href="summary.json">Scope and limits</a></p>
<h2>Complete local context groups</h2><p>Groups overlap: the stamped F Trench 43 group is a subset of its all-pot group. Both are shown so object form is not silently mixed. Existing sentences and current literal key values are separate.</p>'''
 for label,selected in sets:
  page+='<details><summary>'+esc(label)+' — '+str(len(selected))+' objects</summary><div class="scroll"><table><thead><tr><th>Reference / type</th><th>Recorded signs</th><th>Existing proposed reading</th><th>Actual recorded location</th><th>Strata</th><th>Current literal values</th></tr></thead><tbody>'
  for r in selected:
   page+='<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [r['reference']+' / '+r['object_type'],r['sign_sequence'],r['existing_proposed_translation'],r['found_at'],r['recorded_stratigraphy']])+'<td><details><summary>Show values</summary>'+esc(r['current_key_literal_values'])+'</details></td></tr>'
  page+='</tbody></table></div></details>'
 (OUT/'other_readings_at_same_locations.html').write_text(page)
 print(json.dumps({k:v for k,v in summary.items() if k!='groups'},ensure_ascii=False))
if __name__=='__main__':main()
