"""Join curated excavation evidence by accession, then display existing readings.

No function is inferred from signs, lexical readings, material or broad site labels.
This is retrospective source recovery, not an independent semantic experiment.
"""
import csv
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
CATALOGUE = BASE.parent / 'translation_catalogue/results/all_inscriptions.csv'
OUT = BASE / 'results'


def read(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows, fields=None):
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def canonical(value):
    return re.sub(r'[\s-]', '', value).upper()


def accession_matches(accession, excavation):
    # Only punctuation/spacing changes. Require a complete accession number;
    # a following source/figure label is allowed, a longer number is not.
    target = canonical(accession)
    return bool(re.search(r'(?<![A-Z0-9])' + re.escape(target) + r'(?![0-9])',
                          canonical(excavation)))


def main():
    OUT.mkdir(exist_ok=True)
    contexts = read(BASE / 'inputs/source_contexts.csv')
    specimens = read(BASE / 'inputs/source_specimens.csv')
    by_context = {r['context_id']: r for r in contexts}
    assert len(by_context) == len(contexts)
    assert len({r['source_specimen_id'] for r in specimens}) == len(specimens)
    assert all(r['context_id'] in by_context for r in specimens)
    assert len([r for r in specimens if r['source_id'] == 'DK1991']) == 25
    assert len([r for r in specimens if r['source_id'] == 'J2017']) == 7
    corpus = [r for r in read(CATALOGUE) if r['catalogue'] == 'Lipi']

    # Join stage deliberately receives only identity/context columns.
    identity = [{k: r[k] for k in ['face_id', 'object_identifier', 'reference',
                                  'city', 'excavation_number']} for r in corpus]
    links = []
    for s in specimens:
        c = by_context[s['context_id']]
        hits = []
        if s['match_policy'] == 'exact_accession':
            hits = [r for r in identity if r['city'] == c['site'] and
                    accession_matches(s['source_specimen_id'], r['excavation_number'])]
        objects = sorted({r['object_identifier'] for r in hits})
        assert len(objects) <= 1, f'Ambiguous accession: {s["source_specimen_id"]}'
        status = ('exact_accession' if hits else 'no_catalogue_match')
        if s['match_policy'] != 'exact_accession':
            status = 'unverified_candidate_not_joined'
        links.append({**s, 'site': c['site'], 'source_location': c['source_location'],
                      'assemblage_cluster': c['assemblage_cluster'],
                      'join_status': status,
                      'object_identifiers': '|'.join(objects),
                      'face_ids': '|'.join(r['face_id'] for r in hits),
                      'catalogue_references': '|'.join(r['reference'] for r in hits),
                      'matched_face_count': len(hits)})
    write('accession_links.csv', links)
    # The source evidence packet contains no transcription, reading or sounds.
    write('source_only_contexts.csv', contexts)
    write('source_only_specimens.csv', specimens)

    # Only after joining: attach all faces and verbatim existing proposal versions.
    faces = {r['face_id']: r for r in corpus}
    readings = []
    for link in links:
        if link['join_status'] != 'exact_accession':
            continue
        c = by_context[link['context_id']]
        for face_id in link['face_ids'].split('|'):
            r = faces[face_id]
            readings.append({
                'source_specimen_id': link['source_specimen_id'],
                'context_id': c['context_id'], 'assemblage_cluster': c['assemblage_cluster'],
                'site': c['site'], 'reference': r['reference'], 'face_id': face_id,
                'object_identifier': r['object_identifier'],
                'source_location': c['source_location'],
                'source_unit_item': link['unit_item'],
                'source_specimen_deposition': link['specimen_deposition'],
                'function_candidates': c['function_candidates'],
                'non_script_evidence': c['non_script_evidence'],
                'source_limitations': c['limits'], 'source_specimen_note': link['source_note'],
                'source_id': link['source_id'], 'source_pages': link['pages'],
                **{k: r[k] for k in ['excavation_number', 'excavation_area', 'block_or_house',
                    'room_or_grid', 'found_at', 'recorded_stratigraphy', 'material', 'object_type',
                    'sign_sequence', 'existing_proposed_translation', 'existing_reading_source',
                    'current_163_key_literal_meanings', 'unassigned_signs']},
            })
    write('readings_with_source_context.csv', readings)

    linked = [r for r in links if r['join_status'] == 'exact_accession']
    house = [r for r in linked if r['assemblage_cluster'] == 'H90-AreaC-house']
    summary = dict(
        source_context_records=len(contexts), source_specimen_records=len(specimens),
        matched_source_records=len(linked),
        matched_existing_objects=len({r['object_identifier'] for r in readings}),
        matched_existing_faces=len(readings),
        unmatched_exact_accession_records=sum(r['join_status'] == 'no_catalogue_match' for r in links),
        unverified_candidate_records=sum(r['join_status'] == 'unverified_candidate_not_joined' for r in links),
        linked_objects_by_site=dict(Counter(r['site'] for r in linked)),
        house_objects=len(house), house_faces=sum(r['matched_face_count'] for r in house),
        house_independent_assemblages=1,
        bagasra_inscribed_seals_near_faience=2,
        bagasra_shell_associated_source_fragments=2,
        bagasra_shell_associated_readable_inscriptions=0,
        independently_rated_contexts=0, semantic_validation_tests_run=0,
        interpretation='Additional source annotations and descriptive readings; not fresh blind validation.',
    )
    # Scope and failure checks are about recoverable identities, not semantic truth.
    assert summary['matched_existing_objects'] == 30
    assert summary['linked_objects_by_site'] == {'Harappa': 23, 'Gola Dhoro (Bagasra)': 6, 'Rakhigarhi': 1}
    assert summary['house_objects'] == 11 and summary['house_faces'] == 17
    by_acc = {r['source_specimen_id']: r for r in links}
    assert by_acc['H90-1687']['join_status'] == 'no_catalogue_match'
    assert by_acc['H90-1576']['join_status'] == 'no_catalogue_match'
    assert by_acc['BSR5555']['join_status'] == 'no_catalogue_match'
    assert by_acc['RGR1-elephant-sealings-pair']['object_identifiers'] == ''
    assert by_acc['RGR6304']['context_id'] == 'R-RGR2'
    assert not accession_matches('BSR2037', 'BSR20370')
    assert accession_matches('H90-1578', 'H90-1578Figure 13.46(a)')
    assert all(r['existing_proposed_translation'] == faces[r['face_id']]['existing_proposed_translation']
               for r in readings)
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')

    e = lambda x: html.escape(str(x))
    def table(headers, rows):
        return '<div class="scroll"><table><thead><tr>' + ''.join('<th>'+e(h)+'</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>'+cell+'</td>' for cell in row) + '</tr>' for row in rows) + '</tbody></table></div>'
    def reading_table(rows):
        return table(['Object / face', 'Complete existing proposed reading', 'Source location and deposit', 'Archaeological interpretation / limits'], [
            [e(r['source_specimen_id'])+'<br><b>'+e(r['reference'])+'</b><br>face '+e(r['face_id']),
             '<b>'+e(r['existing_proposed_translation'] or 'No existing translation')+'</b><details><summary>Current key, signs and original fields</summary><p>Current key: '+e(r['current_163_key_literal_meanings'])+'</p><p>Signs: '+e(r['sign_sequence'])+'</p><p>Reading source: '+e(r['existing_reading_source'])+'</p><p>Catalogue: '+e(r['found_at'])+'; '+e(r['recorded_stratigraphy'])+'</p></details>',
             e(r['source_location'])+'<p>'+e(r['source_specimen_deposition'])+'</p><small>'+e(r['source_id']+' '+r['source_pages']+'; '+r['source_specimen_note'])+'</small>',
             e(r['function_candidates'])+'<p>'+e(r['source_limitations'])+'</p>'] for r in rows])

    sections = []
    for title, selected in [
        ('Bagasra: all six catalogue objects, including damaged fragments', [r for r in readings if r['site'] == 'Gola Dhoro (Bagasra)']),
        ('Harappa: eleven objects in one house, with all faces kept separate', [r for r in readings if r['assemblage_cluster'] == 'H90-AreaC-house']),
        ('Harappa: other illustrated street, house and surface finds', [r for r in readings if r['site'] == 'Harappa' and r['assemblage_cluster'] != 'H90-AreaC-house']),
        ('Rakhigarhi: one exact mound/provenance link', [r for r in readings if r['site'] == 'Rakhigarhi'])]:
        sections.append('<h2>'+e(title)+'</h2>'+reading_table(selected))
    missing = [r for r in links if r['join_status'] != 'exact_accession']
    missing_html = table(['Source item', 'Location', 'Join outcome / reason'], [
        [e(r['source_specimen_id']), e(r['source_location']), e(r['join_status'])+'<p>'+e(r['source_note'])+'</p>'] for r in missing])
    ctx_html = table(['Context', 'Function candidates', 'Evidence without reading signs', 'Limits / source'], [
        [e(r['site'])+'<p>'+e(r['source_location'])+'</p>', e(r['function_candidates']), e(r['non_script_evidence']),
         e(r['limits'])+'<p>'+e(r['source_id']+'; '+r['pages'])+'</p>'] for r in contexts])
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Exact archaeological contexts and proposed readings</title>
<style>body{font:16px/1.55 system-ui,sans-serif;color:#18252c;background:#f5f5ef;margin:0}main{max-width:1450px;margin:auto;padding:28px}h1{max-width:1050px;font-size:34px;line-height:1.2}h2{margin-top:42px;font-size:24px}.intro{max-width:1000px}.notice{border-left:5px solid #a85b20;background:#fff3df;padding:15px 20px;max-width:1000px}.cards{display:flex;gap:14px;flex-wrap:wrap;margin:24px 0}.card{padding:16px 24px;background:#e3ece7;border-radius:10px}.card strong{font-size:30px;display:block}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;background:white;margin:14px 0}th{text-align:left;background:#253e43;color:white}td,th{padding:14px;vertical-align:top;border:1px solid #d7ded9}td{min-width:170px}td:nth-child(2){min-width:260px}small{color:#495f65}p{margin:8px 0}details{margin-top:10px}summary{cursor:pointer;color:#315e63}a{color:#145d72}input{font:inherit;width:min(95%,680px);padding:12px;border:1px solid #92a5a4;border-radius:6px}</style>
<main><h1>What do the inscriptions say where we can recover the archaeological context?</h1>
<div class="intro"><p>22 November 2026 · Primary-source context recovery. Every translation below is an existing proposal; no words have been changed to fit a workshop.</p>
<p>Thirty existing catalogue objects now have accession-linked source annotations. The useful distinction is between a reported workshop, a find near one, a house, and a displaced surface find.</p></div>
<div class="cards"><div class="card"><strong>30</strong>existing objects linked</div><div class="card"><strong>11</strong>objects in one Harappa house</div><div class="card"><strong>2</strong>seals near Bagasra faience activity</div><div class="card"><strong>0</strong>independent semantic tests</div></div>
<div class="notice"><b>What this establishes:</b> better documented locations and comparison cases. Collection was retrospective; the curator knew the readings and there are no independent ratings. Near a workshop does not mean that a seal names its product. The data do not yet provide secure craft-specific inscription groups for a comparative semantic test.</div>
<div class="intro"><h2>Three concrete corrections</h2><p><b>Bagasra:</b> BSR2037 and BSR8288 are near the faience/lithic area at similar reported depths. Keep them together as one vicinity cluster. Shell-associated BSR5555/6952 have lost the readable inscription; they cannot validate a bangle word. BSR7197 is probably redeposited near the gateway.</p>
<p><b>Harappa:</b> eleven objects belong to three rooms in one house. A small oven or kiln and domestic debris do not identify a textile or pottery workshop. Surface bangle H-2576 must not be assigned to an in-situ household activity.</p>
<p><b>Rakhigarhi:</b> RGR6304 is from mound RGR-2, while the bead factory with two reported elephant sealings is on RGR-1. The elephant-tag candidate is not joined without an accession or photographic identity check.</p>
<p>Sources and all uncertainties: <a href="../SOURCES.md">source notes</a> · <a href="../README.md">interpretation and reproduction</a> · <a href="accession_links.csv">all source joins and nonmatches</a> · <a href="readings_with_source_context.csv">complete reading/context table</a> · <a href="source_only_contexts.csv">source-only context packet</a></p></div>
<label for="search">Filter all tables by word, reference, accession or place</label><p><input id="search" placeholder="Try faience, Room 3, H-2576, BSR2037…"></p>
''' + ''.join(sections) + '<h2>Every unmatched source item and unverified candidate</h2>' + missing_html + '<h2>Source-only context evidence, including contexts with no linked inscription</h2>' + ctx_html + '''
<p id="filter-status" role="status"></p></main><script>const input=document.querySelector('#search');input.addEventListener('input',()=>{const q=input.value.toLowerCase();let shown=0;document.querySelectorAll('tbody tr').forEach(r=>{const yes=r.textContent.toLowerCase().includes(q);r.hidden=!yes;if(yes)shown++;});document.querySelector('#filter-status').textContent=shown+' rows shown across the tables';});</script></html>'''
    (OUT / 'contexts.html').write_text(page)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
