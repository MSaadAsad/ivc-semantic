"""Additional-vessel comparison with an unchanged metrology parser and fixed units.

The statistical unit is a physical vessel, not each source, profile or face.
Only one additional vessel has an independently labelled interior profile here.
"""
import argparse
import ast
import base64
import csv
import hashlib
import html
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
OUT = BASE / 'results'
CATALOGUE = BASE.parent / 'translation_catalogue/results/all_inscriptions.csv'


def read_csv(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def write_csv(name, rows):
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def inherited_parser():
    """Compile only selected pure definitions: do not import modules/write old logs."""
    namespace = {}
    wanted = {'NUM_CATALOG', 'PURE_NUMS', 'OPENER_SIGNS', 'parse_num_runs', 'pot_capacity_equiv'}
    found = set()
    for filename in ['met_common.py', 'met_03_physical.py']:
        path = REPO / 'work_scripts' / filename
        for node in ast.parse(path.read_text()).body:
            name = None
            if isinstance(node, ast.FunctionDef):
                name = node.name
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
            if name in wanted:
                exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
                found.add(name)
    assert found == wanted
    return namespace['pot_capacity_equiv']


def frustum_volume(r0, r1, height):
    """Cubic centimetres, exact for a linearly changing circular radius."""
    return math.pi * height * (r0*r0 + r0*r1 + r1*r1) / 3


def geometry(trace, radial_px=0, scale_px=0, vertical=1):
    (xa, ya), (xb, yb) = trace['axis_endpoints_px']
    (sx0, sy0), (sx1, sy1) = trace['scale_endpoints_px']
    cm_per_px = trace['scale_cm'] / (math.hypot(sx1-sx0, sy1-sy0) + scale_px)
    wall = trace['inner_wall_y_x_px']
    assert all(y1 > y0 for (y0, _), (y1, _) in zip(wall, wall[1:]))
    floor_y = wall[-1][0]
    profile = []
    # Reverse: internal floor first, mouth last, giving increasing fill height.
    for y, x in reversed(wall):
        axis = xa + (xb-xa) * (y-ya) / (yb-ya)
        radius = max(0, axis-x+radial_px) * cm_per_px
        height = (floor_y-y) * cm_per_px * vertical
        profile.append((height, radius))
    return profile


def volume(profile, fill_height=None):
    """Litres below a specified height; no extrapolated tip or generic shape factor."""
    if fill_height is None:
        fill_height = profile[-1][0]
    total = 0
    for (h0, r0), (h1, r1) in zip(profile, profile[1:]):
        if fill_height <= h0:
            break
        end = min(h1, fill_height)
        r_end = r0 + (r1-r0) * (end-h0) / (h1-h0)
        total += frustum_volume(r0, r_end, end-h0)
    return total / 1000


def check_math():
    assert math.isclose(frustum_volume(2, 2, 5), math.pi*20)
    assert math.isclose(frustum_volume(0, 3, 6), math.pi*18)
    whole = frustum_volume(2, 4, 10)
    assert math.isclose(whole, frustum_volume(2, 3, 5)+frustum_volume(3, 4, 5))
    profile = [(0, 2), (10, 4)]
    assert math.isclose(volume(profile, 5)*1000, frustum_volume(2, 3, 5))
    assert volume(profile, 0) == 0
    assert volume(profile, 5) < volume(profile)
    assert math.isclose(volume([(h*2, r*2) for h, r in profile]), 8*volume(profile))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-pdf', type=Path, help='Optional primary Kenoyer PDF for an auditable source-overlay figure')
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    check_math()
    trace = json.loads((BASE / 'inputs/h95_profile_trace.json').read_text())
    source_inventory = read_csv(BASE / 'inputs/fuls2012_inventory.csv')
    parser = inherited_parser()
    catalogue = [r for r in read_csv(CATALOGUE) if r['catalogue'] == 'Lipi']
    by_object = defaultdict(list)
    by_ref = defaultdict(list)
    for r in catalogue:
        by_ref[r['reference']].append(r)
        if r['object_type'].startswith('POT'):
            by_object[r['object_identifier']].append(r)

    screen = []
    for object_id, faces in by_object.items():
        faces.sort(key=lambda r: r['face_id'])
        tokens = [tuple(r['sign_sequence'].split('-')) for r in faces]
        first = faces[0]
        original_domain = first['object_type'] == 'POT:T:g'
        cups, basis = parser(tokens) if original_domain else (None, 'outside_original_POT:T:g_domain')
        screen.append(dict(
            object_identifier=object_id, reference=first['reference'], site=first['city'],
            object_type=first['object_type'], original_parser_domain=original_domain,
            face_ids='|'.join(r['face_id'] for r in faces),
            face_sequences=' | '.join(r['sign_sequence'] for r in faces),
            existing_proposed_readings=' | '.join(r['existing_proposed_translation'] for r in faces),
            catalogue_preservation=first['preservation'],
            excavation_number=first['excavation_number'], found_at=first['found_at'],
            cup_equivalents='' if cups is None else cups,
            parser_basis=basis or '',
            predicted_full_capacity_l='' if cups is None else cups*9.24,
            geometry_available_here=first['reference'] == 'H-2263',
            caution='A catalogue complete label is not independent proof of a surviving whole vessel. Parsing is a proposal, not a measured capacity.',
        ))
    write_csv('all_pottery_prediction_screen.csv', screen)
    assert len(screen) == 629
    assert sum(len(v) for v in by_object.values()) == 635
    screen_ref = {r['reference']: r for r in screen}
    assert screen_ref['H-2263']['cup_equivalents'] == 4
    assert screen_ref['K-90']['cup_equivalents'] == 1  # Bare cup face wins before rim face.
    assert parser([('032',), ('700', '798', '740')])[0] == 2  # Document order sensitivity.
    assert screen_ref['M-2063']['cup_equivalents'] == ''
    assert screen_ref['M-2061']['cup_equivalents'] == ''

    joined_inventory = []
    for s in source_inventory:
        matches = by_ref[s['catalogue_reference']] if s['catalogue_reference'] else []
        prediction = screen_ref.get(s['catalogue_reference'], {})
        joined_inventory.append({**s,
            'catalogue_face_ids': '|'.join(r['face_id'] for r in matches),
            'existing_proposed_readings': ' | '.join(r['existing_proposed_translation'] for r in matches),
            'catalogue_found_at': ' | '.join(dict.fromkeys(r['found_at'] for r in matches)),
            'inherited_parser_cup_equivalents': prediction.get('cup_equivalents', ''),
            'inherited_prediction_l': prediction.get('predicted_full_capacity_l', ''),
            'primary_additional_capacity_comparison': s['source_vessel_id'] == 'H95-2661',
        })
    write_csv('eight_vessel_source_inventory.csv', joined_inventory)
    assert len(joined_inventory) == 8
    assert sum(r['prior_role'] == 'additional' for r in joined_inventory) == 5
    assert not [r for r in joined_inventory if r['source_vessel_id'] == 'MD-1374'][0]['catalogue_face_ids']

    profile = geometry(trace)
    observed = volume(profile)
    predictions = [
        ('repo_fixed_9.24', 4, 9.24),
        ('repo_calibration_array_mean', 4, sum([27.30/3, 55.56/6, 65.89/7])/3),
        ('later_Wells2015_40.4', 4, 40.4),
        ('alternative_3_strokes_repo', 3, 9.24),
        ('alternative_3_strokes_later_Wells', 3, 40.4),
    ]
    comparisons = [dict(model=model, strokes=count, unit_litres=unit,
                        predicted_litres=count*unit, reconstructed_rim_capacity_litres=observed,
                        actual_over_predicted=observed/(count*unit),
                        predicted_minus_reconstructed_litres=count*unit-observed)
                   for model, count, unit in predictions]
    write_csv('h95_fixed_predictions.csv', comparisons)
    s = trace['sensitivity']
    scenarios = [dict(radial_offset_px=r, scale_length_offset_px=sc, vertical_multiplier=v,
                      capacity_litres=volume(geometry(trace, r, sc, v)))
                 for r, sc, v in itertools.product(s['radial_offset_px'], s['scale_length_offset_px'], s['vertical_multiplier'])]
    write_csv('h95_geometry_sensitivity.csv', scenarios)
    fills = [dict(fraction_of_internal_height=f, fill_height_cm=f*profile[-1][0],
                  litres=volume(profile, f*profile[-1][0])) for f in trace['fill_fractions_of_interior_height']]
    write_csv('h95_fill_levels.csv', fills)
    # Quantify the post-hoc partial-fill explanation, without calling it a prediction.
    low, high = 0, profile[-1][0]
    for _ in range(60):
        mid = (low+high)/2
        if volume(profile, mid) < 36.96:
            low = mid
        else:
            high = mid
    sensitivity_min = min(r['capacity_litres'] for r in scenarios)
    sensitivity_max = max(r['capacity_litres'] for r in scenarios)
    assert sensitivity_min > 36.96 and sensitivity_max < 161.6
    calibration = []
    repo_values = {'H-372': 27.30, 'H-371': 55.56, 'H-370': 65.89}
    for r in source_inventory:
        if r['prior_role'] == 'original_calibration':
            source_value = float(r['source_volume_l'])
            n = int(r['source_strokes'])
            calibration.append(dict(reference=r['source_vessel_id'], strokes=n,
                                    repo_news_derived_litres=repo_values[r['source_vessel_id']],
                                    fuls2012_reported_profile_litres=source_value,
                                    source_reported_litres_per_stroke=source_value/n,
                                    caution='Same old objects; table recovered as author-posted text, not a visually verified PDF table.'))
    write_csv('original_calibration_source_comparison.csv', calibration)
    summary = dict(
        pottery_faces_screened=635, pottery_objects_screened=629,
        objects_given_numeric_parser_prediction=sum(r['cup_equivalents'] != '' for r in screen),
        source_vessels_recovered=8, original_calibration_objects=3, additional_source_vessels=5,
        additional_vessels_with_labelled_interior_profile=1,
        additional_vessels_with_primary_numeric_comparison=1,
        primary_reference='H-2263 (drawing H95-2661/6640-501; caption H95-2662)',
        profile_reconstructed_litres=observed, predicted_repo_litres=36.96,
        predicted_later_wells_litres=161.6,
        actual_over_repo_prediction=observed/36.96,
        trace_sensitivity_litres=[sensitivity_min, sensitivity_max],
        broad_10_percent_linear_scale_sensitivity_litres=[observed*0.9**3, observed*1.1**3],
        implied_unit_if_four_strokes_litres=observed/4,
        original_trace_before_contour_review_litres=volume(geometry({**trace, 'inner_wall_y_x_px': trace['superseded_initial_trace_y_x_px']})),
        source_reported_fuls_h95_litres=88.3,
        internal_height_cm=profile[-1][0],
        partial_fill_to_equal_36_96_litres_height_fraction=((low+high)/2)/profile[-1][0],
        parser_K90_cups_original_face_order=1, parser_K90_cups_reversed_face_order=2,
        statistical_significance_tests_run=0,
        independent_direct_liquid_measurements_made=0,
        blinded=False,
        finding='The fixed9.24L/stroke full-capacity prediction mismatches this additional scaled profile. The proposed Dravidian language is not identified or excluded.',
    )
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')

    e = lambda x: html.escape(str(x))
    # Scientific overlay: trace, axis and labelled scale on a cropped source figure.
    background = ''
    if args.source_pdf:
        assert hashlib.sha256(args.source_pdf.read_bytes()).hexdigest() == trace['source_pdf_sha256']
        import fitz
        from PIL import Image
        import io
        doc = fitz.open(args.source_pdf)
        raw = doc.extract_image(trace['image_xref'])['image']
        image = Image.open(io.BytesIO(raw)).convert('RGB').crop((8, 182, 458, 775))
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        background = '<image x="8" y="182" width="450" height="593" href="data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()+'"/>'
    points = ' '.join(f'{x},{y}' for y, x in trace['inner_wall_y_x_px'])
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 175 470 620"><rect x="0" y="175" width="470" height="620" fill="white"/>'+background+'<polyline points="'+points+'" fill="none" stroke="#d63a20" stroke-width="2.5"/><line x1="237" y1="240" x2="231" y2="745" stroke="#1469b2" stroke-width="2"/><line x1="68" y1="422" x2="217" y2="422" stroke="#26843d" stroke-width="3"/><text x="16" y="790" font-family="sans-serif" font-size="11">Kenoyer Fig7.2; red: inner wall; blue: axis; green:20cm scale</text></svg>'
    if args.source_pdf or not (OUT / 'h95_profile_overlay.svg').exists():
        (OUT / 'h95_profile_overlay.svg').write_text(svg)

    bars = [(36.96, 'Repo prediction: 4 × 9.24 L', '#aa4630'),
            (observed, 'Reconstructed interior capacity', '#2c7569'),
            (161.6, 'Later Wells unit: 4 × 40.4 L', '#7a699f')]
    chart = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 285"><rect width="740" height="285" fill="#fff"/><text x="22" y="30" font-size="20" font-family="sans-serif">One additional jar: prediction versus geometry</text>'
    for i, (value, label, color) in enumerate(bars):
        y = 65+i*70
        chart += f'<text x="22" y="{y}" font-family="sans-serif" font-size="15">{e(label)}</text><rect x="22" y="{y+8}" width="{value*3.7:.1f}" height="25" fill="{color}"/><text x="{35+value*3.7:.1f}" y="{y+27}" font-family="sans-serif" font-size="16">{value:.1f}L</text>'
    chart += '</svg>'
    (OUT / 'h95_capacity_comparison.svg').write_text(chart)

    inventory_rows = ''.join('<tr>'+''.join('<td>'+e(r[k])+'</td>' for k in ['source_vessel_id','catalogue_reference','source_volume_l','source_strokes','existing_proposed_readings','eligibility_note'])+'</tr>' for r in joined_inventory)
    calibration_rows = ''.join(f'<tr><td>{e(r["reference"])}</td><td>{r["repo_news_derived_litres"]:.2f}</td><td>{r["fuls2012_reported_profile_litres"]:.1f}</td></tr>' for r in calibration)
    report = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Additional inscribed-jar capacity check</title><style>
body{{margin:0;background:#f4f4ee;color:#213237;font:16px/1.6 system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:30px}}h1{{font-size:35px;line-height:1.2;max-width:1000px}}h2{{margin-top:38px}}.intro{{max-width:960px}}.result{{padding:18px 24px;background:#e2ece6;border-left:5px solid #367569}}.figures{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.35fr);gap:26px;align-items:start;margin-top:25px}}img{{max-width:100%;height:auto;background:white}}figure{{margin:0}}figcaption{{font-size:14px;color:#4c5f63}}table{{width:100%;border-collapse:collapse;background:white}}td,th{{padding:13px;text-align:left;vertical-align:top;border:1px solid #d4ddda}}th{{background:#2b4549;color:white}}.scroll{{overflow:auto}}a{{color:#156580}}small{{color:#53696d}}@media(max-width:760px){{.figures{{grid-template-columns:1fr}}main{{padding:20px}}h1{{font-size:29px}}}}</style><main>
<h1>The additional jar reconstructs to about {observed:.0f} litres. The repo's fixed rule predicts 37 litres.</h1>
<div class="intro"><p>22 November 2026 · A source-linked, reproducible geometric comparison. One additional vessel supplies the primary test; the complete eight-vessel published inventory remains visible.</p>
<div class="result"><b>This weakens the fixed 9.24 L-per-stroke interpretation of full jar capacity.</b> It does not establish whether the marks record quantities placed in the jar, different units, something else, or a particular language.</div>
<p>The jar drawing is labelled <b>H95-2661/6640-501</b>, matching the catalogue accession prefix for <b>H-2263</b>. Its caption instead says 2662, and the catalogue's unit string differs. These discrepancies are retained. The rim reading is <b>4</b>; the drawing also shows separate body graffiti and potter's marks.</p><p>The fixed prediction is <b>4 × 9.24 = 36.96 L</b>, compared with <b>{observed:.2f} L</b> reconstructed from the interior drawing.</p></div>
<div class="figures"><figure><img src="h95_profile_overlay.svg" alt="Traced inner wall, axis and20cm scale on Kenoyer's published jar drawing"><figcaption>Published inner profile, not outer height×width. Trace coordinates, the superseded first trace and the source caption conflict are released. Prior published capacities were already known; this is not blind replication.</figcaption></figure><figure><img src="h95_capacity_comparison.svg" alt="37L repo prediction, approximately89L reconstructed capacity,162L later Wells prediction"><p><b>Geometry sensitivity:</b> {sensitivity_min:.1f}–{sensitivity_max:.1f} L across 27 combinations of ±3px radius, ±2px scale-bar length and ±2% vertical scaling. This is an analyst-selected range, not a confidence interval.</p><p><b>Broader size sensitivity:</b> changing all linear dimensions by ±10% gives {observed*0.9**3:.1f}–{observed*1.1**3:.1f} L. The 37 L prediction remains below that range.</p><p><b>Partial filling:</b> 37 L is about {36.96/observed:.0%} of reconstructed capacity. It could fit inside the jar; no fill mark or prior fill-level rule establishes that this was the intended reading.</p></figure></div>
<h2>The original calibration needs correction</h2><div class="intro"><p>The repo's 9.24 L/stroke anchor comes from an older news summary. Wells's 2015 primary account instead reports about <b>40.4 L per tall stroke</b>. Fuls 2012 also reports roughly40L/stroke for the same three old jars. Those are repeated analyses of the calibration objects, not three new test vessels.</p></div>
<table><thead><tr><th>Original jar</th><th>Repo's news-derived litres</th><th>Fuls's reported profile litres</th></tr></thead><tbody>{calibration_rows}</tbody></table><p><small>Fuls table cells were recovered from author-posted public text, not a visually verified PDF table. Wells's 2015 running text independently states the later 40.4 L unit. No reason for the older discrepancy has been established here.</small></p>
<h2>All eight source vessels, including every exclusion</h2><p>Five are additional to the original three. Only the H95 jar currently combines an identified inscription, numeric interpretation and independently labelled interior profile. K-90's two rim strokes were checked in the catalogue photograph, but its scale units are unlabelled. MD-1374 is not silently equated with CISI M-1374. The two Mackay pots have complex readings, not an established1-unit capacity inscription.</p>
<div class="scroll"><table><thead><tr><th>Source ID</th><th>Catalogue link</th><th>Published litres</th><th>Source count</th><th>Existing proposed reading</th><th>Eligibility / caveat</th></tr></thead><tbody>{inventory_rows}</tbody></table></div>
<h2>What ran</h2><p>The unchanged parser was screened against 635 pottery faces on 629 catalogue objects. It produces numerical candidates for {summary['objects_given_numeric_parser_prediction']} objects; this is not a count of measured vessels. K-90 exposes a face-order issue: the code returns 1 cup from its body face, but 2 if the rim face is processed first. No new cross-face interpretation is presented as a confirmed reading.</p>
<p>There is one additional geometric comparison, zero significance tests and zero direct liquid measurements. The inherited three-jar result, source reports and new trace are not pooled as independent observations.</p>
<p><a href="../README.md">Interpretation and reproduction</a> · <a href="../SOURCES.md">Sources, access and prior work</a> · <a href="h95_fixed_predictions.csv">Fixed predictions</a> · <a href="h95_geometry_sensitivity.csv">All 27 sensitivity scenarios</a> · <a href="all_pottery_prediction_screen.csv">All 629 pottery candidates</a> · <a href="eight_vessel_source_inventory.csv">Complete source inventory</a></p></main></html>'''
    (OUT / 'capacity.html').write_text(report)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
