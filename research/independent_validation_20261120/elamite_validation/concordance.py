"""Predict raw Indus signs with/without an explicit class-marker copy mechanism.

No dictionary, proposed pronunciation or English sign meaning is imported.
"""
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
OUT = BASE/'results'
UNK = '<UNKNOWN>'


def write(name, rows, fields=None):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)


def formula_id(seq):
    return hashlib.sha256('-'.join(seq).encode()).hexdigest()[:16]


def source_formulas(path):
    events=json.loads(path.read_text())
    grouped=collections.defaultdict(list)
    rejected=collections.Counter()
    raw_faces=0
    for event in events:
        for face_no,seq in enumerate(event['faces'],1):
            raw_faces+=1
            if len(seq)<4:
                rejected['fewer_than_four_signs']+=1;continue
            if not all(s.isdigit() and s!='000' for s in seq):
                rejected['damaged_or_non_numeric_ID_transcription']+=1;continue
            grouped[tuple(seq)].append(dict(object_key=event['key'],site=event['site'],kind=event['kind'],face=face_no))
    rows=[]
    for seq,objects in sorted(grouped.items()):
        kinds=collections.Counter(x['kind'] for x in objects)
        kind=min(kinds,key=lambda k:(-kinds[k],k))
        rows.append(dict(seq=seq,id=formula_id(seq),kind=kind,records=objects))
    return rows,dict(raw_objects=len(events),raw_faces=raw_faces,eligible_faces=sum(map(len,grouped.values())),
                     unique_eligible_formulas=len(rows),rejected=dict(rejected))


def observations(formulas):
    result=[]
    for row in formulas:
        seq=row['seq'];n=len(seq)
        for pos in range(3,n):
            result.append(dict(id=row['id'],seq=seq,kind=row['kind'],pos=pos,target=seq[pos],
                               previous=seq[pos-1],context=(min(n,9),'final' if pos==n-1 else 'interior',row['kind']),
                               weight=1/(n-3)))
    return result


class Baseline:
    def __init__(self,formulas):
        self.vocabulary={s for r in formulas for s in r['seq']}|{UNK}
        self.global_counts=collections.Counter();self.context_counts=collections.defaultdict(collections.Counter)
        self.bigram_counts=collections.defaultdict(collections.Counter)
        for row in observations(formulas):
            w=row['weight'];t=row['target'];c=row['context'];p=row['previous']
            self.global_counts[t]+=w;self.context_counts[c][t]+=w;self.bigram_counts[(c,p)][t]+=w
        self.total=sum(self.global_counts.values())
        self.context_totals={c:sum(v.values()) for c,v in self.context_counts.items()}
        self.bigram_totals={c:sum(v.values()) for c,v in self.bigram_counts.items()}

    def probability(self,row):
        t=row['target'] if row['target'] in self.vocabulary else UNK
        p=row['previous'] if row['previous'] in self.vocabulary else UNK
        c=row['context'];b=(c,p)
        prior=(self.global_counts[t]+.5)/(self.total+.5*len(self.vocabulary))
        conditioned=(self.context_counts.get(c,{}).get(t,0)+10*prior)/(self.context_totals.get(c,0)+10)
        return (self.bigram_counts.get(b,{}).get(t,0)+10*conditioned)/(self.bigram_totals.get(b,0)+10)


def candidates(formulas):
    counts=collections.Counter(s for r in formulas for s in r['seq'])
    return {s for s,n in counts.items() if n>=20 and s.isdigit() and int(s)>=60}


def copy_distribution(row,allowed):
    seq=row['seq'];pos=row['pos']
    found=[seq[i] for i in range(1,pos-1) if seq[i] in allowed
           and seq[i-1]!=seq[i] and seq[pos-1]!=seq[i] and seq[i-1]!=seq[pos-1]]
    return collections.Counter(found)


def score_inputs(model,formulas,allowed):
    rows=observations(formulas)
    for row in rows:
        counts=copy_distribution(row,allowed)
        row['baseline_p']=model.probability(row)
        row['copy_available']=bool(counts)
        row['copy_p']=counts[row['target']]/sum(counts.values()) if counts else 0
        row['candidate_suffixes']='|'.join(sorted(counts))
    return rows


def fit_lambda(rows):
    best,best_score=0.0,-float('inf')
    for coefficient in np.arange(0,.95001,.005):
        score=sum(r['weight']*math.log((1-coefficient)*r['baseline_p']+coefficient*r['copy_p'])
                  if r['copy_available'] else r['weight']*math.log(r['baseline_p']) for r in rows)
        if score>best_score+1e-12:
            best,best_score=float(coefficient),score
    return best


