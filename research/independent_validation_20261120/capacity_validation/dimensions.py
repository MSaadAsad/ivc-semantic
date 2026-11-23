"""Compare explicit vessel-length/area/volume hypotheses on the same mark counts.

All models have one scale, no intercept, and predict the held-out object's count.
External cloth/land accounts have no measured endpoint in these inputs and are not scored.
"""
import csv
import gzip
import html
import io
import itertools
import json
import math
import statistics
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / 'results'
MODELS = ['diameter_length', 'circular_section_area', 'interior_volume']
LABELS = {'diameter_length': 'Width / circumference', 'circular_section_area': 'Widest cross-section area',
          'interior_volume': 'Interior capacity', 'external_height': 'External height',
          'cylinder_side_area': 'Bounding-cylinder side area'}


def read(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    data = stream.getvalue().encode()
    if name.endswith('.gz'):
        data = gzip.compress(data, mtime=0)
    (OUT / name).write_bytes(data)


def quantity(row, model):
    d = row['diameter_cm']
    if model == 'diameter_length': return d
    if model == 'circular_section_area': return math.pi*d*d/4
    if model == 'interior_volume': return row['volume_l']
    if model == 'external_height': return row['height_cm']
    if model == 'cylinder_side_area': return math.pi*d*row['height_cm']
    raise ValueError(model)


def fit_unit(rows, model):
    return math.exp(statistics.mean(math.log(quantity(r, model)/r['count']) for r in rows))


def folds(rows, model, scope):
    result = []
    for i, target in enumerate(rows):
        train = rows[:i]+rows[i+1:]
        unit = fit_unit(train, model)
        actual_q = quantity(target, model)
        predicted_n = actual_q/unit
        error = predicted_n-target['count']
        assert target['id'] not in {r['id'] for r in train}
        result.append(dict(scope=scope, model=model, target=target['id'],
                           train_ids='|'.join(r['id'] for r in train),
                           actual_count=target['count'], actual_quantity=actual_q,
                           fitted_quantity_per_mark=unit, predicted_count=predicted_n,
                           predicted_quantity_from_actual_count=unit*target['count'],
                           absolute_count_error=abs(error),
                           absolute_percentage_count_error=100*abs(error)/target['count'],
                           log_count_error=math.log(predicted_n/target['count'])))
    return result


def scores(fold_rows):
    return dict(n=len(fold_rows),
                log_rmse=math.sqrt(statistics.mean(r['log_count_error']**2 for r in fold_rows)),
                mean_absolute_count_error=statistics.mean(r['absolute_count_error'] for r in fold_rows),
                mean_absolute_percentage_count_error=statistics.mean(r['absolute_percentage_count_error'] for r in fold_rows))


def check_engine():
    for correct, exponent in [('diameter_length', 1), ('circular_section_area', 0.5), ('interior_volume', 1/3)]:
        rows = [dict(id=str(n), count=n, diameter_cm=10*n**exponent,
                     volume_l=math.pi*(10*n**exponent)**3/6000) for n in [1, 2, 3, 4]]
        assert scores(folds(rows, correct, 'synthetic'))['log_rmse'] < 1e-12
        for model in MODELS:
            if model != correct:
                assert scores(folds(rows, model, 'synthetic'))['log_rmse'] > 0.1
        scaled = [{**r, 'diameter_cm': r['diameter_cm']*10, 'volume_l': r['volume_l']*1000} for r in rows]
        for model in MODELS:
            a = folds(rows, model, 'units')
            b = folds(scaled, model, 'units')
            assert all(math.isclose(x['predicted_count'], y['predicted_count'], rel_tol=1e-12) for x, y in zip(a, b))


def main():
    OUT.mkdir(exist_ok=True)
    check_engine()
    dimensions = read(BASE / 'inputs/vessel_dimensions.csv')
    source = {r['source_vessel_id']: r for r in read(BASE / 'inputs/fuls2012_inventory.csv')}
    h95 = json.loads((OUT / 'summary.json').read_text())
    assert {r['source_vessel_id'] for r in dimensions} == set(source)
    rows, exclusions = [], []
    for r in dimensions:
        identifier = r['source_vessel_id']
        if '?' in r['count']:
            exclusions.append(dict(id=identifier, reason='Uncertain numerical reading1?; not scored', source=r['source_locator']))
            continue
        rows.append(dict(id=identifier, count=int(r['count']),
                         diameter_cm=float(r['maximum_external_diameter_cm']),
                         height_cm=float(r['external_height_cm']) if r['external_height_cm'] else None,
                         volume_l=h95['profile_reconstructed_litres'] if identifier == 'H95-2661' else float(source[identifier]['source_volume_l']),
                         primary=r['primary_four_case'] == 'True',
                         count_class=r['count_class'], scale=r['absolute_scale'], source=r['source_locator']))
    primary = [r for r in rows if r['primary']]
    original = [r for r in primary if r['id'] != 'H95-2661']
    mixed = primary+[r for r in rows if r['id'] == 'MD-1374']
    photo = mixed+[r for r in rows if r['id'] == 'K-90']
    heights = [r for r in primary if r['height_cm'] is not None]
    assert len(primary) == 4 and len(original) == 3 and len(heights) == 3
    assert len(exclusions) == 2
    assert next(r for r in rows if r['id'] == 'H-372')['height_cm'] is None
    assert {r['count'] for r in primary} == {3, 4, 6, 7}
    write('dimension_eligible_measurements.csv', rows)
    write('dimension_excluded_readings.csv', exclusions)

    all_folds, aggregates = [], []
    groups = [('primary_four', primary, MODELS), ('original_three_selected', original, MODELS),
              ('mixed_stroke_five_conditional', mixed, MODELS), ('photo_scale_six_conditional', photo, MODELS),
              ('known_height_three', heights, MODELS+['external_height', 'cylinder_side_area'])]
    for scope, group, models in groups:
        for model in models:
            f = folds(group, model, scope)
            all_folds += f
            aggregates.append(dict(scope=scope, model=model, **scores(f)))
    assert len(all_folds) == 69
    write('dimension_predictions_all_folds.csv', all_folds)
    write('dimension_model_scores.csv', aggregates)
    baseline = []
    for i, target in enumerate(primary):
        train = primary[:i]+primary[i+1:]
        predicted = math.exp(statistics.mean(math.log(r['count']) for r in train))
        baseline.append(dict(scope='primary_four', model='constant_count_baseline',
                             target=target['id'], train_ids='|'.join(r['id'] for r in train),
                             actual_count=target['count'], predicted_count=predicted,
                             absolute_count_error=abs(predicted-target['count']),
                             absolute_percentage_count_error=100*abs(predicted-target['count'])/target['count'],
                             log_count_error=math.log(predicted/target['count'])))
    baseline_score = scores(baseline)
    write('dimension_constant_baseline.csv', baseline)
    target_predictions = [r for r in all_folds if r['scope'] == 'primary_four' and r['target'] == 'H95-2661']
    write('dimension_h95_predictions.csv', target_predictions)

    # Coherent linear-scale scenarios, crossed with reported volume-model/trace choices.
    # These are stress configurations, not random draws or confidence probabilities.
    volume_choices = {'H-372': [123.6, 118.8, 121.0], 'H-371': [248.7, 259.1, 240.6],
                      'H-370': [292.9, 282.7, 283.8],
                      'H95-2661': [h95['trace_sensitivity_litres'][0], h95['profile_reconstructed_litres'], h95['trace_sensitivity_litres'][1]]}
    stress, winners = [], Counter()
    for scale_choice in itertools.product([0.98, 1.0, 1.02], repeat=4):
        for vol_choice in itertools.product(range(3), repeat=4):
            altered = [{**r, 'diameter_cm': r['diameter_cm']*s,
                        'volume_l': volume_choices[r['id']][v]*s**3}
                       for r, s, v in zip(primary, scale_choice, vol_choice)]
            errors = {model: scores(folds(altered, model, 'stress'))['log_rmse'] for model in MODELS}
            winner = min(errors, key=errors.get)
            winners[winner] += 1
            stress.append(dict(scenario=len(stress)+1, scale_by_object='|'.join(map(str, scale_choice)),
                               volume_choice_by_object='|'.join(map(str, vol_choice)),
                               winner=winner, **errors))
    assert len(stress) == 6561
    write('dimension_stress_scenarios.csv.gz', stress)
    primary_scores = [r for r in aggregates if r['scope'] == 'primary_four']
    primary_winner = min(primary_scores, key=lambda r: r['log_rmse'])['model']
    winner_by_scope = {scope: min((r for r in aggregates if r['scope'] == scope), key=lambda r: r['log_rmse'])['model']
                       for scope, _, _ in groups}
    # Report the numerical range of each property as a limitation on a common unit.
    unit_ranges = {model: [min(quantity(r, model)/r['count'] for r in primary),
                          max(quantity(r, model)/r['count'] for r in primary)] for model in MODELS}
    summary = dict(primary_objects=4, original_selected_objects=3, conditional_extra_objects=2,
                   uncertain_readings_excluded=2, primary_models=3, primary_folds=12,
                   all_scope_folds=len(all_folds), primary_score='root mean squared log-count prediction error',
                   primary_winner=primary_winner, winner_by_scope=winner_by_scope,
                   primary_scores=primary_scores, h95_predictions=target_predictions,
                   primary_constant_baseline=baseline_score,
                   quantity_per_mark_ranges=unit_ranges,
                   stress_scenarios=len(stress), stress_winner_counts=dict(winners),
                   stress_counts_are_probabilities=False,
                   external_cloth_or_land_account_tests_run=0,
                   external_account_unit_identified=False,
                   significance_tests_run=0,
                   conclusion='Vessel section-area fits the four-case panel better than capacity, while width best predicts H95. Results depend on scope and do not identify the dimension of an external account or a language.')
    (OUT / 'dimension_summary.json').write_text(json.dumps(summary, indent=2)+'\n')

    e = lambda x: html.escape(str(x))
    human = lambda x: e(str(x).replace('_', ' '))
    # Plot count predictions on a common response scale, all four objects retained.
    colors = {'diameter_length': '#317cb0', 'circular_section_area': '#a47722', 'interior_volume': '#557c51'}
    chart = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 440"><rect width="860" height="440" fill="white"/>'
    chart += '<text x="25" y="30" font-family="sans-serif" font-size="21">Predicting each jar’s marks from the other three</text>'
    left, top, width, height = 65, 58, 540, 305
    xx = lambda n: left+n/10*width
    yy = lambda n: top+height-n/10*height
    for tick in range(0, 11, 2):
        chart += f'<path d="M {xx(tick)} {top} V {top+height} M {left} {yy(tick)} H {left+width}" stroke="#e0e5e2"/>'
        chart += f'<text x="{xx(tick)}" y="{top+height+21}" text-anchor="middle" font-family="sans-serif" font-size="13">{tick}</text><text x="{left-12}" y="{yy(tick)+4}" text-anchor="end" font-family="sans-serif" font-size="13">{tick}</text>'
    chart += f'<line x1="{xx(0)}" y1="{yy(0)}" x2="{xx(10)}" y2="{yy(10)}" stroke="#7b878a" stroke-dasharray="5 5"/>'
    for model in MODELS:
        for r in all_folds:
            if r['scope'] != 'primary_four' or r['model'] != model: continue
            x, y = xx(r['actual_count']), yy(r['predicted_count'])
            chart += f'<circle cx="{x}" cy="{y}" r="{7 if r["target"] == "H95-2661" else 5}" fill="{colors[model]}" stroke="white"><title>{e(r["target"])}; {e(LABELS[model])}: actual {r["actual_count"]}, predicted {r["predicted_count"]:.2f}</title></circle>'
        i = MODELS.index(model)
        chart += f'<circle cx="635" cy="{100+i*45}" r="6" fill="{colors[model]}"/><text x="650" y="{105+i*45}" font-family="sans-serif" font-size="14">{e(LABELS[model])}</text>'
    chart += '<text x="330" y="410" text-anchor="middle" font-family="sans-serif" font-size="16">Actual number of marks</text><text x="20" y="210" text-anchor="middle" transform="rotate(-90 20 210)" font-family="sans-serif" font-size="16">Predicted number of marks</text><text x="635" y="275" font-family="sans-serif" font-size="13">Larger dots: H95 jar</text><text x="635" y="300" font-family="sans-serif" font-size="13">Dashed line: exact prediction</text></svg>'
    (OUT / 'dimension_predictions.svg').write_text(chart)
    score_rows = ''.join(f'<tr><td>{e(LABELS[r["model"]])}</td><td>{r["mean_absolute_percentage_count_error"]:.1f}%</td><td>{r["mean_absolute_count_error"]:.2f} marks</td><td>{r["log_rmse"]:.3f}</td></tr>' for r in primary_scores)
    score_rows += f'<tr><td>Constant count, ignoring geometry</td><td>{baseline_score["mean_absolute_percentage_count_error"]:.1f}%</td><td>{baseline_score["mean_absolute_count_error"]:.2f} marks</td><td>{baseline_score["log_rmse"]:.3f}</td></tr>'
    target_rows = ''.join(f'<tr><td>{e(LABELS[r["model"]])}</td><td>{r["predicted_count"]:.2f}</td><td>4</td><td>{r["absolute_percentage_count_error"]:.1f}%</td></tr>' for r in target_predictions)
    data_rows = ''.join(f'<tr><td>{e(r["id"])}</td><td>{r["count"]}</td><td>{r["diameter_cm"]:.1f}cm</td><td>{r["volume_l"]:.1f}L</td><td>{human(r["count_class"])}</td><td>{human(r["scale"])}</td></tr>' for r in rows)
    scope_rows = ''.join(f'<tr><td>{human(scope)}</td><td>{len(group)}</td><td>{e(LABELS[winner_by_scope[scope]])}</td></tr>' for scope, group, _ in groups)
    stress_names = ', '.join(LABELS[k] for k in winners)
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Length, area or volume? Jar-mark comparison</title><style>body{{margin:0;background:#f3f4ee;color:#20363b;font:16px/1.6 system-ui,sans-serif}}main{{max-width:1100px;margin:auto;padding:28px}}h1{{font-size:34px;line-height:1.2}}h2{{margin-top:35px}}.intro{{max-width:980px}}.result{{padding:18px;background:#e1ebe5;border-left:5px solid #3a7868}}.limit{{padding:16px;background:#fff1dc;border-left:5px solid #ae6d2b}}.scroll{{overflow:auto}}table{{border-collapse:collapse;width:100%;background:white}}td,th{{padding:12px;border:1px solid #d1dcd5;text-align:left;vertical-align:top}}th{{background:#2d474b;color:white}}img{{width:100%;height:auto}}a{{color:#126277}}</style><main>
<h1>Could the marks measure length or area?</h1><p>22 November 2026 · An exploratory prediction comparison on four primary jars. All models predict the same thing: how many marks should be on the omitted jar.</p>
<p><a href="jar_marks_comparison.png">Illustrated one-page chart (PNG)</a> · <a href="jar_marks_comparison.svg">Scalable chart (SVG)</a>. Includes the published jar drawing, schematic mark counts, all four jars' measurements and prediction errors.</p>
<div class="result"><b>The recovered measurements do not force a volume reading.</b> Cross-section area has the lowest error across all four cases; width predicts the additional H95 jar most closely. The original selected three jars instead favor volume. This is a scope-dependent pattern, not an identified ancient unit.</div>
<div class="intro"><p><b>What “length” and “area” mean here:</b> length is the vessel's maximum width (or equivalently its circumference after a constant conversion). Area is its widest circular cross-section. These are not measurements of a textile or a field.</p><p>Each model learns one common unit from the other jars, then predicts the omitted jar's mark count. Capacity gets its own fitted unit, just as length and area do; it is not forced to use the disputed 9.24L value. Predictions remain unrounded. A one-parameter constant-count baseline ignores geometry entirely.</p></div>
<h2>All four jars: predict each from the other three</h2><div class="scroll"><table><thead><tr><th>Hypothesis</th><th>Mean percentage count error</th><th>Mean count error</th><th>Log-error score</th></tr></thead><tbody>{score_rows}</tbody></table></div>
<img src="dimension_predictions.svg" alt="Observed versus omitted-jar mark-count predictions for width, cross-section area and capacity"><p>The same four objects are used for every primary model. Lower errors indicate a closer fit under the specified common-unit assumption, not a deciphered word or a probability of truth.</p>
<h2>The additional four-mark H95 jar</h2><p>Catalogue rim sign <b>034</b> has the proposed reading <b>four</b>. The alternatives below change what quantity the count describes; they supply no new spoken word. No sign 700 cup/measure is transcribed in that rim entry; separate body marks are not transcribed there.</p><div class="scroll"><table><thead><tr><th>Model trained on original three</th><th>Predicted marks</th><th>Actual marks</th><th>Count error</th></tr></thead><tbody>{target_rows}</tbody></table></div>
<p>The linear model predicts nearly four from its width. But its unit is unstable elsewhere: the four jars imply {unit_ranges['diameter_length'][0]:.1f}–{unit_ranges['diameter_length'][1]:.1f}cm of diameter per mark. A successful H95 prediction alone does not establish a standardized ruler unit.</p>
<h2>Change the scope; the preferred model can change</h2><div class="scroll"><table><thead><tr><th>Panel</th><th>Objects</th><th>Lowest log error</th></tr></thead><tbody>{scope_rows}</tbody></table></div>
<p>The five-case panel adds MD-1374 only by treating three vertical and three oblique marks as six equivalent counts. The six-case panel also accepts K-90's assumed, unlabelled photo scale. Neither is promoted to primary evidence. The height panel uses three objects with unambiguous exterior heights and adds a bounding-cylinder side-area proxy; it is not the same four-case panel.</p>
<p>Across 6,561 analyst-selected geometry/model stress configurations, winning models include: <b>{e(stress_names)}</b>. These configurations are not probabilities or confidence intervals. All configurations are released.</p>
<div class="limit"><b>The original three jars were selected in earlier research because their volumes match their counts.</b> Their volume fit is development evidence. Four primary objects, uncertain source tables and scope changes do not establish a generally superior length/area interpretation.</div>
<h2>Every dimension-bearing source case</h2><div class="scroll"><table><thead><tr><th>Vessel</th><th>Marks</th><th>External width</th><th>Interior capacity</th><th>Count qualification</th><th>Scale qualification</th></tr></thead><tbody>{data_rows}</tbody></table></div><p>MD-63-3 and MD-63-6 remain excluded because the source's 1? is not an established numeral reading. The full eight-row source table and every prediction are linked below.</p>
<h2>What about accounts for cloth length or land area?</h2><p>Those hypotheses are <b>not tested by a jar's width or cross-section</b>. The account could refer to something outside the jar. The bounded source checks recover linear-measurement artefacts and marked bricks, but no verified pairing of one of these accounts with an independently measured cloth length or plot area. Physical graduations on a ruler do not identify the unit of a separate inscription.</p>
<p>No language, pronunciation, field-area unit or textile-length unit is identified here. The next discriminating observation must connect an account to its measured subject and specify the unit before scoring a new case.</p>
<p><a href="../DIMENSION_TEST.md">Design, scope and source checks</a> · <a href="dimension_model_scores.csv">All model scores</a> · <a href="dimension_constant_baseline.csv">Baseline predictions</a> · <a href="eight_vessel_source_inventory.csv">All eight source cases</a> · <a href="dimension_predictions_all_folds.csv">Every prediction</a> · <a href="dimension_stress_scenarios.csv.gz">All stress configurations</a> · <a href="dimension_summary.json">Summary</a> · <a href="capacity.html">Earlier capacity comparison</a></p></main></html>'''
    (OUT / 'dimensions.html').write_text(page)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
