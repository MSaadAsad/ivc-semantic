import ast
import csv
import json
from pathlib import Path
import numpy as np

import argparse
parser = argparse.ArgumentParser(description='Re-evaluate committed allograph models; requires numpy.')
parser.add_argument('--repo', type=Path, required=True)
parser.add_argument('--output', type=Path, default=Path('ivc-model-check.json'))
args = parser.parse_args()
repo = args.repo.resolve()
source = ast.parse((repo/'work_scripts/key4d_allographs.py').read_text())
names = {'extract_sequences_from_events', 'seqs_to_bigram_arrays', 'eval_brown_and_context_bps', 'make_cmap'}
selected = ast.Module(body=[n for n in source.body if isinstance(n, ast.FunctionDef) and n.name in names], type_ignores=[])
ns = {'np': np}
exec(compile(selected, 'key4d-selected-functions', 'exec'), ns)
load = lambda path: json.loads((repo/path).read_text())
l = load('work_data/sem/events_lipi.json')
n = load('work_data/sem/events_new.json')
rows = list(csv.DictReader((repo/'work_data/reader_v3/corpus_soundfree_readings.csv').open()))
intact = set(t for r in rows if r['intact']=='True' and (r['catalogue']=='Lipi' or r['partnered']=='False') for t in r['signs'].split('-') if t and t!='000' and not t.startswith('X'))
signs = sorted(intact | {s for e in l+n for f in e['faces'] for s in f if s and s!='000' and not s.startswith('X')})
vocab = {s:i+2 for i,s in enumerate(signs)}
vtotal=len(vocab)+2
lse = ns['extract_sequences_from_events'](l,vocab)
nse = ns['extract_sequences_from_events'](n,vocab)
lp,lc=ns['seqs_to_bigram_arrays'](lse)
npv,ncv=ns['seqs_to_bigram_arrays'](nse)
foldids=np.zeros(len(lse), dtype=np.int32)
for i,j in enumerate(np.random.default_rng(20261119).permutation(len(lse))):foldids[j]=i%5
results={}
for name,filename in [('baseline',None),('pure','verified_clusters_pure.csv'),('all','verified_clusters_all.csv')]:
    clusters={}
    if filename:
        for r in csv.DictReader((repo/'work_data/key4d'/filename).open()):clusters[r['canonical']]=r['members'].split('|')
    cmap=ns['make_cmap'](clusters,vocab,vtotal)
    cv=np.zeros(3); total=0
    for k in range(5):
        tr=ns['seqs_to_bigram_arrays']([lse[i] for i in range(len(lse)) if foldids[i]!=k])
        te=ns['seqs_to_bigram_arrays']([lse[i] for i in range(len(lse)) if foldids[i]==k])
        cv+=np.array(ns['eval_brown_and_context_bps'](*tr,*te,cmap,vtotal))*len(te[1]);total+=len(te[1])
    results[name]={'cv_bps':list(cv/total),'new_bps':list(ns['eval_brown_and_context_bps'](lp,lc,npv,ncv,cmap,vtotal))}
results['event_counts']={'lipi':len(l),'new':len(n),'lipi_transitions':len(lc),'new_transitions':len(ncv)}
saved=load('work_data/key4d/perplexity_results.json')
results['saved_event_counts']={k:saved[k] for k in ['lipi_transitions','new_transitions']}
text=json.dumps(results,indent=2)
args.output.write_text(text+'\n')
print(text)