def coefficient_curve(validation,test):
    """Post-fit diagnostics only; never used to choose a test coefficient."""
    curve=[]
    for coefficient in np.arange(0,.95001,.005):
        means={}
        for name,rows in [('validation',validation),('test',test)]:
            weighted=0
            for r in rows:
                p=(1-coefficient)*r['baseline_p']+coefficient*r['copy_p'] if r['copy_available'] else r['baseline_p']
                weighted+=r['weight']*math.log2(p/r['baseline_p'])
            means[name]=weighted/len({r['id'] for r in rows})
        curve.append(dict(coefficient=float(coefficient),validation_mean_gain_bits=means['validation'],
                          test_mean_gain_bits=means['test'],use='post-fit diagnostic; no test-set coefficient selection'))
    return curve


def evaluate(rows,coefficient):
    per_formula=collections.defaultdict(list)
    for r in rows:
        p=(1-coefficient)*r['baseline_p']+coefficient*r['copy_p'] if r['copy_available'] else r['baseline_p']
        r['agreement_p']=p;r['gain_bits']=math.log2(p/r['baseline_p'])
        per_formula[r['id']].append(r)
    formula_rows=[]
    for key,group in sorted(per_formula.items()):
        formula_rows.append(dict(formula_id=key,sequence='-'.join(group[0]['seq']),kind=group[0]['kind'],
                                 predicted_positions=len(group),copy_opportunities=sum(x['copy_available'] for x in group),
                                 actual_copy_repeats=sum(x['copy_p']>0 for x in group),
                                 mean_gain_bits_per_predicted_sign=sum(x['gain_bits'] for x in group)/len(group),
                                 joint_gain_bits=sum(x['gain_bits'] for x in group)))
    values=np.array([r['mean_gain_bits_per_predicted_sign'] for r in formula_rows])
    rng=np.random.default_rng(20261123)
    means=values[rng.integers(0,len(values),(9999,len(values)))].mean(axis=1)
    return dict(formulas=len(formula_rows),predicted_positions=len(rows),
                copy_opportunities=sum(r['copy_available'] for r in rows),actual_copy_repeats=sum(r['copy_p']>0 for r in rows),
                mean_gain_bits_per_predicted_sign=float(values.mean()),
                mean_joint_gain_bits_per_formula=float(np.mean([r['joint_gain_bits'] for r in formula_rows])),
                formula_bootstrap_95_percentile_interval=list(np.quantile(means,[.025,.975]))),formula_rows


def run_direction(train,test,reverse=False):
    if reverse:
        train=[{**r,'seq':r['seq'][::-1]} for r in train]
        test=[{**r,'seq':r['seq'][::-1]} for r in test]
    inner=[r for r in train if int(r['id'][:8],16)%5!=0]
    validation=[r for r in train if int(r['id'][:8],16)%5==0]
    allowed=candidates(inner)
    validation_rows=score_inputs(Baseline(inner),validation,allowed)
    coefficient=fit_lambda(validation_rows)
    validation_score,_=evaluate(validation_rows,coefficient)
    target=score_inputs(Baseline(train),test,allowed)
    score,formula_rows=evaluate(target,coefficient)
    curve=coefficient_curve(validation_rows,target)
    write('concordance_'+('reversed' if reverse else 'as_stored')+'_coefficient_curve.csv',curve)
    return dict(direction='reversed' if reverse else 'as_stored',inner_train_formulas=len(inner),
                inner_validation_formulas=len(validation),candidate_suffix_count=len(allowed),
                candidate_suffixes=sorted(allowed),fitted_copy_coefficient=coefficient,
                validation=validation_score,test=score,
                zero_coefficient_interpretation='If coefficient=0, agreement and baseline predictions are identical by construction; a zero interval is not precise evidence against all agreement.'),target,formula_rows


def fit_sparse_markers(validation_rows,allowed):
    """Exploratory refinement: select at most six marker signs on Lipi only.

    Six corresponds to the distinct nonzero nominal class marker types in the
    cited inventory, not a proposed mapping of their sounds to any Indus sign.
    """
    selected=[];coefficient=0.0;best_gain=0.0;steps=[]
    p=np.array([r['baseline_p'] for r in validation_rows])
    weights=np.array([r['weight'] for r in validation_rows])
    grid=np.arange(0,.95001,.005)[:,None]
    all_counts=[copy_distribution(r,allowed) for r in validation_rows]
    markers=sorted(allowed)
    counts=np.array([[c[m] for m in markers] for c in all_counts],dtype=float)
    targets=np.array([[c[m] if m==r['target'] else 0 for m in markers] for c,r in zip(all_counts,validation_rows)],dtype=float)
    for step in range(6):
        winner=None
        for j,marker in enumerate(markers):
            if j in selected:continue
            group=selected+[j];den=counts[:,group].sum(axis=1)
            q=np.divide(targets[:,group].sum(axis=1),den,out=np.zeros(len(den)),where=den>0)
            mixed=np.where(den[None,:]>0,(1-grid)*p[None,:]+grid*q[None,:],p[None,:])
            gains=(np.log2(mixed/p[None,:])*weights[None,:]).sum(axis=1)
            idx=int(np.argmax(gains));gain=float(gains[idx])
            if gain>best_gain+1e-10 and (winner is None or gain>winner[0]+1e-10):
                winner=(gain,j,float(grid[idx,0]))
        if winner is None:break
        best_gain,j,coefficient=winner;selected.append(j)
        steps.append(dict(step=step+1,added_marker=markers[j],selected_markers='|'.join(markers[k] for k in selected),
                          coefficient=coefficient,validation_total_formula_weighted_gain=best_gain))
    return {markers[j] for j in selected},coefficient,steps


