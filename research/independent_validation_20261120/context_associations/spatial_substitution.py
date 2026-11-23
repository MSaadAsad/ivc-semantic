"""Exact-remainder search with published spatial labels; no new sign readings.

Run from any directory. Uses existing local CSVs and never fetches from GitHub.
Candidate text equality is not scored as a verified physical substitution.
"""
import collections
import csv
import html
import json
from pathlib import Path
import re
import shutil

from online_expansion_extract import canonical

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
OUT = BASE / 'results/spatial_substitution'
SOURCE = BASE / 'results/online_expansion/frontal33_existing_readings.csv'
SOURCE_M77 = ['', '', '', '2133', '', '2554', '2565', '9204', '', '2516',
              '', '8071', '1167', '', '', '6122', '1385', '8011', '', '1550',
              '2279', '1303', '', '3080', '2518', '', '2661', '2316', '6402',
              '1093', '8121', '', '']


def read(p):
    with p.open() as f:
        return list(csv.DictReader(f))


def write(name, rows, fields=None):
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def codes(value):
    """Source punctuation is retained elsewhere; only exact numeric lists parse."""
    if not re.fullmatch(r'\d+(?:\s*;\s*\d+)*', value.strip()):
        return None
    return tuple(value.replace(' ', '').split(';'))


def insertions(dorsal, frontal):
    return {dorsal[:i] + frontal + dorsal[i:] for i in range(len(dorsal) + 1)}


def recovery_check():
    """Recover a constructed transfer without admitting changed remainder signs."""
    expected = ('59', '162', '342')
    options = insertions(('59', '342'), ('162',))
    assert expected in options
    # Look-alike one-token substitutions and extra/missing words are not matches.
    for wrong in [('60', '162', '342'), ('59', '162', '342', '1'), ('59', '162')]:
        assert wrong not in options
    assert codes('59?') is None and codes('59; lost') is None
    assert codes('59;342') == ('59', '342')


