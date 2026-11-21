import ast,csv,json,itertools,collections
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description='Exact whole-seal sensitivity check for BMAC versus Core Gulf bigram survival.')
parser.add_argument('--repo',type=Path,required=True)
parser.add_argument('--output',type=Path,default=Path('ivc-frontier-check.json'))
args=parser.parse_args()
p=args.repo.resolve()
src=ast.parse((p/'work_scripts/key4e_museum_archives.py').read_text())
fun=next(n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='load_baselines')
exclude=ast.literal_eval(next(n.value for n in fun.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='EXCLUDE_SITES' for t in n.targets)))
bg=collections.Counter()
for e in json.loads((p/'work_data/sense/events_lipi.json').read_text()):
 site=(e.get('site') or '').strip()
 if site in exclude or any(k in site.lower() for k in ('bahrain','failaka','ur','kish','susa','oman','iran','unknown','mesopotamia','near east','west asia')):continue
 for f in e['faces']:
  toks=[t for t in f if t and t!='000']
  bg.update(zip(toks,toks[1:]))
def stats(s):
 pairs=[(a,b) for a,b in zip(s,s[1:]) if a!='000' and b!='000']
 return (sum(bg.get(x,0)>0 for x in pairs),len(pairs))
f=list(csv.DictReader((p/'work_data/key4e/frontier_expanded_corpus.csv').open()))
a=[(r['fid'],*stats(r['seq_ordered'].split('-'))) for r in f if r['zone']=='Central_Asia_BMAC' and r['inscribed_status']=='inscribed_complete']
b=[]
for r in csv.DictReader((p/'work_data/gulf3/gulf3_verified.csv').open()):
 if r['shape']=='round' and any(k in r['site'] for k in ('Bahrain','Karzakkan','Saar','Janabiyah','Failaka','Ur')) and 'Near East' not in r['site']:
  b.append((r['uid'],*stats(r['seq_verified'].split('-'))))
records=a+b
def rate(rs):
 den=sum(r[2] for r in rs)
 return sum(r[1] for r in rs)/den if den else None
obs=abs(rate(a)-rate(b));extreme=valid=0
for ia in itertools.combinations(range(len(records)),len(a)):
 ids=set(ia);aa=[r for i,r in enumerate(records) if i in ids];bb=[r for i,r in enumerate(records) if i not in ids]
 ra,rb=rate(aa),rate(bb)
 if ra is None or rb is None:continue
 valid+=1;extreme+=abs(ra-rb)>=obs-1e-12
res={'bmac_per_seal':a,'gulf_per_seal':b,'observed_rate_gap':obs,'whole_seal_exact_two_sided_permutation_p':extreme/valid,'extreme':extreme,'valid_label_allocations':valid,'method':'Reassign 3 of 19 whole seals; statistic absolute difference in pooled transition hit rates. Observational exchangeability and genre confounding remain assumptions.'}
args.output.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