def run_sparse(train,test):
    inner=[r for r in train if int(r['id'][:8],16)%5!=0]
    validation=[r for r in train if int(r['id'][:8],16)%5==0]
    allowed=candidates(inner)
    chosen,coefficient,steps=fit_sparse_markers(score_inputs(Baseline(inner),validation,allowed),allowed)
    validation_score,_=evaluate(score_inputs(Baseline(inner),validation,chosen),coefficient)
    target=score_inputs(Baseline(train),test,chosen)
    test_score,formula_rows=evaluate(target,coefficient)
    return dict(description='Post-hoc sparse refinement; all sign/weight selection uses Lipi only',
                maximum_markers=6,selected_markers=sorted(chosen),fitted_copy_coefficient=coefficient,
                validation=validation_score,test=test_score,selection_steps=steps),target,formula_rows


def graphical_check(train,test):
    with (REPO/'work_data/signlist/mark_families.csv').open() as f:
        rows=list(csv.DictReader(f))
    mapping={r['compound']:r['base'] for r in rows}
    def root(s):
        seen=set()
        while s in mapping:
            if s in seen:return None
            seen.add(s);s=mapping[s]
        return s
    admitted=[r for r in rows if r['mark_type']=='cage' and
              r['mark'].lower() in {'caged by four small vertical strokes','caged by four small vertical lines'}
              and int(r['base'])>=60 and int(r['compound'])>=60 and root(r['base']) is not None]
    variants={r['compound']:(root(r['base']),1) for r in admitted}
    for r in admitted:
        variants.setdefault(r['base'],(root(r['base']),0))
    # Admit other unmarked spellings only if they are explicit bases, not arbitrary
    # members of a shared root family with additional unknown graphical modifiers.
    write('concordance_graphic_inventory.csv',admitted)
    pairs=[];summaries=[]
    for corpus,formulas in [('Lipi_train',train),('New_formula_test',test)]:
        counts=collections.Counter()
        for row in formulas:
            for i,(a,b) in enumerate(zip(row['seq'],row['seq'][1:])):
                if a not in variants or b not in variants:continue
                ra,ma=variants[a];rb,mb=variants[b]
                if ra==rb:continue
                category=f'{ma}{mb}';counts[category]+=1
                pairs.append(dict(corpus=corpus,formula_id=row['id'],sequence='-'.join(row['seq']),position=i,
                                  first_sign=a,second_sign=b,first_base_family=ra,second_base_family=rb,
                                  first_caged=bool(ma),second_caged=bool(mb),category=category))
        summaries.append(dict(corpus=corpus,plain_plain=counts['00'],plain_caged=counts['01'],
                              caged_plain=counts['10'],caged_caged=counts['11'],total_eligible_pairs=sum(counts.values())))
    write('concordance_graphic_pairs.csv',pairs,fields=['corpus','formula_id','sequence','position','first_sign','second_sign','first_base_family','second_base_family','first_caged','second_caged','category'])
    write('concordance_graphic_summary.csv',summaries)
    return dict(admitted_graphic_rows=len(admitted),suffix_sound_assignment=False,corpora=summaries)


