"""Join a specific published production assemblage to existing inscriptions.

Only accession-number matches are accepted. This adds archaeological source
annotations, not new inscriptions, translations, blind labels or p-values.
"""
import csv,html,json,re
from pathlib import Path
BASE=Path(__file__).resolve().parent;OUT=BASE/'results'
URL='https://www.harappa.com/sites/default/files/pdf/Kenoyer%202005%20Faience%20Workshop.pdf'
SOURCE='Kenoyer 2005, Steatite and Faience Manufacturing at Harappa'
# Publication Figure 3, followed by Figure 4. Blank controls and the figurine
# remain in the source inventory, without inventing corpus inscriptions.
ITEMS=[
 ('3.1','H2001-5084','2913-07','partly inscribed tablet','unfired steatite','partial_tablet_batch'),
 ('3.2','H2001-5087','2934-01','partly inscribed broken tablet','fired steatite','partial_tablet_batch'),
 ('3.3','H2001-5069','2913-02','incised broken tablet; proposed mould','unfired steatite','mould_candidate'),
 ('3.4','H2001-5068','2913-01','partly inscribed broken tablet','unfired steatite','partial_tablet_batch'),
 ('3.5','H2001-5074','2913-04','partly inscribed broken tablet','unfired steatite','partial_tablet_batch'),
 ('3.6','H2001-5187','2934-270','uninscribed broken tablet blank','unfired steatite','blank_control'),
 ('3.7','H2001-5135','2913-210','uninscribed broken tablet blank','unfired steatite','blank_control'),
 ('3.8','H2001-5064','2373-01','moulded tablet','faience','workshop_area'),
 ('3.9','H2001-5065','2373-02','moulded broken tablet','faience','workshop_area'),
 ('3.10','H2001-5077','2913-05','moulded broken tablet','bicolour faience','workshop_area'),
 ('3.11','H2001-5083','2913-06','moulded tablet','faience','workshop_area'),
 ('3.12','H2001-5089','2913-08','moulded tablet','faience','workshop_area'),
 ('3.13','H2001-5090','2913-09','moulded tablet','bicolour faience','workshop_area'),
 ('3.14','H2000-5042','2357-13','moulded tablet','faience','workshop_area'),
 ('3.15','H2000-5041','2360-01','moulded tablet; proposed mould product','faience','mould_product_candidate'),
 ('4.1','H2001-5082','2920-02','moulded tablet','bicolour faience','other_area_find'),
 ('4.2','H2000-4385','2087-05','moulded broken tablet','bicolour faience','other_area_find'),
 ('4.3','H2000-4483','2342-01','moulded broken tablet; surface find downslope','faience','surface_downslope'),
 ('4.4','H2000-4440','2121-90','figurine leg; adjacent erosion gully','bicolour faience','figurine_control'),
]
def write(name,rs):
 with (OUT/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def main():
 rs=list(csv.DictReader((BASE.parent/'translation_catalogue/results/all_inscriptions.csv').open()))
 lp=[r for r in rs if r['catalogue']=='Lipi'];inventory=[];joined=[]
 for fig,acc,lot,status,material,group in ITEMS:
  hits=[r for r in lp if re.search(re.escape(acc)+r'(?!\d)',r['excavation_number'])]
  objects={r['object_identifier'] for r in hits};assert len(objects)<=1,(acc,objects)
  e=dict(source=SOURCE,source_url=URL+'#page='+('9' if fig.startswith('3.') else '10'),source_figure=fig,accession=acc,source_lot=lot,
   source_artefact_status=status,source_material=material,source_group=group,
   archaeological_context='Harappa, Mound E, Trench 54: tablet/bead production area',
   context_limit='Workshop-area association; same depositional event and in-situ use not assumed',
   matching_objects=len(objects),matching_faces=len(hits),references='; '.join(sorted({r['reference'] for r in hits})),
   join_status='Exact accession match' if hits else 'No matching inscription row; no object added')
  inventory.append(e)
  for r in hits:
   joined.append(dict(**e,object_identifier=r['object_identifier'],face_id=r['face_id'],reference=r['reference'],
    signs=r['sign_sequence'],existing_proposed_translation=r['existing_proposed_translation'],
    intact_as_recorded=r['intact_as_recorded'],preservation=r['preservation'],found_at=r['found_at'],recorded_stratigraphy=r['recorded_stratigraphy']))
 write('archaeology_source_inventory.csv',inventory);write('archaeology_linked_inscriptions.csv',joined)
 batch=[r for r in joined if r['source_group']=='partial_tablet_batch'];assert len(batch)==4
 assert {r['reference'] for r in batch}=={'H-2076','H-2077','H-2078','H-2079'}
 pair=[r for r in joined if r['source_group'] in {'mould_candidate','mould_product_candidate'}]
 assert any(a['signs']==b['signs']=='700-033' for a in pair for b in pair if a['source_group']!=b['source_group'])
 summary=dict(source_items=len(inventory),linked_existing_objects=len({r['object_identifier'] for r in joined}),linked_faces=len(joined),
  unmatched_items=[r['accession'] for r in inventory if not r['matching_objects']],
  source_partial_batch_objects=len(batch),source_partial_batch_observed_forms=len({r['signs'] for r in batch}),
  partial_batch_already_flagged_not_intact=sum(r['intact_as_recorded']=='False' for r in batch),
  proposed_mould_pair={'mould':'H-2191','tablet':'H-1912','shared_sequence':'700-033','existing_proposed_reading':'3 measures'},
  new_translations=0,blind_semantic_assignments=0,statistical_tests=0,
  novelty_scope='Specific accession-linked production assemblage and reported production relations. General unfinished seals, material correlations and workshop zones were already studied.')
 assert summary['linked_existing_objects']==16 and len(inventory)==19 and len(joined)==25
 assert summary['partial_batch_already_flagged_not_intact']==2
 (OUT/'archaeology_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
 (OUT/'CLUE_FOLLOWUP.md').write_text((BASE/'CLUE_FOLLOWUP.md').read_text().replace('(results/','('))
 present(joined,summary)
 print(json.dumps(summary,ensure_ascii=False))
def present(joined,s):
 esc=html.escape
 body='''<!doctype html><meta charset="utf-8"><title>Additional archaeological evidence</title>
<style>body{font:17px/1.5 system-ui;margin:30px auto;max-width:1450px;padding:0 25px;color:#19313c}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;border:1px solid #ccd8dc;text-align:left;vertical-align:top}th{background:#eaf1f4}a{color:#175e91}.note{background:#f0f5f6;padding:16px}code{white-space:normal}</style>
<h1>Additional archaeological evidence: a documented production assemblage</h1>
<p>16 existing catalogue objects have now been linked by accession number to Kenoyer's published Trench 54 tablet-production assemblage. The source inventory also preserves two uninscribed blanks and a figurine, without adding them as inscriptions.</p>
<p class="note">These are additional source annotations. The objects were already in the corpus. The source was checked after reading the proposed translations; this is retrospective evidence, not a blind or withheld semantic validation.</p>
<h2>Two concrete relationships</h2>
<p><b>Four tablets belong to one reported partially inscribed group.</b> H-2076 and H-2077 have 240–760–740, H-2079 has 760–740, and H-2078 has 740–000. The source groups all four under the same intended inscription. Two are already marked non-intact in our catalogue. This adds a production relationship; it does not establish an error in intact-only tests or authorize filling missing signs.</p>
<p><b>A proposed mould/product pair shares 700–033.</b> The source's Figure 3.3 joins to H-2191; Figure 3.15 joins to H-1912. Both corresponding faces currently read “3 measures”. This is a physical relationship reported by the archaeologist, consistent with shared text; it does not identify the measure, its sound, or a litre conversion.</p>
<p><b>Interpretation:</b> a cluster near a workshop can represent manufacture or discarded stock. It cannot automatically be counted as several independent customers, transactions or offices. The labels “tax”, “grain” and “house” below remain proposals.</p>
<p><a href="https://www.harappa.com/sites/default/files/pdf/Kenoyer%202005%20Faience%20Workshop.pdf#page=3">Primary study: discussion and figures</a> · <a href="archaeology_source_inventory.csv">Every source item</a> · <a href="archaeology_linked_inscriptions.csv">Every joined face</a> · <a href="CLUE_FOLLOWUP.md">Which clues had already been considered?</a></p>
<table><thead><tr><th>Object / face</th><th>Existing proposed reading</th><th>Signs</th><th>New source annotation</th><th>Recorded findspot / strata</th><th>Source</th></tr></thead><tbody>'''
 for r in joined:
  cells=[r['reference']+' / '+r['face_id'],r['existing_proposed_translation'],r['signs'],r['source_artefact_status']+'; '+r['accession']+'; lot '+r['source_lot'],r['found_at']+'; '+r['recorded_stratigraphy']]
  body+='<tr>'+''.join('<td>'+esc(x)+'</td>' for x in cells)+'<td><a href="'+esc(r['source_url'],quote=True)+'">Figure '+esc(r['source_figure'])+'</a></td></tr>'
 body+='</tbody></table><p>All joins use excavation accession numbers. Recorded metadata and proposed translations remain unchanged. Surface finds and unspecified depositional security are retained explicitly. No new p-values or language identification are claimed.</p>'
 (OUT/'archaeology.html').write_text(body)
if __name__=='__main__':main()
