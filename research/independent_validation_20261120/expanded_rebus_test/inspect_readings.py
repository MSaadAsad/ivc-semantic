"""Post-run witness classification; does not change any score or null."""
import csv
import json
import run as R

def main():
    claims=json.loads((R.BASE.parent/'ivc_language_test/claims.json').read_text())['claims']
    witnesses=list(csv.DictReader((R.BASE/'results/witnesses.csv').open()))
    rows=[]
    for c in claims:
        if c['kind'] not in ('bridge','polysemy'):continue
        ww=[w for w in witnesses if w['panel']=='fixed48' and w['language']=='Dravidian' and
            w['sign']==c['sign'] and w['mode'] in ('phon_exact','distinct_sense_polysemy')]
        expected=[w for w in ww if w['a_eid'] in c['a_entries'] and w['b_eid'] in c['b_entries']]
        status='cited-etyma witness' if expected else 'alternative-only machine match' if ww else 'no exact/polysemy match'
        best=(expected or ww or [{}])[0]
        rows.append(dict(sign=c['sign'],title=c['title'],status=status,
            cited_A='; '.join(c['a_entries']),cited_B='; '.join(c['b_entries']),
            example_A=best.get('a_word',''),example_B=best.get('b_word',''),
            example_A_gloss=best.get('a_gloss',''),example_B_gloss=best.get('b_gloss',''),
            interpretation='Etymon-ID agreement is provenance, not confirmation of the sign meaning or word-sense match.'))
    R.write_csv(R.BASE/'results/reading_provenance.csv',rows)
    counts={s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})}
    (R.BASE/'results/reading_provenance.json').write_text(json.dumps(counts,indent=2)+'\n')
    print(counts)

if __name__=='__main__':main()
