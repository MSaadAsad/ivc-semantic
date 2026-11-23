"""Descriptive reading/context examples; no new semantic test or sound value."""
import collections
import csv
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / 'results/lothal_tables'
with (OUT / 'all_93_sealings.csv').open() as f:
    objects = list(csv.DictReader(f))
labels = {'700': 'measure', '390': 'weave/cloth', '590': 'bale/sack-load'}
rows, summary = [], {}
for sign, label in labels.items():
    selected = [r for r in objects if sign in r['signs'].split('; ')]
    summary[sign] = dict(frozen_label=label, object_records=len(selected),
                         supports=dict(collections.Counter(r['container'] for r in selected)),
                         inference='Descriptive literal-sign count; repeated dies retained; no independent prediction test.')
    for r in selected:
        rows.append(dict(sign=sign, frozen_label=label, cisi=r['cisi'], container=r['container'],
                         sign_sequences=r['sign_sequences'], existing_proposed_readings=r['proposed_translations'],
                         published_die_groups_on_object=r['published_die_groups']))
with (OUT / 'reading_trend_occurrences.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
    w.writeheader();w.writerows(rows)
formula = '705-500-741-001-055-220-740-090'
selected = [r for r in objects if formula in r['sign_sequences'].split(' | ')]
summary['manager_formula'] = dict(formula=formula, encoded_object_records=len(selected),
                                  supports=dict(collections.Counter(r['container'] for r in selected)),
                                  specific_support_categories=len({r['container'] for r in selected} - {'undiagnostic','other_types'}),
                                  prior_work='Cuper jobs/out/stamps.md already identifies11 Lothal objects; the detailed source-support join is additional.')
assert len(selected) == 11 and summary['manager_formula']['specific_support_categories'] == 5
assert summary['700']['object_records'] == 3 and summary['390']['object_records'] == 5 and summary['590']['object_records'] == 4
(OUT / 'reading_trend_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
shutil.copy2(BASE / 'LOTHAL_READING_TRENDS.md', OUT / 'reading_trends.md')
print(json.dumps(summary, indent=2))
