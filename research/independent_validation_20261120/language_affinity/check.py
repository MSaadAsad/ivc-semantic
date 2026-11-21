"""Check important extraction failures and accounting in the released results."""
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / 'results'


def read(name):
    with (OUT / name).open() as f:
        return list(csv.DictReader(f))


forms = read('parsed_forms.csv')
# Real source examples: punctuation-less language labels and omitted glosses
# must not erase cognates or attribute their forms to the previous language.
expected = [('3684', 'Br', 'nī'), ('474', 'Br', 'iraṭ'),
            ('4885', 'Ta', 'mīṉ'), ('4885', 'Ma', 'mīn'),
            ('4885', 'Ka', 'mīn'), ('4885', 'Te', 'mīnu'),
            ('4885', 'Kui', 'mīnu'), ('4885', 'Kuwi', 'mīnu'),
            ('4885', 'Konḍa', 'mīn')]
for eid, lang, form in expected:
    assert any(r['eid'] == eid and r['lang'] == lang and r['form'] == form for r in forms), (eid, lang, form)
assert any(r['eid'] == '4885' and r['lang'] == 'Ma' and
           r['gloss_inference'] == 'implicit_same_etymon' and r['gloss'] == 'fish.' for r in forms)

summary = json.loads((OUT / 'summary.json').read_text())
assert len(summary['dictionary_coverage']) == 21
assert summary['unique_semantic_signs'] == 68
assert all(r['etymon_groups'] > 100 for r in summary['dictionary_coverage'])
for r in summary['key_affinity']:
    assert r['exact_key_atoms'] <= r['cognate_set_covered'] <= r['total_unique_key_atoms']
    assert r['total_unique_key_atoms'] == 87  # Bracketed English operators excluded.
for r in summary['portability']:
    assert r['supported_signs'] <= r['opportunity_signs'] <= 68
    assert max(r['direct_signs'], r['cross_etymon_signs']) <= r['supported_signs']
    for other in summary['portability']:
        if (r['code'] == other['code'] and r['include_id'] <= other['include_id']
                and r['fold_length'] <= other['fold_length']):
            assert r['supported_signs'] <= other['supported_signs']
assert len(summary['fixed_pair_portability']) == 42
assert all(r['fixed_claimed_pairs'] == 35 for r in summary['fixed_pair_portability'])
evidence = read('bridge_evidence.csv')
for lang in ('Ta', 'Ma', 'Ka', 'Ko', 'To'):
    assert any(r['code'] == lang and r['sign'] == '220' and r['a_eid'] == '4885'
               and r['b_eid'] == '4876' and r['fold_length'] == 'False'
               and r['include_id'] == 'True' for r in evidence), lang
print('Passed source-example, omitted-gloss, language-boundary and output-accounting checks.')
