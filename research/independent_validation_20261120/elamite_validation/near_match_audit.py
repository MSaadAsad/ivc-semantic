"""Measure the size of the permissive one-edit leads; no language ranking."""
import collections
import json

import open_rebus as O


def main():
    rows=[r for r in O.R.read(O.OUT/'open_rebus_all_candidates.csv') if r['channel']=='one_edit_whole_form']
    grouped=collections.defaultdict(list)
    for r in rows:grouped[r['picture_word'],r['target_word']].append(r)
    pairs=[]
    for (a,b),rr in sorted(grouped.items()):
        strict_a,strict_b=O.R.norm(a),O.R.norm(b)
        soft_a,soft_b=O.permissive(a),O.permissive(b)
        assert O.R.distance(soft_a,soft_b)==1
        pairs.append(dict(picture_word=a,target_word=b,conservative_picture_key=strict_a,
                          conservative_target_key=strict_b,permissive_picture_key=soft_a,
                          permissive_target_key=soft_b,conservative_edits=O.R.distance(strict_a,strict_b),
                          permissive_edits=1,longer_permissive_length=max(len(soft_a),len(soft_b)),
                          witness_rows=len(rr),picture_nouns=';'.join(sorted({r['picture_noun'] for r in rr})),
                          picture_heads=';'.join(sorted({r['picture_heads'] for r in rr})),
                          target_heads=';'.join(sorted({r['target_heads'] for r in rr}))))
    O.write('near_match_distinct_pairs.csv',pairs)
    def counts(values):return dict(sorted(collections.Counter(values).items()))
    summary=dict(witness_rows=len(rows),distinct_written_word_pairs=len(pairs),
                 witness_conservative_edit_counts=counts(O.R.distance(O.R.norm(r['picture_word']),O.R.norm(r['target_word'])) for r in rows),
                 distinct_pair_conservative_edit_counts=counts(r['conservative_edits'] for r in pairs),
                 witness_longer_permissive_lengths=counts(max(len(O.permissive(r['picture_word'])),len(O.permissive(r['target_word']))) for r in rows),
                 interpretation='One edit after permissive spelling simplification is not necessarily one edit before it, one phoneme, or proven homophony.',
                 comparable_open_target_multilanguage_run=False,colab_units=0)
    assert len(rows)==496 and len(pairs)==185
    assert summary['distinct_pair_conservative_edit_counts']=={1:111,2:66,3:8}
    (O.OUT/'near_match_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