def main():
    recovery_check()
    OUT.mkdir(parents=True, exist_ok=True)
    sources = read(SOURCE)
    assert len(sources) == len(SOURCE_M77) == 33
    for i, r in enumerate(sources):
        r['source_version'] = 'Illustrated PDF'
        r['source_m77_text'] = SOURCE_M77[i]
    # Sensitivity: test both source versions, never choose the one that fits.
    by_ref = {canonical(r['cisi']): r for r in sources}
    variants = []
    for r in read(BASE / 'online_expansion_inputs/animal2024_rows.csv'):
        value = r['source_f3_signs_mahadevan']
        if r['source_named_row'] != 'True' or value.count(';') != 1:
            continue
        ref = canonical(r['raw_cisi'])
        if ref not in by_ref:
            continue
        f, d = value.split(';')
        a = dict(by_ref[ref], source_version='Workbook sensitivity',
                 frontal_mahadevan=f.strip().replace(',', ';'),
                 dorsal_mahadevan=d.strip().replace(',', ';'))
        variants.append(a)
    all_sources = sources + variants
    cw = read(REPO / 'work_data/lipi_mahadevan_crosswalk.csv')
    mapping = {r['lipi']: r['mahadevan'] for r in cw if r['rank_for_lipi_sign'] == '1'}
    assert len(mapping) == sum(r['rank_for_lipi_sign'] == '1' for r in cw)
    corpus = read(BASE.parent / 'translation_catalogue/results/all_inscriptions.csv')
    lipi = {r['face_id']: r for r in corpus if r['catalogue'] == 'Lipi'}
    mah = read(BASE / 'spatial_substitution_inputs/mahadevan_raw_rows.csv')
    mah_gloss = {}
    for r in corpus:
        if r['catalogue'] == 'Mahadevan':
            m = re.fullmatch(r'Mahadevan (\d+) / line (\d+)', r['reference'])
            if m:
                mah_gloss[m.groups()] = r
    stamps = {r['face']: r for r in read(REPO / 'work_data/stamps/objects.csv')}
    # Keep every candidate row; identical formulas are grouped only when reporting.
    targets = []
    for r in lipi.values():
        if r['intact_as_recorded'] != 'True' or not r['object_type'].startswith(('SEAL', 'TAG')):
            continue
        seq = tuple(r['sign_sequence'].split('-'))
        if not seq or not all(s in mapping for s in seq):
            continue
        targets.append(dict(channel='Lipi rank-1 crosswalk', target_id=r['face_id'], target_object=r['object_identifier'],
                            reference=r['reference'], sequence=tuple(mapping[s] for s in seq),
                            original_sequence=r['sign_sequence'], proposed_translation=r['existing_proposed_translation'],
                            found_at=r['found_at'], object_type=r['object_type'],
                            photos=stamps.get(r['face_id'], {}).get('photos', ''),
                            physical_line_verified=False))
    for r in mah:
        if r['strict'] != '1' or r['inscobj'] not in ('1', '2'):
            continue
        seq = tuple(r[f'S{i}'] for i in range(1, 15) if r[f'S{i}'])
        if not all(s.isdigit() and int(s) > 0 for s in seq):
            continue
        t = mah_gloss.get((r['textnum'], r['sideline']), {})
        targets.append(dict(channel='Direct Mahadevan', target_id=r['index'], target_object=r['textnum'],
                            reference=f'Mahadevan {r["textnum"]} / line {r["sideline"]}',
                            sequence=seq, original_sequence='-'.join(seq),
                            proposed_translation=t.get('existing_proposed_translation', 'No joined existing translation'),
                            found_at=t.get('found_at', f'M77 site code {r["textnum"][0]}; locus {r["locus"]}; level {r["level"]}'),
                            object_type={'1': 'seal', '2': 'sealing'}[r['inscobj']],
                            photos='', physical_line_verified=False))
    index = collections.defaultdict(list)
    for t in targets:
        index[t['sequence']].append(t)
    anchors, candidates, representation = [], [], []
    for r in all_sources:
        f, d = codes(r['frontal_mahadevan']), codes(r['dorsal_mahadevan'])
        reasons = []
        if not f or len(f) != 1:
            reasons.append('frontal code uncertain, non-numeric, or multiple signs')
        if not d:
            reasons.append('no exact numeric dorsal list')
        elif len(d) < 2:
            reasons.append('fewer than two dorsal signs')
        if r['source_disagreement']:
            reasons.append('source-code/identification disagreement')
        if r['source_version'] != 'Illustrated PDF':
            reasons.append('alternate workbook coding; sensitivity only')
        if r['cisi'] == 'K-39':
            reasons.append('unmapped/disputed left-facing variant')
        if r['cisi'] == 'C-23':
            reasons.append('source explicitly disputes frontality')
        primary = not reasons
        a = dict(source_row=r['source_row'], reference=r['cisi'], source_version=r['source_version'], animal=r['animal'],
                 frontal_mahadevan=r['frontal_mahadevan'], dorsal_mahadevan=r['dorsal_mahadevan'],
                 primary_anchor=primary, primary_exclusion='; '.join(reasons),
                 source_disagreement=r['source_disagreement'], source_m77_text=r['source_m77_text'],
                 existing_proposed_reading=r['existing_proposed_readings'], found_at=r['found_at'],
                 photo='../online_expansion/' + r['source_photo'])
        anchors.append(a)
        # Object-level representation only: source A-F faces are not aligned here.
        ids = [s.strip() for s in r['existing_face_ids'].split(';') if s.strip()]
        present, absent, unmapped = [], [], []
        for face in ids:
            signs = lipi[face]['sign_sequence'].split('-')
            mapped = [mapping.get(s) for s in signs]
            if f and all(s in mapped for s in f):
                present.append(face)
            elif f and all(mapped):
                absent.append(face)
            else:
                unmapped.append(face)
        if not ids:
            status = 'no exact corpus object link'
        elif not f:
            status = 'uncertain frontal code; not classified'
        elif present:
            status = 'frontal glyph represented in at least one stored face'
        elif unmapped:
            status = 'not detected; incomplete numerical crosswalk'
        else:
            status = 'frontal glyph absent from all mapped stored faces'
        if r['source_version'] == 'Illustrated PDF':
            representation.append(dict(**a, representation=status, present_faces='; '.join(present),
                                       absent_faces='; '.join(absent), unresolved_faces='; '.join(unmapped),
                                       old_field_object_labels=r['old_field_object_labels'],
                                       existing_sequences=r['existing_sign_sequences']))
        if not f or not d:
            continue
        # Both displayed orders remain labelled, not optimized into one reading.
        for orientation, dd, ff in [('source-listed', d, f), ('reversed', d[::-1], f[::-1])]:
            for seq in sorted(insertions(dd, ff)):
                for t in index.get(seq, []):
                    if t['channel'].startswith('Lipi'):
                        if t['target_id'].split('.')[0] in r['existing_object_ids'].split('; '):
                            continue
                    elif t['target_object'] == r['source_m77_text']:
                        continue
                    candidates.append(dict(anchor_reference=r['cisi'], anchor_source_row=r['source_row'],
                                           anchor_source_version=r['source_version'],
                                           primary_anchor=primary, primary_exclusion=a['primary_exclusion'],
                                           frontal_mahadevan='-'.join(ff), dorsal_mahadevan='-'.join(dd),
                                           tested_orientation=orientation, matched_mahadevan='-'.join(seq), **t))
    # Tuple sequence is an internal search key, not a second printed transcription.
    for t in candidates:
        del t['sequence']
    write('anchors.csv', anchors)
    write('representation.csv', representation)
    fields = ['anchor_reference', 'anchor_source_row', 'anchor_source_version', 'primary_anchor', 'primary_exclusion',
              'frontal_mahadevan', 'dorsal_mahadevan', 'tested_orientation', 'matched_mahadevan',
              'channel', 'target_id', 'target_object', 'reference', 'original_sequence',
              'proposed_translation', 'found_at', 'object_type', 'photos', 'physical_line_verified']
    write('candidates.csv', candidates, fields)
    reviews = read(BASE / 'spatial_substitution_inputs/photo_review.csv')
    supported = [r for r in reviews if r['review_status'] == 'supported spatial parallel']
    for r in supported:
        assert any(t['anchor_reference'] == r['anchor_reference'] and t['reference'] == r['target_reference'] for t in candidates)
        assert (BASE / 'spatial_substitution_inputs/images' / r['photo']).is_file()
    summary = dict(source_rows=len(sources), primary_anchors=sum(a['primary_anchor'] for a in anchors),
                   additional_workbook_variants=len(variants),
                   parsed_dorsal_frontal_anchors=sum(bool(codes(r['frontal_mahadevan']) and codes(r['dorsal_mahadevan'])) for r in sources),
                   searched_target_rows=len(targets), searched_distinct_target_formulas=len(index),
                   target_rows_by_channel=dict(collections.Counter(t['channel'] for t in targets)),
                   raw_candidate_rows=len(candidates),
                   unique_anchor_channel_target_matches=len({(t['anchor_reference'], t['channel'], t['target_id']) for t in candidates}),
                   primary_candidate_rows=sum(t['primary_anchor'] for t in candidates),
                   primary_anchor_references_with_candidates=sorted({t['anchor_reference'] for t in candidates if t['primary_anchor']}),
                   sensitivity_anchor_references_with_candidates=sorted({t['anchor_reference'] for t in candidates if not t['primary_anchor']}),
                   candidate_target_references=sorted({t['reference'] for t in candidates}),
                   representation_counts=dict(collections.Counter(r['representation'] for r in representation)),
                   primary_spatial_pairs_verified=0,
                   exploratory_spatial_pair_comparisons_supported=len(supported),
                   exploratory_source_layouts_supported=len({r['anchor_reference'] for r in supported}),
                   distinct_count_patterns_supported=1 if supported else 0,
                   independently_blind_reviewed_pairs=0,
                   semantic_substitutions_validated=0, heldout_prediction_trials=0,
                   colab_units=0,
                   interpretation='Four reviewed comparisons support one short six-stroke/trident spatial pattern. No primary longer-remainder match or independent validation of cloth, a language, or seven strokes.')
    (OUT / 'search_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    write('photo_review.csv', reviews)
    shutil.copy2(BASE / 'spatial_substitution_inputs/image_sources.csv', OUT / 'image_sources.csv')
    shutil.copytree(BASE / 'spatial_substitution_inputs/images', OUT / 'images', dirs_exist_ok=True)
    report(summary, anchors, candidates, reviews, representation, lipi)
    print(json.dumps(summary, indent=2))


def table(rows, columns):
    h = html.escape
    return '<div class="scroll"><table><thead><tr>' + ''.join('<th>' + h(label) + '</th>' for _, label in columns) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + h(str(r.get(k, ''))) + '</td>' for k, _ in columns) + '</tr>' for r in rows) + '</tbody></table></div>'


