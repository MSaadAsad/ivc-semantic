"""Count existing animal/text families and physical-die candidates; no new test."""
import collections
import csv
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent;REPO=BASE.parents[2];OUT=BASE/'results'


def read(p):return list(csv.DictReader(p.open()))


def write(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def main():
    family={}
    for r in read(REPO/'work_data/copper/text_families.csv'):
        for text in r['texts'].split(' | '):family[text]=r['family']
    groups=collections.defaultdict(list)
    for r in read(REPO/'work_data/copper/objects.csv'):
        if r['pic_src'] in {'eye','catalogue'} and r['pic'] not in {'','quadruped'}:
            groups[r['pic']].append(r)
    table=[]
    for motif,rr in sorted(groups.items()):
        table.append(dict(motif=motif,object_rows=len(rr),set_texts=len({r['set_text'] for r in rr}),
                          existing_text_families=len({family.get(r['set_text'],r['set_text']) for r in rr}),
                          scope='Existing Lipi copper subset with eye/catalogue-specific motif; not all objects or independent trials.'))
    write('animal_followup_family_feasibility.csv',table)
    elephants=[dict(**{k:r[k] for k in ['obj','cisi','text','set_text','complete','pic','pic_src','area','bh','room','exc']},
                    existing_family=family.get(r['set_text'],r['set_text'])) for r in groups['elephant']]
    write('animal_followup_elephant_members.csv',elephants)
    die=[r for r in read(REPO/'work_data/stamps/matches.csv') if r['match']=='exact' and int(r['n'])>=3]
    write('animal_followup_die_candidates.csv',die)
    prior=[r for r in read(REPO/'work_data/sound_v6/job1_tests.csv') if r['test'] in {'T1','T2','T3','T4','T6'}]
    write('animal_followup_prior_transfer_tests.csv',prior)
    summary=dict(reviewed_upstream_snapshot='727dfd411a4faa44d193d204757540d45c7b139b',
                 pictured_copper_subset_rows=sum(r['object_rows'] for r in table),motif_labels=len(table),
                 elephant_subset_rows=len(elephants),elephant_set_texts=len({r['set_text'] for r in elephants}),
                 elephant_existing_families=len({r['existing_family'] for r in elephants}),
                 exact_text_die_candidate_pairs=len(die),impression_faces=len({r['imp_face'] for r in die}),
                 seal_faces=len({r['seal_face'] for r in die}),physical_die_matches_verified_here=0,
                 new_animal_prediction_test_run=False,existing_transfer_test_rows_released=len(prior),
                 interpretation='Prior-work/feasibility check only. Existing text-family observations and matches are credited to Cuper.',
                 colab_units=0)
    assert summary['elephant_subset_rows']==11 and summary['elephant_set_texts']==2 and summary['elephant_existing_families']==1
    assert len(die)==15 and summary['impression_faces']==13 and summary['seal_faces']==6
    (OUT/'animal_followup_feasibility.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
