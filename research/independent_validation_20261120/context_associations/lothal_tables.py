"""Expand the Lothal archaeological table and join all existing face readings.

Run with the validation environment's numpy and Pillow. No network, model fitting
or automatically invented sign transcriptions. The source-table rasters are
retained so the 93 hand-transcribed categories/contexts can be checked against
independent grid-cell and marker measurements.
"""
import collections
import csv
import html
import json
import re
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
INPUT = BASE / 'lothal_inputs'
OUT = BASE / 'results/lothal_tables'
SOURCE = 'https://doi.org/10.5281/zenodo.5513821'
CATEGORIES = ['pegs_on_wall', 'locker', 'structure', 'parallel_reeds', 'wooden_box',
              'pottery_jar', 'leather_sack', 'basket', 'single_rope', 'other_types', 'undiagnostic']
CONTEXTS = {'filled_circle': 'warehouse', 'open_square': 'other_context', 'question_mark': 'unknown_context'}
GROUPS = ['elephant', 'unicorn_1', 'unicorn_2', 'unicorn_3', 'unicorn_4', 'unicorn_5', 'unicorn_6']


def read(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def write(name, rows):
    assert rows, name
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def runs(v):
    groups = []
    for i in np.flatnonzero(v):
        if not groups or i > groups[-1][-1] + 1:
            groups.append([int(i)])
        else:
            groups[-1].append(int(i))
    return [sum(g) / len(g) for g in groups]


def black(n):
    return np.array(Image.open(INPUT / f'source_tables/table-{n}.png').convert('L')) < 180


def verify_source_cells(source):
    lookup = {r['cisi']: r for r in source}
    checked = []
    for image, start, threshold in [(40, 124, 135), (44, 171, 137)]:
        a = black(image)
        xs = runs(a.mean(0) > .65)
        ys = [v for v in runs(a.mean(1) > .65) if v > threshold]
        assert len(xs) == 14
        assert len(ys) == (48 if image == 40 else 47)
        for i, (y0, y1) in enumerate(zip(ys, ys[1:])):
            cisi = f'L-{start+i}'
            hits = []
            for j, (x0, x1) in enumerate(zip(xs[2:], xs[3:])):
                cell = a[round(y0)+3:round(y1)-2, round(x0)+4:round(x1)-3]
                yy, xx = np.where(cell)
                if len(xx) > 4:
                    height = int(np.ptp(yy)) + 1
                    marker = 'question_mark' if height >= 11 else ('filled_circle' if len(xx) >= 45 else 'open_square')
                    hits.append(dict(category=CATEGORIES[j], marker=marker, pixels=len(xx), height=height))
            assert len(hits) == 1, (cisi, hits)
            hit = hits[0]
            assert hit['category'] == lookup[cisi]['container'], (cisi, hit, lookup[cisi])
            assert hit['marker'] == lookup[cisi]['context_marker'], (cisi, hit, lookup[cisi])
            checked.append(dict(cisi=cisi, source_image=f'table-{image}.png',
                                source_row=i+1, **hit, hand_transcription_agrees=True))
    write('source_cell_checks.csv', checked)
    return checked


def repeated_dies():
    a = black(30)
    # Object labels read directly from the source image, including its three blank rows.
    refs = list(range(124, 140)) + list(range(161, 173)) + list(range(189, 207))
    ys = [v for v in runs(a.mean(1) > .65) if v > 70]
    xs = [52.5, 79, 105, 131, 157.5, 184, 210, 236]
    assert len(ys) == len(refs) + 1 == 47
    matrix, members = [], []
    for ref, y0, y1 in zip(refs, ys, ys[1:]):
        row = dict(cisi=f'L-{ref}')
        for g, x0, x1 in zip(GROUPS, xs, xs[1:]):
            pixels = int(a[round(y0)+3:round(y1)-2, round(x0)+3:round(x1)-2].sum())
            row[g] = int(pixels >= 6)
            if pixels >= 6:
                assert 15 <= pixels <= 30, (ref, g, pixels)
                members.append(dict(cisi=f'L-{ref}', published_die_group=g,
                                    source='Frenez 2020 table1 p29', source_url=SOURCE,
                                    basis='Author groups impressions as same seal; not independently reverified here',
                                    dark_marker_pixels=pixels))
        matrix.append(row)
    write('repeated_seal_matrix.csv', matrix)
    write('repeated_die_memberships.csv', members)
    return matrix, members


def join(source, members):
    stamps = collections.defaultdict(list)
    for r in read(REPO / 'work_data/stamps/objects.csv'):
        stamps[r['cisi']].append(r)
    readings = collections.defaultdict(list)
    for r in read(BASE.parent / 'translation_catalogue/results/all_inscriptions.csv'):
        if r['catalogue'] == 'Lipi':
            readings[r['reference']].append(r)
    backs = {r['cisi']: r for r in read(REPO / 'work_data/stamps/backs_seen.csv')}
    die_by_ref = collections.defaultdict(list)
    for r in members:
        die_by_ref[r['cisi']].append(r['published_die_group'])
    prior_followup = {'L-201', 'L-208', 'L-210'}
    objects, faces = [], []
    for raw in source:
        ref = raw['cisi']
        rr = readings[ref]
        ss = stamps[ref]
        types = sorted({r['type'] for r in ss})
        specific_type = any(t != 'TAG' for t in types)
        old_labels = specific_type or ref in backs or ref in prior_followup
        texts = [r['sign_sequence'] for r in rr]
        signs = set(s for t in texts for s in t.split('-') if re.fullmatch(r'\d{3}', s) and s != '000')
        photos = sorted({p.name for p in (INPUT / 'recovered_photos').glob('*.jpg') if ref + '_' in p.name})
        o = dict(**raw, context=CONTEXTS[raw['context_marker']], source_url=SOURCE,
                 source_table='2 part1' if raw['printed_page'] == '31' else '2 part2',
                 corpus_joined=bool(rr), corpus_faces=len(rr), published_impressions=int(raw['impressions']),
                 impression_count_equals_encoded_faces=int(raw['impressions']) == len(rr),
                 old_catalogue_types='; '.join(types), old_back_note=backs.get(ref, {}).get('back', ''),
                 prior_followup_context_seen=ref in prior_followup,
                 prior_specific_backing_evidence=old_labels,
                 newly_supplied_backing_label=not old_labels,
                 published_die_groups='; '.join(die_by_ref[ref]),
                 sign_sequences=' | '.join(texts),
                 proposed_translations=' | '.join(r['existing_proposed_translation'] for r in rr),
                 signs='; '.join(sorted(signs)), sign440_present='440' in signs, sign690_present='690' in signs,
                 independently_identified_contents='', recovered_photos='; '.join(photos),
                 missing_join_reason='' if rr else 'No exact CISI transcription in the existing Lipi metadata/reading catalogue; absence of target signs cannot be inferred.')
        objects.append(o)
        for r in rr:
            faces.append(dict(cisi=ref, face_id=r['face_id'], object_identifier=r['object_identifier'],
                              container=o['container'], context=o['context'], published_impressions=o['published_impressions'],
                              sign_sequence=r['sign_sequence'], complete=r['intact_as_recorded'],
                              existing_proposed_translation=r['existing_proposed_translation'],
                              current_frozen_meanings=r['current_163_key_literal_meanings'],
                              recorded_findspot=r['found_at'], source_recorded_strata=r['recorded_stratigraphy'],
                              reading_source=r['existing_reading_source'], reading_validated=r['reading_validated'],
                              published_die_groups_on_object=o['published_die_groups'],
                              die_assignment_status='Object-level membership only; individual faces not assigned to a die on multistamp objects.'))
    # A row with an old same-die relative is not a wholly unseen physical seal.
    by_id = {r['cisi']: r for r in objects}
    group_old = {g: any(by_id[m['cisi']]['prior_specific_backing_evidence'] for m in members if m['published_die_group'] == g) for g in GROUPS}
    for o in objects:
        groups = die_by_ref[o['cisi']]
        o['same_published_die_as_prior_evidence'] = any(group_old[g] for g in groups)
        complete_texts = {r['sign_sequence'] for r in readings[o['cisi']] if r['intact_as_recorded'] == 'True' and '000' not in r['sign_sequence']}
        old_texts = {r['sign_sequence'] for other in objects if other['prior_specific_backing_evidence'] for r in readings[other['cisi']] if r['intact_as_recorded'] == 'True' and '000' not in r['sign_sequence']}
        o['same_complete_text_as_prior_evidence'] = bool(complete_texts & old_texts)
        o['new_to_recorded_backings_after_known_die_and_text_exclusions'] = (
            o['newly_supplied_backing_label'] and not o['same_published_die_as_prior_evidence'] and not o['same_complete_text_as_prior_evidence'])
        o['independence_status'] = 'Unlinked is not proven independent; damaged texts and unidentified dies may conceal duplicates.'
    write('all_93_sealings.csv', objects)
    write('all_existing_face_readings.csv', faces)
    write('missing_transcriptions.csv', [r for r in objects if not r['corpus_joined']])
    return objects, faces, group_old


def summarize(objects, faces, members, group_old):
    categories = []
    for c in CATEGORIES:
        rr = [r for r in objects if r['container'] == c]
        categories.append(dict(container=c, source_objects=len(rr), corpus_joined_objects=sum(r['corpus_joined'] for r in rr),
                               missing_transcriptions=sum(not r['corpus_joined'] for r in rr),
                               newly_supplied_labels=sum(r['newly_supplied_backing_label'] for r in rr),
                               warehouse=sum(r['context'] == 'warehouse' for r in rr),
                               other_context=sum(r['context'] == 'other_context' for r in rr),
                               unknown_context=sum(r['context'] == 'unknown_context' for r in rr)))
    write('category_coverage.csv', categories)
    by_id = {r['cisi']: r for r in objects}
    dies = []
    for g in GROUPS:
        refs = [r['cisi'] for r in members if r['published_die_group'] == g]
        rr = [by_id[ref] for ref in refs]
        diagnostic = sorted({r['container'] for r in rr} - {'undiagnostic', 'other_types'})
        texts = sorted({f['sign_sequence'] for f in faces if f['cisi'] in refs})
        singles = [r['cisi'] for r in rr if r['published_impressions'] == 1]
        single_texts = sorted({f['sign_sequence'] for f in faces if f['cisi'] in singles})
        dies.append(dict(published_die_group=g, source_sealings=len(refs), joined_sealings=sum(r['corpus_joined'] for r in rr),
                         diagnostic_use_categories='; '.join(diagnostic), diagnostic_category_count=len(diagnostic),
                         source_objects='; '.join(refs), prior_evidence_in_group=group_old[g],
                         single_impression_objects='; '.join(singles),
                         transcriptions_from_single_impression_objects=' | '.join(single_texts),
                         all_transcriptions_on_member_objects_not_die_assigned=' | '.join(texts),
                         attribution='Published Frenez 2020 seal grouping, not a new die discovery or contents identification.'))
    write('published_die_use_summary.csv', dies)
    predictions = []
    for sign, meaning, positive in [('440', 'literal vessel (frozen key: goblet/corner)', {'pottery_jar'}),
                                     ('690', 'narrow storehouse (frozen key: bundle/store)', {'pegs_on_wall', 'locker'})]:
        target = [r for r in objects if sign in r['signs'].split('; ')]
        predictions.append(dict(sign=sign, proposed_meaning=meaning, positive_use_categories='; '.join(sorted(positive)),
                                source_rows=len(objects), objects_with_joined_text=sum(r['corpus_joined'] for r in objects),
                                sign_bearing_joined_objects=len(target),
                                target_objects='; '.join(r['cisi'] for r in target),
                                missing_transcription_objects=sum(not r['corpus_joined'] for r in objects),
                                test_run=False, p_value='',
                                reason='No sign-bearing exposure among joined objects; missing transcriptions remain unknown.' if not target else 'Evaluate independence and complete text before scoring.'))
    write('fixed_prediction_eligibility.csv', predictions)
    summary = dict(source_sealings=len(objects), source_impressions=sum(r['published_impressions'] for r in objects),
                   corpus_joined_objects=sum(r['corpus_joined'] for r in objects), existing_encoded_faces=len(faces),
                   missing_transcription_objects=sum(not r['corpus_joined'] for r in objects),
                   new_backing_labels=sum(r['newly_supplied_backing_label'] for r in objects),
                   old_specific_backing_evidence=sum(r['prior_specific_backing_evidence'] for r in objects),
                   newly_labelled_joined_objects=sum(r['newly_supplied_backing_label'] and r['corpus_joined'] for r in objects),
                   unlinked_new_label_rows=sum(r['new_to_recorded_backings_after_known_die_and_text_exclusions'] for r in objects),
                   unlinked_new_label_joined_rows=sum(r['new_to_recorded_backings_after_known_die_and_text_exclusions'] and r['corpus_joined'] for r in objects),
                   published_repeated_die_groups=len(dies), published_die_memberships=len(members),
                   objects_in_repeated_die_matrix=len({r['cisi'] for r in members}),
                   groups_spanning_multiple_diagnostic_support_types=sum(r['diagnostic_category_count'] > 1 for r in dies),
                   context_counts=dict(collections.Counter(r['context'] for r in objects)),
                   impression_count_join_discrepancies=sum(not r['impression_count_equals_encoded_faces'] for r in objects if r['corpus_joined']),
                   independent_contents_labels=0, primary_hypothesis_tests_run=0,
                   sign440_joined_objects=predictions[0]['sign_bearing_joined_objects'],
                   sign690_joined_objects=predictions[1]['sign_bearing_joined_objects'],
                   colab_units=0,
                   scope='New archaeological label joins, not 93 new inscriptions. Repeated dies and missing texts limit independent validation.')
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary, categories, dies, predictions


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source = read(INPUT / 'containers.csv')
    assert [r['cisi'] for r in source] == [f'L-{i}' for i in range(124, 217)]
    checks = verify_source_cells(source)
    matrix, members = repeated_dies()
    assert len(checks) == 93 and len(matrix) == 46
    objects, faces, group_old = join(source, members)
    for r in matrix:
        assert sum(r[g] for g in GROUPS) <= int(next(o['impressions'] for o in source if o['cisi'] == r['cisi']))
    summary, categories, dies, predictions = summarize(objects, faces, members, group_old)
    # Reporting is separate so extraction and source checks can run on their own.
    from lothal_tables_report import report
    report(summary, categories, dies, predictions, objects, faces)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
