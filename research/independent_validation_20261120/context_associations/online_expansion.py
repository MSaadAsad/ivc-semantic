"""Join additional published animal/layout observations to unchanged existing texts."""
import collections
import csv
import html
import json
from pathlib import Path
import re
import shutil

from online_expansion_extract import canonical

BASE=Path(__file__).resolve().parent
INPUT=BASE/'online_expansion_inputs'
OUT=BASE/'results/online_expansion'
ARTICLE='https://link.springer.com/article/10.1007/s43539-023-00102-3'
ESM='https://static-content.springer.com/esm/art%3A10.1007%2Fs43539-023-00102-3/MediaObjects/'


def read(path):
    with path.open() as f:return list(csv.DictReader(f))


def write(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def join(source,metadata,readings):
    matched=metadata.get(canonical(source),[])
    objects=sorted({r['id'].split('.')[0] for r in matched})
    status='Exact CISI object reference; numerical faces not independently aligned to source A–F' if len(objects)==1 else 'Unresolved multiple corpus objects' if objects else 'No exact CISI match recovered'
    return dict(existing_object_ids='; '.join(objects),existing_face_ids='; '.join(r['id'] for r in matched),
                existing_sign_sequences=' | '.join(r['id']+': '+readings[r['id']]['sign_sequence'] for r in matched),
                existing_proposed_readings=' | '.join(r['id']+': '+readings[r['id']]['existing_proposed_translation'] for r in matched),
                current_key_literal_meanings=' | '.join(r['id']+': '+readings[r['id']]['current_163_key_literal_meanings'] for r in matched),
                old_symbol_labels=' | '.join(sorted({r['symbol'] for r in matched})),
                old_field_object_labels=' | '.join(sorted({r['cult'] for r in matched})),
                found_at=' | '.join(sorted({readings[r['id']]['found_at'] for r in matched})),
                join_status=status,face_alignment_verified=False,independent_validation_eligible=False)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=read(INPUT/'animal2024_rows.csv')
    readings={r['face_id']:r for r in read(BASE.parent/'translation_catalogue/results/all_inscriptions.csv') if r['catalogue']=='Lipi'}
    metadata=collections.defaultdict(list)
    for r in read(INPUT/'existing_animal_metadata.csv'):metadata[canonical(r['cisi'])].append(r)
    named=[dict(**r,**join(r['raw_cisi'],metadata,readings)) for r in rows if r['source_named_row']=='True']
    frontal=[dict(**r,**join(r['cisi'],metadata,readings)) for r in read(INPUT/'frontal33_review.csv')]
    for r in frontal:r['source_photo']=f'images/frontal-{int(r["source_row"]):02}.jpg'
    write('animal2024_named_records.csv',named)
    write('animal2024_all_source_rows.csv',rows)
    write('frontal33_existing_readings.csv',frontal)
    unmatched=[r for r in frontal if not r['existing_object_ids']]
    write('unmatched_illustrated_candidates.csv',unmatched)
    shutil.copy2(INPUT/'animal2024_source_notes.csv',OUT/'animal2024_source_notes.csv')
    shutil.copy2(INPUT/'image_sources.csv',OUT/'image_sources.csv')
    versions=json.loads((INPUT/'animal_version_summary.json').read_text())
    shutil.copy2(INPUT/'animal_version_summary.json',OUT/'animal_version_summary.json')
    shutil.copy2(INPUT/'animal_version_changes.csv',OUT/'animal_version_changes.csv')
    shutil.copytree(INPUT/'images',OUT/'images',dirs_exist_ok=True)
    linked={o for r in named for o in r['existing_object_ids'].split('; ') if o}
    linked_faces={o for r in named for o in r['existing_face_ids'].split('; ') if o}
    ids=[r['source_canonical_id'] for r in named if r['source_canonical_id']]
    repeats={k:v for k,v in collections.Counter(ids).items() if v>1}
    issues=[dict(kind='Repeated source reference',source=k,handling=f'{v} named rows retained; never count them as {v} independent objects') for k,v in repeats.items()]
    issues.extend(dict(kind='Unparsed source identifier',source=r['raw_cisi'],handling='Retain source spelling; no inferred catalogue identity') for r in named if not r['source_canonical_id'])
    issues.append(dict(kind='Publication/source denominator',source='Paper reports 2023 animal-bearing objects; extracted sheet has 2022 named rows plus continuation and legend rows',
                       handling='Report extracted row/reference counts separately; do not force agreement or claim every row is a new specimen.'))
    issues.append(dict(kind='ESM1 versus ESM13',source='The separate 33-object illustrated list is not identical to workbook F3 rows; some signs and animal labels differ',
                       handling='Keep both source versions and explicit disagreements; do not merge into a single authoritative glyph transcription.'))
    write('source_issues.csv',issues)
    source_screen=[
        dict(source='Bhaskar 2022 animal catalogue',url='https://doi.org/10.1007/s43539-022-00052-2',result='Already archived in upstream evidence/tmp/m1206_bhaskar; not claimed as a new source',addition='None credited as a discovery here'),
        dict(source='Bhaskar 2024 ESM1 and ESM13',url=ARTICLE,result='Both public supplements downloaded; no matching 2024 title/file/DOI use located in materialized scripts/reports and filename inventory',addition='Updated animal/face/layout observations plus separately illustrated 33-object register'),
        dict(source='Rakhigarhi Mound 3 season 2021–22 report, published 2026',url='https://bssspublications.com/PublishedPaper/Publish_749.pdf',result='Report p17 explicitly says the seal has no script or animal depiction',addition='Uninscribed control/lead only; zero inscriptions added'),
        dict(source='Official ASI Binjor summary',url='https://sansad.in/getFile/loksabhaquestions/annex/176/AU183.pdf?source=pqals',result='Downloaded; official aggregate eleven seals for 2015–16/2016–17; no individual register or sign strings',addition='Aggregate source record only; not eleven transcriptions'),
        dict(source='Binjor unicorn seal photograph',url='https://faculty.fordham.edu/vinod/kalyanaraman2021.pdf',result='Embedded photograph recovered from secondary reproduction p17; original Frontline route unavailable',addition='One unjoined image-backed source record; numeric coding and accession unresolved'),
        dict(source='Manjul 2021 Binjor chapter / official report download / TN proceedings',url='https://www.academia.edu/104754509/Excavations_at_4MSR_Binjor_District_Sri_Ganganagar_Rajasthan_A_Harappan_Industrial_Settlement',result='Author chapter identified but preview unavailable; official ASI report and TN proceedings timed out',addition='Primary individual-register recovery still pending; no invented entries'),
        dict(source='NMMA Rakhigarhi seal records',url='https://nmma.nic.in/nmma/exploreObject.do?object=32&pager.offset=2000',result='Search index exposes accession-like NMMA references; direct page timed out',addition='Unrecovered lead; no joined image or inscription'),
        dict(source='Shinde and Willis 2014 nine copper plates',url='https://doi.org/10.5334/aa.12317',result='Publication identified; private-collection provenance and authenticity criticism in Fuls 2022 make it unsuitable as clean fresh validation',addition='Separate provenance-disputed lead; not pooled into excavated copper tests'),
        dict(source='Binjor seven food balls, Agnihotri et al. 2021',url='https://doi.org/10.1016/j.jasrep.2021.102917',result='Primary abstract recovered; cereals/legumes analysed, but no accession-level inscription join recovered',addition='Potential contents/context lead; no coded inscription outcome assigned')]
    write('source_screen.csv',source_screen)
    binjor=[dict(source_record='BINJOR-photo-2015-unicorn',site='Binjor / 4MSR',accession='',animal='Unicorn',material='Reported steatite',
                 source_reported_characters=5,sign_sequence='',translation='',
                 observation='Published photo has an animal and a top inscription; no numeric sign coding asserted in this release.',
                 source_image='images/binjor-unicorn-photo.jpeg',source_url='https://faculty.fordham.edu/vinod/kalyanaraman2021.pdf',source_page=17,
                 source_quality='Secondary reproduction of credited excavation-reporting photograph; original route unavailable',
                 existing_named_site_rows=0,existing_object_join='',new_numeric_transcription=False,
                 limitation='No excavation accession or exact trench recovered for this object; do not identify it with a nearby hearth or food balls.')]
    write('binjor_source_records.csv',binjor)
    summary=dict(worksheet_data_rows=len(rows),named_source_rows=len(named),continuation_rows=len(rows)-len(named),
                 parseable_distinct_source_references=len(set(ids)),unparsed_named_identifier_rows=sum(not r['source_canonical_id'] for r in named),
                 repeated_parseable_reference_groups=len(repeats),source_named_rows_with_corpus_links=sum(bool(r['existing_object_ids']) for r in named),
                 linked_existing_objects=len(linked),linked_existing_faces=len(linked_faces),
                 illustrated_frontal_register_rows=len(frontal),frontal_rows_with_existing_links=sum(bool(r['existing_object_ids']) for r in frontal),
                 illustrated_rows_without_exact_corpus_id_match=len(unmatched),
                 frontal_rows_with_source_disagreements=sum(bool(r['source_disagreement']) for r in frontal),
                 workbook_named_rows_with_F3_label=sum('F3' in r['right_behavior']+' '+r['left_behavior'] for r in named),
                 additional_unjoined_binjor_photos=1,new_numeric_transcriptions=0,new_confirmed_corpus_artifacts=0,
                 new_published_sign_coding_rows_vs_archived2022=versions['new_f3_coding_named_rows'],
                 shared_reference_groups_with_label_revisions_vs2022=versions['changed_reference_labels'],
                 baseline_byte_identical_to_archived_workbook=versions['baseline_byte_identical_to_archived_workbook'],
                 semantic_validation_tests_run=0,frozen923_new_family_trials=0,colab_units=0)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    report(named,frontal,source_screen,summary)
    print(json.dumps(summary,indent=2))


def report(named,frontal,sources,summary):
    h=html.escape
    cards=[]
    explanations={
        'M-410':('A fish in a gharial’s mouth','The existing single-sign proposal is “Star.” The new source makes the image/text relationship explicit: the fish is in the gharial’s mouth. This can motivate a literal-image versus rebus use comparison, but it does not establish either sound or meaning.'),
        'M-272':('A turning goat looking at two strokes','The animal turns back toward the two-stroke sign. The source separates that mark from the wheel above the animal. Keep physical layout separate from the stored linear sequence; the animal does not itself establish a numeric or phonetic reading.'),
        'M-1719':('A box-shaped field element outside the stored text','The source labels the rectangle under the unicorn’s nose as Mahadevan 242. The old catalogue already records S621 under its field-object code, while the running inscription is a separate sequence. The addition is independent layout annotation, not a newly discovered sign occurrence or a translation of the box.')}
    for r in frontal:
        if r['cisi'] not in explanations:continue
        title,explanation=explanations[r['cisi']]
        cards.append('<article><h3>'+h(r['cisi']+': '+title)+'</h3><img class="specimen" src="'+h(r['source_photo'])+'" alt="Published illustration '+h(r['cisi'])+'"><p><b>Existing proposal:</b> '+h(r['existing_proposed_readings'] or 'No joined reading')+'</p><p>'+h(explanation)+'</p><small>Source animal: '+h(r['animal'])+'; front-facing sign(s): Mahadevan '+h(r['frontal_mahadevan'])+'.</small></article>')
    frows=''.join('<tr>'+''.join('<td>'+h(r[k])+'</td>' for k in ['cisi','animal','orientation','frontal_mahadevan','dorsal_mahadevan','existing_sign_sequences','existing_proposed_readings','found_at','qualification','source_disagreement'])+'</tr>' for r in frontal)
    nrows=''.join('<tr data-linked="'+str(bool(r['existing_object_ids'])).lower()+'" data-front="'+str('F3' in r['right_behavior']+' '+r['left_behavior']).lower()+'">'+''.join('<td>'+h(str(r[k]))+'</td>' for k in ['source_row','raw_cisi','right_behavior','left_behavior','source_f3_signs_mahadevan','seal_face_A','impression_face_A','existing_face_ids','existing_proposed_readings','found_at','join_status'])+'</tr>' for r in named)
    screen=''.join('<tr>'+''.join('<td>'+h(r[k])+'</td>' for k in ['source','result','addition'])+'</tr>' for r in sources)
    gallery=''.join('<article><h3>'+h(r['cisi']+' — '+r['animal'])+'</h3><img class="specimen" src="'+h(r['source_photo'])+'" alt="Published source illustration '+h(r['cisi'])+'"><p>Source front-facing coding: Mahadevan '+h(r['frontal_mahadevan'])+'. Above/behind coding: '+h(r['dorsal_mahadevan'] or 'none listed')+'.</p><p>'+h(r['qualification'])+'</p><small>'+h(r['source_disagreement'])+'</small></article>' for r in frontal if not r['existing_object_ids'])
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Additional online animal and inscription data</title><style>
*{box-sizing:border-box}body{font:17px/1.55 system-ui,sans-serif;background:#faf8f2;color:#253647;max-width:1280px;margin:36px auto;padding:0 24px}h1{font-size:36px;line-height:1.15}h2{margin-top:38px}h3{font-size:21px}a{color:#0e647b}.notice{padding:18px;border-left:5px solid #287d70;background:#e1eeea}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}article{background:white;border:1px solid #d3dcd6;padding:18px}.specimen{width:100%;height:240px;object-fit:contain}.scroll{overflow:auto;max-height:680px}table{border-collapse:collapse;min-width:1800px;width:100%;background:white;font-size:14px}td,th{border:1px solid #d3dcd6;padding:10px;text-align:left;vertical-align:top}th{position:sticky;top:0;background:#e9eee7}input,select{font:inherit;padding:9px;margin:12px 8px 12px 0}input{width:min(100%,600px)}small{color:#576773}.binjor{max-width:470px;width:100%}[hidden]{display:none!important}@media(max-width:780px){.cards{grid-template-columns:1fr}body{padding:0 15px}h1{font-size:28px}}</style>
<h1>Additional animal layouts, existing proposed readings, and a Binjor inscription photo</h1><p>23 November 2026 · local research continuation</p>
<div class="notice"><b>Imported the 2024 animal catalogue and a separate illustrated 33-object register.</b> The additions are published observations about animal imagery, faces and layout. Existing inscriptions and proposed readings are preserved. A Binjor photograph is retained separately with no invented numeric transcription.</div>
<h2>What changed from the animal data already in the repo?</h2><p>The downloaded 2022 workbook exactly matches the archived source file byte for byte. Compared with that baseline, the 2024 workbook adds a sign-coding column populated on <b>32 named rows</b> and changes common-field label values for <b>421 shared reference groups</b>. Many changes are nomenclature or corrections, not new archaeological discoveries. The 1,733 linked objects below are existing objects, not the number of newly added specimens. <a href="animal_version_changes.csv">All version differences</a> · <a href="animal_version_summary.json">Comparison scope and counts</a>.</p>
<h2>What the import actually contains</h2><p>'''+h(str(summary['named_source_rows']))+''' named source rows, plus '''+h(str(summary['continuation_rows']))+''' continuation rows. The named rows include '''+h(str(summary['parseable_distinct_source_references']))+''' distinct parseable references and '''+h(str(summary['unparsed_named_identifier_rows']))+''' unparsed identifiers. Exact CISI reference matching links the catalogue to '''+h(str(summary['linked_existing_objects']))+''' existing objects / '''+h(str(summary['linked_existing_faces']))+''' encoded faces. Those are existing artifacts, not newly found inscriptions.</p>
<p>The separate illustrated register contains 33 rows; '''+h(str(summary['frontal_rows_with_existing_links']))+''' have existing corpus links. The larger workbook has '''+h(str(summary['workbook_named_rows_with_F3_label']))+''' named rows tagged F3. These are different source inventories. Repeated references, blanks, uncertain animals and PDF/workbook disagreements remain visible. A–F source face labels are not silently equated with the corpus's numerical face IDs.</p>
<h2>Three concrete animal/text cases</h2><div class="cards">'''+''.join(cards)+'''</div>
<h2>Binjor / 4MSR: a site absent by name from the current metadata</h2><img class="binjor" src="images/binjor-unicorn-photo.jpeg" alt="Published Binjor unicorn seal photograph, secondary reproduction of a photograph credited to S. Subramanium"><p>An official ASI summary reports eleven excavated seals for the 2015–16/2016–17 seasons. This release recovers one published unicorn-seal photograph with an upper inscription, reported as five characters. The original accession, exact trench and numerical coding are not established here. Eleven seals do not mean eleven inscriptions, and absence of the site name does not prove that no unknown-provenance corpus row depicts the same object.</p>
<p>The photograph comes from a secondary reproduction of the excavation reporting. Its surrounding Vedic and metalwork decipherments are not adopted. Neither a nearby hearth nor the separate study of seven food balls is assigned as this seal's exact context.</p>
<h2>Five illustrated candidates missing exact corpus-reference matches</h2><p><b>K-37, K-34, B-14, B-11 and M-1718</b> have no exact CISI-ID match in the current metadata. They were already listed in the older published animal catalogue; they are not newly discovered artifacts. The first four place a single fish or pitchfork-like glyph in an animal scene; this alone does not establish a written word. M-1718 has a multi-sign line plus a frontal glyph, but the source disputes its numeral coding and the PDF/workbook differ. These are image-backed candidates for an explicit corpus crosswalk. Alternate IDs and glyph classification must be resolved before treating them as additional independent inscriptions. <a href="unmatched_illustrated_candidates.csv">All five records</a>.</p><div class="cards">'''+gallery+'''</div>
<h2>All 33 illustrated animal-facing-sign records</h2><p>Mahadevan sign numbers below are source numbers. Existing numerical sequences use the corpus's current numbering. Source uncertainty and disagreement are not repaired by choosing whichever interpretation fits a proposed meaning.</p><div class="scroll"><table id="frontal"><thead><tr><th>CISI</th><th>Animal</th><th>Gaze/orientation</th><th>Frontal sign(s), Mahadevan</th><th>Dorsal sign(s), Mahadevan</th><th>Existing coded sequences</th><th>Existing proposed readings</th><th>Found at</th><th>Qualification</th><th>Source disagreement</th></tr></thead><tbody>'''+frows+'''</tbody></table></div>
<h2>Search the larger catalogue and linked readings</h2><p>Source face A is shown for each medium in this view. The complete CSV retains every A–F field and every continuation row.</p><input id="search" aria-label="Search larger animal catalogue" placeholder="Search elephant, a city, a proposed word, or M-410"><select id="filter" aria-label="Filter records"><option value="all">All named source rows</option><option value="linked">With existing corpus links</option><option value="F3">Animal faces a sign (F3)</option></select><p id="count"></p><div class="scroll"><table id="catalogue"><thead><tr><th>Source row</th><th>CISI label</th><th>Right-side behavior</th><th>Left-side behavior</th><th>Source F3 coding</th><th>Seal face A</th><th>Impression face A</th><th>Existing faces</th><th>Existing proposed readings</th><th>Found at</th><th>Join status</th></tr></thead><tbody>'''+nrows+'''</tbody></table></div>
<h2>Other sources checked</h2><div class="scroll"><table style="min-width:1000px"><thead><tr><th>Source</th><th>What was found</th><th>What was added</th></tr></thead><tbody>'''+screen+'''</tbody></table></div>
<h2>What this enables next</h2><p>Use the explicit layouts to distinguish a glyph in an animal scene from the same glyph in the running inscription, and to identify where current occurrence counts depend on that distinction. Recover primary accession-labelled Binjor photos before assigning its signs or scoring a new-site prediction. This import adds no qualifying new family to the frozen 923 elephant/copper test and runs no new semantic validation.</p>
<h2>Data and sources</h2><p><a href="animal2024_named_records.csv">Named catalogue rows and existing readings</a> · <a href="animal2024_all_source_rows.csv">All raw source data rows</a> · <a href="frontal33_existing_readings.csv">33 illustrated cases</a> · <a href="binjor_source_records.csv">Unjoined Binjor photo record</a> · <a href="source_screen.csv">All source decisions</a> · <a href="source_issues.csv">Identifier and denominator issues</a> · <a href="image_sources.csv">Image attribution</a> · <a href="summary.json">Computed counts</a></p>
<p><a href="'''+ARTICLE+'''">Bhaskar 2024</a>: ESM1 and ESM13 are public supplements linked by the publisher. The older Bhaskar 2022 catalogue is already archived in the repo and is credited as prior work. Our addition is the current import and crosswalk; no claim is made that Cúper never read the 2024 paper. <a href="https://sansad.in/getFile/loksabhaquestions/annex/176/AU183.pdf?source=pqals">Official Binjor summary</a>; <a href="https://faculty.fordham.edu/vinod/kalyanaraman2021.pdf">Binjor photograph reproduction, p17</a>. No GitHub fetch or push. Colab units 0.</p>
<script>const rows=[...document.querySelectorAll('#catalogue tbody tr')],q=document.querySelector('#search'),f=document.querySelector('#filter');function apply(){let n=0;for(const r of rows){r.hidden=!(r.textContent.toLowerCase().includes(q.value.toLowerCase())&&(f.value==='all'||f.value==='linked'&&r.dataset.linked==='true'||f.value==='F3'&&r.dataset.front==='true'));n+=!r.hidden}document.querySelector('#count').textContent=n+' of '+rows.length+' named source rows shown'}q.addEventListener('input',apply);f.addEventListener('change',apply);apply()</script></html>'''
    (OUT/'online_expansion.html').write_text(page)


if __name__=='__main__':main()
