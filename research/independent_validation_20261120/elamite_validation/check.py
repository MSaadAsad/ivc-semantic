"""Positive/negative controls for the lexical scoring engine."""
import run as R


def main():
    R.checks()
    R.N = 199  # Synthetic verification only; production results use 9,999.
    entries = [dict(id=str(i),category='N',word=w,phon=w,ascii=w,senses=(g,),periods=('synthetic',),
                    cognate_flag='',gloss_uncertain=False) for i,(w,g) in enumerate([
                        ('sun','fish'),('sun','star'),('tu','house'),('la','pot')])]
    pairs = [dict(sign=str(i),title=a+' to '+b,a_en=R.rx_terms([a]).pattern,b_en=R.rx_terms([b]).pattern)
             for i,(a,b) in enumerate([('fish','star'),('pot','house'),('ship','king')])]
    result, rows, witnesses, _, _ = R.rebus(entries,pairs,'phon',123)
    assert result['hits']==1 and result['both_covered']==2
    assert [r['same_form_hit'] for r in rows]==[True,False,False]
    assert len(witnesses)==1 and witnesses[0]['a']['word']==witnesses[0]['b']['word']=='sun'
    reversed_result, _, _, _, _ = R.rebus(entries[::-1],pairs,'phon',123)
    assert result['hits']==reversed_result['hits'] and result['both_covered']==reversed_result['both_covered']
    claims = [dict(sign='1',title='star',kind='literal',a=['star'],b=[''],proposal_root='*sun'),
              dict(sign='2',title='house',kind='literal',a=['house'],b=[''],proposal_root='*lala'),
              dict(sign='3',title='king',kind='literal',a=['king'],b=[''],proposal_root='*ga')]
    direct, details, _, _ = R.direct(entries,claims,'phon',234)
    assert direct['covered']==2 and direct['exact_hits']==1
    assert details[0]['best_similarity']==1 and details[0]['exact_hit']
    assert not details[1]['exact_hit'] and not details[2]['covered']
    print('Synthetic lexical recovery, semantic nonmatches, missingness and entry-order checks passed.')


if __name__ == '__main__':
    main()
