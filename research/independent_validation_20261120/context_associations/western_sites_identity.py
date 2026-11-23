"""Publish the completed documentary crosswalk review, not a semantic validation."""
import csv
import html
import json
from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent
INPUT = BASE / 'western_sites_inputs'
OUT = BASE / 'results/western_sites'
PAPER = 'https://www.nature.com/articles/s41599-023-02320-7'
REGISTER = 'https://www.scribd.com/document/262316120/Excavations-at-Dholavifra-1989-2005-RS-Bisht-2015'


def read(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (OUT / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def run(source, candidates, old):
    review = read(INPUT / 'identity_review.csv')
    by_pair = {(r['source_record'], r['corpus_object_id']): r for r in review}
    assert len(by_pair) == len(review)
    assert set(by_pair) == {(r['source_record'], r['corpus_object_id']) for r in candidates}
    supported = {k for k, r in by_pair.items() if r['decision'] == 'documentary_context_link_supported'}
    assert supported == {('DHR2015-33', '4156'), ('DHR2015-45', '4292')}
    joined = []
    for r in candidates:
        item = by_pair[(r['source_record'], r['corpus_object_id'])]
        accepted = (r['source_record'], r['corpus_object_id']) in supported
        r.update(documentary_context_link_accepted=accepted, identity_review_decision=item['decision'],
                 identity_comparison=item['comparison_basis'], identity_discrepancies=item['discrepancies'],
                 physical_specimen_identity_verified=False)
        if accepted:
            r['reason'] = 'Source-labelled sign image and excavation metadata support a documentary context link; no separately authenticated corpus photograph or physical specimen authentication.'
        if accepted:
            joined.append(dict(source_record=r['source_record'], source_accession=r['source_accession'],
                               corpus_object_id=r['corpus_object_id'], corpus_face_id=r['corpus_face_id'],
                               attachment_category=r['attachment_category'], source_qualification=r['source_qualification'],
                               observation=r['source_observation'], existing_sign_sequence=r['existing_sign_sequence'],
                               existing_proposed_reading=r['existing_proposed_reading'],
                               scope='object context inherited; face sequence not independently verified' if r['corpus_face_id']=='4156.2'
                                     else 'source-labelled signs and excavation context support documentary link',
                               semantic_validation_eligible=False, physical_identity_verified=False,
                               source_url=r['source_url'], printed_pages=r['printed_pages'],
                               additional_sign_source=PAPER if r['source_accession']=='4608' else ''))
    for r in source:
        r['documentary_context_link_accepted'] = any(k[0] == r['source_record'] for k in supported)
    for r in old:
        links = [j for j in joined if j['corpus_object_id'] == r['corpus_object_id']]
        r['newly_accepted_context'] = '; '.join(sorted({j['attachment_category'] for j in links}))
        r['context_acceptance_scope'] = 'documentary context link; not physical specimen authentication' if links else ''
    write('identity_review.csv', review)
    write('documentary_context_links.csv', joined)
    summary = dict(reviewed_source_object_pairs=len(review), supported_documentary_context_objects=len(supported),
                   context_linked_existing_faces=len(joined), directly_compared_sign_faces=2,
                   unresolved_source_object_pairs=len(review)-len(supported),
                   independently_authenticated_physical_specimens=0, new_sign_transcriptions=0,
                   semantic_validation_tests_run=0, colab_units=0)
    (OUT / 'identity_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    assets = OUT / 'identity_images'
    shutil.copytree(INPUT / 'identity_images', assets, dirs_exist_ok=True)
    h = html.escape
    rows = ''.join('<tr>'+''.join('<td>'+h(r[k].replace('_',' ') if k=='decision' else r[k])+'</td>'
                                for k in ['source_accession','corpus_object_id','decision','comparison_basis','discrepancies','reading_assessment'])+'</tr>'
                   for r in review)
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dholavira: completed context-link review</title><style>
*{box-sizing:border-box}body{font:17px/1.55 system-ui,sans-serif;color:#253647;background:#faf8f2;max-width:1180px;margin:36px auto;padding:0 22px}h1{font-size:34px;line-height:1.2}h2{margin-top:32px}a{color:#0e647b}.note{background:#e1eeea;border-left:5px solid #287d70;padding:18px}.cards{display:grid;grid-template-columns:1fr 1fr;gap:20px}.card{background:white;border:1px solid #d3dcd6;padding:20px}.photo{width:100%;height:190px}.sequence{max-width:100%;height:80px;object-fit:contain}.scroll{overflow:auto}table{border-collapse:collapse;min-width:1500px;width:100%;font-size:14px;background:white}td,th{border:1px solid #d3dcd6;padding:10px;text-align:left;vertical-align:top}th{background:#e9eee7}input{font:inherit;width:100%;padding:10px;margin:16px 0}small{color:#576773}@media(max-width:650px){.cards{grid-template-columns:1fr}body{padding:0 15px}h1{font-size:28px}}</style>
<h1>Dholavira: two context links supported by source images and findspots</h1><p>23 November 2026 · completed documentary review · saved locally</p>
<div class="note"><b>Two existing objects now have usable documentary context links: a box attachment and textile contact.</b> We reviewed 21 source/object possibilities. Nineteen remain unresolved. No new inscription or translation was created.</div>
<p>This links a published accession-labelled image or sign drawing to an existing coded inscription using visible signs and recorded excavation context. It is not a comparison of two independently authenticated photographs of the physical specimen. The two links remain excluded from a claim of fresh predictive semantic validation.</p>
<div class="cards"><section class="card"><h2>4608 ↔ object 4156: box attachment</h2>
<svg class="photo" viewBox="0 45 208 150" role="img" aria-label="Published front and back photographs beside accession 4608"><image href="identity_images/page-337-image.jpg" width="784" height="195"/></svg>
<p><b>Existing proposal:</b> “two quarters: [lost sign], chief.”</p>
<img class="sequence" src="identity_images/4608_published_signs.png" alt="Drawing explicitly labelled ASI 4608 in the 2023 paper: arrow-shaped sign, missing position, two strokes and spoked wheel">
<p>The 2023 paper explicitly names ASI 4608 beside this drawing. Its display order matches <code>520–000–002–820</code>; Cúper's analytical order for 4156.1 is <code>820–002–000–520</code>. Bailey, XH 34, 45 cm, red complete sealing, unicorn and two impressions also agree.</p>
<p>The excavation report infers a square/rectangular box from the reverse. This attaches a documented box-use context to the existing proposed reading. A box can carry an authority's mark, a quantity or other information: it does not establish “chief” or “quarter-share.” The second encoded impression, 4156.2, inherits object context only.</p>
<small>Bisht 2015, printed p319; Mukhopadhyay 2023, discussion of ASI 4608.</small></section>
<section class="card"><h2>20502 ↔ object 4292: textile contact</h2>
<svg class="photo" viewBox="0 200 208 142" role="img" aria-label="Published front and back photographs beside accession 20502"><image href="identity_images/page-341-image.jpg" width="784" height="342"/></svg>
<p><b>Existing reading:</b> <code>[604]</code> — unresolved.</p>
<p>The source photo beside accession 20502 preserves a ladder-shaped sign compatible with 604. South Reservoir, 48×45×4, stratum 7, 312 cm, a grey fragment and one surviving sign agree with 4292.1.</p>
<p>The report identifies textile impressions on the back. We attach <b>textile contact</b>, not “cloth commodity” or a translation “cloth.” The sign could label an issuer, authorization, amount, contents or something else; this object alone does not distinguish them.</p>
<small>Bisht 2015, printed p323. The source page placement and front/back photographs were inspected; no separate accession-labelled corpus photograph was recovered.</small></section></div>
<h2>What the other comparisons changed</h2><p>The proposed vessel-linked object 4289 has a source/catalogue period disagreement and different sign counts. Object 4300, currently coded 923 and proposed “Ivory,” is described by the excavator as a half fragment whose mark might be a symbol rather than an Indus sign. Neither supplies a new confirmed commodity reading. Face 3951.1 still has two competing source candidates at 320 cm.</p>
<h2>All reviewed source/object possibilities</h2><input id="search" aria-label="Search identity review" placeholder="Search accession, object ID, discrepancy or proposed meaning"><p id="count"></p><div class="scroll"><table id="review"><thead><tr><th>Source accession</th><th>Existing object</th><th>Decision</th><th>Evidence checked</th><th>Discrepancies retained</th><th>Meaning and use</th></tr></thead><tbody>'''+rows+'''</tbody></table></div>
<h2>Files and sources</h2><p><a href="western_sites.html">All 61 source records</a> · <a href="documentary_context_links.csv">Accepted documentary context links</a> · <a href="identity_review.csv">All 21 reviews</a> · <a href="identity_summary.json">Counts</a> · <a href="identity_images/sources.csv">Image attribution</a></p>
<p>Source register: <a href="'''+REGISTER+'''">Bisht 2015, printed pp309–329</a>. Accession-labelled sign drawing: <a href="'''+PAPER+'''">Mukhopadhyay 2023</a>. The observations and drawing were already published. Our addition is their explicit connection to the existing corpus IDs; no claim is made that Cúper never saw these sources.</p>
<script>const rows=[...document.querySelectorAll('#review tbody tr')],q=document.querySelector('#search');function apply(){let n=0;for(const r of rows){r.hidden=!r.textContent.toLowerCase().includes(q.value.toLowerCase());n+=!r.hidden}document.querySelector('#count').textContent=n+' of 21 source/object reviews shown'}q.addEventListener('input',apply);apply()</script></html>'''
    (OUT / 'identity_review.html').write_text(page)
    return summary


if __name__ == '__main__':
    raise SystemExit('Run western_sites.py to rebuild the source tables and completed identity review together.')
