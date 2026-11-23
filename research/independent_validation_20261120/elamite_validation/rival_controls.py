"""Descriptive unrelated-language controls using existing lexical pools.

These pools have different histories/coverage and lack the Elamite release's
chronological and loan metadata. Do not turn their scores into language odds.
"""
import csv
import json
import re
import run as R


def main():
    claims = json.loads((R.BASE.parent/'ivc_language_test/claims.json').read_text())['claims']
    primary = [r for r in R.read(R.OUT/'all_direct_results.csv') if r['pool']=='unflagged' and r['mode']=='phon']
    pools = {}
    for language, name in [('Sumerian','sumerian_wiktionary.tsv'),('Akkadian','akkadian_wiktionary.tsv')]:
        path = R.REPO/'work_data/lang_m/lex'/name
        entries = {}
        with path.open() as f:
            for row in csv.reader(f,delimiter='\t'):
                if len(row)<5:
                    continue
                word = row[1]
                if any(c in word for c in '[]?<>') or len(R.norm(word))<2 or not any(c.isalpha() for c in word):
                    continue
                ss = R.senses(row[4])
                if not ss:
                    continue
                key = (R.norm(word),ss)
                entries[key] = dict(word=word,senses=ss,phon=R.norm(word))
        pools[language] = list(entries.values())
    details = []
    for language, entries in pools.items():
        for claim in claims:
            terms = claim['b'] if claim['kind'] in {'bridge','polysemy'} else claim['a']
            candidates = [e for e in entries if R.matching(R.rx_terms(terms),e)]
            roots = [R.norm(x) for x in re.findall(r'\*[-]?([^\W\d_]+(?:-[^\W\d_]+)*)',claim['proposal_root']) if R.norm(x)]
            score = lambda e:max(1-R.distance(r,e['phon'])/max(len(r),len(e['phon'])) for r in roots)
            best = max(candidates,key=score) if roots and candidates else None
            details.append(dict(language=language,sign=claim['sign'],title=claim['title'],
                                proposed_root=claim['proposal_root'],covered=bool(best),
                                similarity=score(best) if best else 0,
                                exact_hit=any(r==e['phon'] for r in roots for e in candidates),
                                best_word=best['word'] if best else '',best_head='; '.join(best['senses']) if best else ''))
    common = {r['sign'] for r in primary if r['covered']=='True'}
    for language in pools:
        common &= {r['sign'] for r in details if r['language']==language and r['covered']}
    summaries = []
    for language in ['Elamite','Sumerian','Akkadian']:
        if language=='Elamite':
            all_rows = [dict(sign=r['sign'],covered=r['covered']=='True',similarity=float(r['best_similarity']),exact_hit=r['exact_hit']=='True') for r in primary]
        else:
            all_rows = [r for r in details if r['language']==language]
        for scope in ['all_covered','common_coverage']:
            selected = [r for r in all_rows if r['covered'] and (scope=='all_covered' or r['sign'] in common)]
            summaries.append(dict(language=language,scope=scope,covered=len(selected),
                                  mean_similarity=sum(r['similarity'] for r in selected)/len(selected) if selected else 0,
                                  exact_hits=sum(r['exact_hit'] for r in selected),
                                  dictionary_form_head_pairs=next(p['unique_form_head_pairs'] for p in json.loads((R.OUT/'summary.json').read_text())['pool_sizes'] if p['pool']=='unflagged') if language=='Elamite' else len(pools[language]),
                                  interpretation='descriptive control; unequal dictionaries; no language ranking inference'))
    R.write('rival_dictionary_details.csv',details)
    R.write('rival_dictionary_summary.csv',summaries)
    print(json.dumps(summaries,indent=2))


if __name__ == '__main__':
    main()