def synthetic_checks():
    rng=np.random.default_rng(92615)
    def generate(n,agreement,offset):
        result=[]
        for i in range(n):
            a=str(100+int(rng.integers(250)));b=str(400+int(rng.integers(250)))
            m=str(800+int(rng.integers(3)));end=m if agreement else str(800+int(rng.integers(3)))
            seq=(a,m,b,end)
            result.append(dict(seq=seq,id=hashlib.sha256(f'{offset}-{i}'.encode()).hexdigest()[:16],kind='synthetic',records=[]))
        return result
    positive,_,_=run_direction(generate(900,True,'train'),generate(300,True,'test'))
    negative,_,_=run_direction(generate(900,False,'nulltrain'),generate(300,False,'nulltest'))
    assert positive['fitted_copy_coefficient']>.5
    assert positive['test']['mean_gain_bits_per_predicted_sign']>.5
    assert negative['test']['mean_gain_bits_per_predicted_sign']<.05
    sparse_positive,_,_=run_sparse(generate(900,True,'sparse_train'),generate(300,True,'sparse_test'))
    assert sparse_positive['test']['mean_gain_bits_per_predicted_sign']>.5
    return dict(positive_copy_coefficient=positive['fitted_copy_coefficient'],
                positive_test_gain=positive['test']['mean_gain_bits_per_predicted_sign'],
                independent_control_coefficient=negative['fitted_copy_coefficient'],
                independent_control_test_gain=negative['test']['mean_gain_bits_per_predicted_sign'],
                sparse_positive_selected_markers=sparse_positive['selected_markers'],
                sparse_positive_test_gain=sparse_positive['test']['mean_gain_bits_per_predicted_sign'],
                note='Synthetic engine verification, not recovery of a known Elamite corpus.')


def main():
    start=time.monotonic();OUT.mkdir(exist_ok=True)
    checks=synthetic_checks()
    sources=[REPO/'work_data/sense/events_lipi.json',REPO/'work_data/sense/events_new.json',REPO/'work_data/signlist/mark_families.csv']
    train,train_count=source_formulas(sources[0]);new,new_count=source_formulas(sources[1])
    train_forms={r['seq'] for r in train}
    test=[r for r in new if r['seq'] not in train_forms]
    assert len(train)==1373 and len(test)==183
    assert not train_forms & {r['seq'] for r in test}
    memberships=[]
    for corpus,rows in [('Lipi_train',train),('New_formula_test',test)]:
        for r in rows:
            memberships.append(dict(corpus=corpus,formula_id=r['id'],sequence='-'.join(r['seq']),
                                    inner_split=('validation' if int(r['id'][:8],16)%5==0 else 'train') if corpus=='Lipi_train' else 'not_applicable_test',
                                    modal_kind=r['kind'],object_face_records=len(r['records']),
                                    sites='; '.join(sorted({x['site'] for x in r['records']})),
                                    raw_object_keys=' | '.join(x['object_key'] for x in r['records'])))
    write('concordance_formula_membership.csv',memberships)
    results=[]
    for reverse in [False,True]:
        result,positions,formulas=run_direction(train,test,reverse)
        results.append(result);direction=result['direction']
        write(f'concordance_{direction}_formulas.csv',formulas)
        write(f'concordance_{direction}_predictions.csv',[
            dict(formula_id=r['id'],sequence='-'.join(r['seq']),kind=r['kind'],position=r['pos'],target=r['target'],
                 previous_sign=r['previous'],candidate_suffixes=r['candidate_suffixes'],copy_available=r['copy_available'],
                 copy_probability=r['copy_p'],baseline_probability=r['baseline_p'],agreement_probability=r['agreement_p'],gain_bits=r['gain_bits'])
            for r in positions])
    sparse,sparse_positions,sparse_formulas=run_sparse(train,test)
    write('concordance_sparse_formulas.csv',sparse_formulas)
    write('concordance_sparse_selection.csv',sparse['selection_steps'],fields=['step','added_marker','selected_markers','coefficient','validation_total_formula_weighted_gain'])
    write('concordance_sparse_predictions.csv',[
        dict(formula_id=r['id'],sequence='-'.join(r['seq']),kind=r['kind'],position=r['pos'],target=r['target'],
             candidate_suffixes=r['candidate_suffixes'],copy_available=r['copy_available'],copy_probability=r['copy_p'],
             baseline_probability=r['baseline_p'],agreement_probability=r['agreement_p'],gain_bits=r['gain_bits'])
        for r in sparse_positions])
    graphics=graphical_check(train,test)
    summary=dict(research_question='Does an explicit Elamite-style agreement representation improve prediction of Indus signs?',
                 primary_direction='as_stored',uses_dravidian_words=False,uses_proposed_sign_meanings=False,
                 fits_elamite_pronunciations=False,language_identified=False,
                 source_sha256={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                 train_counts=train_count,new_counts=new_count,new_formulas_excluded_for_training_overlap=len(new)-len(test),
                 training_formulas=len(train),test_formulas=len(test),linear_models=results,sparse_refinement=sparse,graphic_representation=graphics,
                 synthetic_verification=checks,bootstrap_unit='unique full inscription formula; 9999 resamples',
                 principal_score='mean bits per predicted sign, averaged equally over formulas',
                 scope='Conditional written agreement models; agreement is not unique to Elamite and may be omitted or written differently.',
                 runtime_seconds=round(time.monotonic()-start,2),colab_units=0)
    (OUT/'concordance_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
