"""Substantive checks on answer withholding, recovered witnesses and sensitivity."""
import ast,csv,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
REPO=BASE.parents[2]
def read(n):return list(csv.DictReader((BASE/'results'/n).open()))

def main():
    meta=json.loads((BASE/'results/run_inputs.json').read_text())
    assert meta['cases_sha256']==hashlib.sha256((BASE/'cases.json').read_bytes()).hexdigest()
    assert meta['runner_sha256']==hashlib.sha256((BASE/'run.py').read_bytes()).hexdigest()
    assert meta['inputs']
    for p,h in {**meta['inputs'],**meta['code']}.items():assert hashlib.sha256((REPO/p).read_bytes()).hexdigest()==h,p
    # The runner must not access the answer-key filename, even indirectly via a constant.
    tree=ast.parse((BASE/'run.py').read_text())
    doc_node=tree.body[0].value
    assert not any(isinstance(n,ast.Constant) and isinstance(n.value,str) and 'truth.json' in n.value for n in ast.walk(tree) if n is not doc_node)
    result=json.loads((BASE/'results/scored.json').read_text())
    assert result['truth_sha256']==hashlib.sha256((BASE/'truth.json').read_bytes()).hexdigest()
    primary=result['reading_recovery'][:3]
    assert sum(x['original_correct_reading'] for x in primary)==1
    assert sum(x['distinct_entry_correct_reading'] for x in primary)==3
    assert result['rankings']['phon_exact']['winners']==['Sumerian']
    assert result['rankings']['phon_exact_entry_only']['winners']==['Sumerian']
    scores=read('case_scores.csv');assert len(scores)==28
    assert len({(x['case'],x['language']) for x in scores})==28
    edge=read('edge_eligibility.csv')
    for r in edge:assert int(r['total_homophone_edges'])==int(r['eligible_distinct_cluster_edges'])+int(r['blocked_shared_cluster_edges'])
    for l in ['Akkadian','Burushaski']:
        r=next(r for r in edge if r['language']==l and r['mode']=='phon_exact');assert int(r['total_homophone_edges'])>0 and int(r['eligible_distinct_cluster_edges'])==0
    order=read('row_order_sensitivity.csv')
    for l in {r['language'] for r in order}:assert len({r['record_multiset_sha256'] for r in order if r['language']==l})==1
    assert [int(r['primary_hits']) for r in order if r['language']=='Sumerian']==[1,0]
    permutations=read('permutation_controls.csv');assert len(permutations)==42
    assert sum(r['full_derangement']=='True' for r in permutations)==14
    old=read('indus12_cluster_sensitivity.csv')
    for r in old:assert int(r['distinct_entry_hits'])>=int(r['original_hits'])
    stored=list(csv.DictReader((REPO/'work_data/key2a/test_a2_anchors_summary.csv').open()))
    for r in old:
        original=next(x for x in stored if x['suite']=='A2c_Wave2B_12_Clean' and x['family']==r['language'])
        assert int(original[r['mode']])==int(r['original_hits']),(r,original)
    print('PASS: frozen sources, withheld oracle, 28 cells, real recovered readings, blocked edges, six permutations, order-only change and reproduction of original 12-pair counts.')

if __name__=='__main__':main()