def report(summary, anchors, candidates, reviews, representation, lipi):
    h = html.escape
    review_table = table(reviews, [('anchor_reference', 'Scene-layout object'), ('target_reference', 'Possible inline counterpart'), ('review_status', 'Image review result'), ('observation', 'What the evidence shows')])
    anchor_table = table([a for a in anchors if a['source_version'] == 'Illustrated PDF'], [('reference', 'Reference'), ('animal', 'Animal'), ('frontal_mahadevan', 'Beside animal, source code'), ('dorsal_mahadevan', 'Above/behind, source codes'), ('primary_anchor', 'Primary search'), ('primary_exclusion', 'Why excluded from primary')])
    examples = []
    for ref in ['M-1904', 'H-71', 'M-178', 'M-822', 'M-1365', 'B-10', 'M-1200', 'K-26', 'M-1782']:
        rr = [r for r in lipi.values() if r['reference'] == ref]
        examples.append(dict(reference=ref, signs=' | '.join(r['sign_sequence'] for r in rr),
                             old_reading=' | '.join(r['existing_proposed_translation'] for r in rr),
                             found_at=' | '.join(sorted({r['found_at'] for r in rr}))))
    readings = table(examples, [('reference', 'Object'), ('signs', 'Unchanged existing transcription'), ('old_reading', 'Unchanged existing proposed English'), ('found_at', 'Recorded findspot')])
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Testing a sign beside the animal against the same sign in text</title><style>
*{box-sizing:border-box}body{max-width:1200px;margin:36px auto;padding:0 22px;background:#faf8f1;color:#243646;font:17px/1.55 system-ui,sans-serif}h1{font-size:36px;line-height:1.15}h2{font-size:26px;margin-top:36px}.finding{padding:20px;background:#e5eee9;border-left:6px solid #287665}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.cards article{background:white;border:1px solid #d0d9d2;padding:16px}.cards img{width:100%;height:235px;object-fit:contain}h3{margin:0 0 14px;font-size:21px}.scroll{overflow:auto}table{border-collapse:collapse;min-width:900px;width:100%;background:white;font-size:14px}td,th{border:1px solid #d3dad5;text-align:left;vertical-align:top;padding:10px}th{background:#e9eee8}a{color:#096780}small{color:#546575}.note{background:#fff1d8;padding:16px}.summary{font-size:20px}li{margin-bottom:8px}@media(max-width:750px){.cards{grid-template-columns:1fr}h1{font-size:29px}}</style>
<h1>The six-stroke mark and trident occur in two layouts</h1><p>Local continuation · 23 November 2026 · photographs compared with unchanged catalogue readings</p>
<div class="finding"><b>One short pattern has a photographed spatial parallel.</b> M-1904 puts the six-stroke mark above a goat and the trident beside it. Four reviewed counterparts put six strokes and a trident together in text. This permits the conditional whole-design reading “six [cloth?]” using Cúper’s existing value for the trident. The word <b>cloth</b> has not been independently established.</div>
<h2>See the actual comparison</h2><div class="cards">
<article><h3>M-1904 · Mohenjo-daro</h3><img src="../online_expansion/images/frontal-07.jpg" alt="Published M-1904 photograph: six strokes above goat, trident in animal field"><p><b>Six strokes above; trident beside goat.</b> Existing running-text reading: “3 3.” The trident was already retained separately as field code S390. Bhaskar groups the strokes as six.</p></article>
<article><h3>M-178 · Mohenjo-daro</h3><img src="images/M-178_a.jpg" alt="M-178 has six strokes and trident in upper text"><p><b>Six strokes and trident together above the animal.</b> Existing proposed reading: “6 Woven-Cloths.” M-822 and H-71 provide two further reviewed upper-text counterparts.</p></article>
<article><h3>M-1365 · Mohenjo-daro</h3><img src="images/M-1365_a.jpg" alt="M-1365 text face with six strokes and trident"><p><b>The pair on a text face.</b> This face has no animal scene to account for the trident’s position. Another panel of the object depicts an animal. Existing proposed reading: “6 Woven-Cloths.”</p></article></div>
<p class="summary">The measured correspondence is <b>six strokes + trident</b>. The interpretation <b>six cloth items</b> depends on Cúper’s proposed meaning for the trident, sign 390 (Mahadevan 162). A different countable label could fit the same arrangement.</p>
<h2>What was tested and what happened</h2><ul>
<li>All 33 illustrated layouts were retained, plus 19 separately labelled workbook variants. Six source examples meet the primary rule of one clear frontal sign, at least two clear dorsal signs, and no source disagreement.</li>
<li>The exact-insertion search examined ''' + str(summary['searched_target_rows']) + ''' eligible catalogue rows, corresponding to ''' + str(summary['searched_distinct_target_formulas']) + ''' distinct numerical sequences across overlapping catalogues. A candidate must preserve the complete remaining text and add only the scene sign.</li>
<li><b>No primary longer-remainder match.</b> The expanded search finds candidates for three source objects: M-1904, B-10 and K-26.</li>
<li><b>Four photographed counterparts support M-1904’s short six-stroke pattern</b>: H-71, M-178, M-822 and M-1365. They are one count-and-sign pattern, not four independently predicted meanings.</li>
<li>M-987 is broken; M-1799 has no recovered photo. The leaf-and-jar K-26 comparison lacks a verified counterpart photograph.</li>
<li>B-10’s seven-stroke lead is unresolved. Its PDF and workbook use different numeral codes. M-1200 panel c visibly places a trident beside a stroke group, but its full stroke count cannot be independently confirmed as seven from the reproduction. It is not a confirmed second count.</li></ul>
<div class="note"><b>No held-out prediction was scored.</b> This is an exact-pattern discovery followed by image checks. Zero longer matches in this selected register does not reject spatial interchange throughout the script. No p-value, established English meaning or language attribution follows from these images.</div>
<h2>The unresolved seven-stroke case</h2><div class="cards"><article><h3>B-10 · source scene</h3><img src="../online_expansion/images/frontal-08.jpg" alt="Published B-10 goat scene with stroke group above and trident beside it"><p>PDF dorsal 110; workbook dorsal 112. Both codings remain visible in the candidate export.</p></article><article><h3>M-1200 · panel c</h3><img src="images/M-1200_c.jpg" alt="M-1200 c shows a trident beside upper and lower marks"><p>The catalogues give seven plus trident. The photograph shows upper and lower marks; this review cannot confirm a seven-stroke total.</p></article></div>
<h2>All counterpart image decisions</h2>''' + review_table + '''
<h2>Meanings and archaeological locations</h2><p>These are the stored proposals, not established translations. No original transcription is overwritten. The four supported inline counterparts span Mohenjo-daro and Harappa, but one Harappan occurrence is not an independent city-level prediction.</p>''' + readings + '''
<h2>Where the source examples enter the primary search</h2>''' + anchor_table + '''
<h2>What is new relative to the repo</h2><p>Cúper already investigated copper picture/sign substitutions, animal/text associations and field glyphs. The old metadata already mark M-1904’s trident as S390 outside its stored running text. Bhaskar’s published 2024 classification already identifies the frontal/dorsal positions. This continuation adds the explicit exact-remainder search across both numerical catalogues and the counterpart photograph decisions. It does not claim to discover the trident, the six-and-trident formula or the general idea of movable signs.</p>
<h2>Data and reproducibility</h2><p><a href="anchors.csv">All source versions and exclusions</a> · <a href="candidates.csv">Every raw candidate match</a> · <a href="photo_review.csv">Complete image review</a> · <a href="representation.csv">How scene glyphs enter current stored transcriptions</a> · <a href="search_summary.json">Computed counts</a> · <a href="image_sources.csv">Local image provenance</a></p><p>Source images: <a href="https://static-content.springer.com/esm/art%3A10.1007%2Fs43539-023-00102-3/MediaObjects/43539_2023_102_MOESM1_ESM.pdf">Bhaskar 2024 ESM1</a>, originally courtesy CISI; other CISI reproductions recovered unmodified from an existing local checkout. Direct Mahadevan search uses original strict/uncertainty flags rather than accepting cleaned doubtful signs. No GitHub fetch/push. Colab units: 0.</p></html>'''
    (OUT / 'spatial_substitution.html').write_text(page)


if __name__ == '__main__':
    main()
