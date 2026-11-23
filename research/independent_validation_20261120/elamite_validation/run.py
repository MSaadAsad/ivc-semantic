"""Fixed-concept lexical screen of structured Elamite; no new sign assignments."""
import argparse
import collections
import csv
import functools
import hashlib
import html
import itertools
import json
from pathlib import Path
import re
import time
import unicodedata

import numpy as np

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
OUT = BASE/'results'
VOCAB = {'N', 'V', 'ADJ', 'Other', 'Uncalss'}
POOLS = ['all', 'unflagged', 'pre_achaemenid_unflagged', 'old_labelled_unflagged']
N = 9999


def read(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows, fields=None):
    with (OUT/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def norm(s, mode='phon'):
    """Vowel-length folding; consonant diacritics preserved in primary mode."""
    s = unicodedata.normalize('NFC', s.lower())
    bits = []
    for ch in s:
        if not ch.isalpha():
            continue
        decomp = unicodedata.normalize('NFD', ch)
        if mode == 'ascii' or decomp[0] in 'aeiou':
            ch = decomp[0]
        bits.append(ch)
    return re.sub(r'([aeiou])\1+', r'\1', ''.join(bits))


def senses(raw):
    # Uppercase suffixes are explicit grammar, not English headwords.
    raw = re.sub(r'-(?=[A-Z0-9])[A-Z0-9].*$', '', raw.strip())
    raw = re.sub(r'\([^()]*\)', '', raw)
    return tuple(sorted({re.sub(r'\s+', ' ', s).strip(' ?!.') .lower()
                         for s in re.split('[,;/]', raw) if s.strip(' ?!.')}))


def matching(rx, entry):
    return any(rx.fullmatch(s) for s in entry['senses'])


def in_pool(e, pool):
    if pool == 'all':
        return True
    if e['cognate_flag']:
        return False
    if pool == 'unflagged':
        return True
    return bool(set(e['periods']) & {'oE', 'mE', 'nE'}) if pool == 'pre_achaemenid_unflagged' else 'oE' in e['periods']


def rx_terms(terms):
    return re.compile(r'\b(?:'+'|'.join(re.escape(s) for s in terms if s)+r')\b', re.I)


@functools.lru_cache(maxsize=None)
def distance(a, b):
    prev = list(range(len(b)+1))
    for i, x in enumerate(a, 1):
        now = [i]
        for j, y in enumerate(b, 1):
            now.append(min(now[-1]+1, prev[j]+1, prev[j-1]+(x != y)))
        prev = now
    return prev[-1]


def pvalue(observed, null):
    return float((1+np.count_nonzero(null >= observed-1e-12))/(len(null)+1))


def holm(ps):
    result = [0.0]*len(ps)
    last = 0
    for rank, idx in enumerate(sorted(range(len(ps)), key=lambda i: ps[i])):
        last = max(last, min(1.0, ps[idx]*(len(ps)-rank)))
        result[idx] = last
    return result


def bitcount(x):
    return bin(x).count('1')


def rebus(entries, cases, mode, seed):
    aa = [[i for i, e in enumerate(entries) if matching(re.compile(c['a_en'], re.I), e)] for c in cases]
    bb = [[i for i, e in enumerate(entries) if matching(re.compile(c['b_en'], re.I), e)] for c in cases]
    by_form = collections.defaultdict(list)
    for i, e in enumerate(entries):
        by_form[e[mode]].append(i)
    edges = [(u, v) for group in by_form.values() for u, v in itertools.combinations(group, 2)]
    a_bits, b_bits = [0]*len(entries), [0]*len(entries)
    for j, (a, b) in enumerate(zip(aa, bb)):
        for i in a: a_bits[i] |= 1 << j
        for i in b: b_bits[i] |= 1 << j
    matrix = np.zeros((len(cases), len(cases)), dtype=bool)
    all_witnesses = []
    for j, a in enumerate(aa):
        for k, b in enumerate(bb):
            found = [(u, v) for u in a for v in b if entries[u]['senses'] != entries[v]['senses']
                     and entries[u][mode] == entries[v][mode]]
            matrix[j, k] = bool(found)
            if j == k:
                for u, v in found:
                    all_witnesses.append(dict(case=j, a=entries[u], b=entries[v]))
    observed = int(np.trace(matrix))
    rng = np.random.default_rng(seed)
    perms = np.array([rng.permutation(len(cases)) for _ in range(N)])
    target_null = matrix[np.arange(len(cases))[None, :], perms].sum(axis=1)
    strata = collections.defaultdict(list)
    for i, e in enumerate(entries):
        strata[(e['category'], min(len(e[mode])//2, 5))].append(i)
    strata = [np.array(x) for x in strata.values() if len(x)>1]
    sound_null = np.zeros(N, dtype=int)
    for j in range(N):
        perm = np.arange(len(entries))
        for group in strata:
            perm[group] = rng.permutation(group)
        hit = 0
        for u, v in edges:
            x, y = int(perm[u]), int(perm[v])
            if entries[x]['senses'] != entries[y]['senses']:
                hit |= (a_bits[x] & b_bits[y]) | (a_bits[y] & b_bits[x])
        sound_null[j] = bitcount(hit)
    rows = []
    for j, c in enumerate(cases):
        rows.append(dict(sign=c['sign'], title=c['title'], picture_entries=len(aa[j]),
                         target_entries=len(bb[j]), both_covered=bool(aa[j] and bb[j]),
                         same_form_hit=bool(matrix[j, j]),
                         picture_words=' | '.join(entries[i]['word']+' ['+'; '.join(entries[i]['senses'])+']' for i in aa[j]),
                         target_words=' | '.join(entries[i]['word']+' ['+'; '.join(entries[i]['senses'])+']' for i in bb[j])))
    return dict(claims=len(cases), both_covered=sum(bool(a and b) for a, b in zip(aa, bb)), hits=observed,
                target_null_mean=float(target_null.mean()), target_p=pvalue(observed, target_null),
                sound_null_mean=float(sound_null.mean()), sound_p=pvalue(observed, sound_null)), rows, all_witnesses, target_null, sound_null


def direct(entries, claims, mode, seed):
    roots = [sorted({norm(x, mode) for x in re.findall(r'\*[-]?([^\W\d_]+(?:-[^\W\d_]+)*)', c['proposal_root']) if norm(x, mode)}) for c in claims]
    targets = [c['b'] if c['kind'] in {'bridge','polysemy'} else c['a'] for c in claims]
    matches = [[e for e in entries if matching(rx_terms(target), e)] for target in targets]
    covered = [i for i in range(len(claims)) if matches[i] and roots[i]]
    sim = np.zeros((len(claims), len(claims)))
    exact = np.zeros_like(sim, dtype=int)
    rows = []
    for i, candidate_roots in enumerate(roots):
        for j, candidates in enumerate(matches):
            if candidates and candidate_roots:
                sim[i,j] = max(1-distance(r,e[mode])/max(len(r),len(e[mode])) for r in candidate_roots for e in candidates)
                exact[i,j] = any(r == e[mode] for r in candidate_roots for e in candidates)
        best = max(matches[i], key=lambda e:max(1-distance(r,e[mode])/max(len(r),len(e[mode])) for r in candidate_roots)) if matches[i] and candidate_roots else None
        rows.append(dict(sign=claims[i]['sign'], title=claims[i]['title'], kind=claims[i]['kind'],
                         proposed_root=claims[i]['proposal_root'], target_concepts='; '.join(targets[i]),
                         covered=i in covered, eligible_equivalents=len(matches[i]),
                         best_similarity=float(sim[i,i]), exact_hit=bool(exact[i,i]),
                         best_word=best['word'] if best else '', best_head='; '.join(best['senses']) if best else '',
                         best_periods='; '.join(best['periods']) if best else '', best_source_id=best['id'] if best else '',
                         best_source_annotations=best.get('source_annotations','') if best else '',
                         best_gloss_uncertain=best['gloss_uncertain'] if best else '',
                         all_equivalents=' | '.join(e['word']+' ['+'; '.join(e['senses'])+']' for e in matches[i])))
    observed = float(np.mean([sim[i,i] for i in covered])) if covered else 0.0
    exact_obs = int(sum(exact[i,i] for i in covered))
    rng = np.random.default_rng(seed)
    groups = [[i for i in covered if (claims[i]['kind']=='numeral') == numeral] for numeral in [False, True]]
    null_sim, null_exact = np.zeros(N), np.zeros(N, dtype=int)
    for k in range(N):
        assigned = np.arange(len(claims))
        for group in groups:
            assigned[group] = rng.permutation(group)
        null_sim[k] = float(sim[covered, assigned[covered]].mean()) if covered else 0
        null_exact[k] = int(exact[covered, assigned[covered]].sum())
    return dict(claims=len(claims), covered=len(covered), mean_similarity=observed,
                exact_hits=exact_obs, similarity_null_mean=float(null_sim.mean()),
                similarity_p=pvalue(observed,null_sim), exact_null_mean=float(null_exact.mean()),
                exact_p=pvalue(exact_obs,null_exact)), rows, null_sim, null_exact


def checks():
    assert norm('mi-in') == norm('mīṉ') .replace('ṉ', 'n')
    assert norm('kuṭi') != norm('kuti')
    assert norm('kuṭi','ascii') == norm('kuti','ascii')
    assert senses('house-PL-3SG.POSS') == ('house',)
    assert not matching(rx_terms(['star']), {'senses':senses('bastard')})
    assert not matching(rx_terms(['chief']), {'senses':senses('mischief')})
    assert not matching(rx_terms(['grain']), {'senses':senses('grain.handler-PL')})
    assert not matching(rx_terms(['month']), {'senses':senses('Halbatum')})
    assert distance('sunki','sunki') == 0 and distance('sunki','kuti') > 0
    assert holm([.01,1,.02,1]) == [.04,1,.06,1]


def main(source_dir):
    started = time.monotonic()
    OUT.mkdir(exist_ok=True)
    checks()
    metadata = json.loads((BASE/'inputs/source_files.json').read_text())
    inventory, audit, eligible = [], [], []
    for spec in metadata['files']:
        path = source_dir/Path(spec['path']).name
        if not path.exists():
            assert path.name == 'PN-EWB-EJSmith.csv'
            continue
        blob = path.read_bytes()
        assert hashlib.sha1(f'blob {len(blob)}\0'.encode()+blob).hexdigest() == spec['blob_sha'], path.name
        records = read(path)
        category = path.name.split('-')[0]
        inventory.append(dict(category=category, filename=path.name, rows=len(records),
                              morphology_populated=sum(bool(x['morphology']) for x in records),
                              semantics_populated=sum(bool(x['semantics']) for x in records),
                              cognate_flagged=sum(bool(x['cognate']) for x in records)))
        for i, r in enumerate(records, 2):
            identifier = f'{category}:{i}'
            w = r['transliteration']
            ss = senses(r['morphology'])
            reason = ('excluded source category' if category not in VOCAB else
                      'no morphology lexical head' if not ss else
                      'damaged or uncertain form' if re.search(r'[?\[\]<>]', w) else
                      'determinative or compound dot' if '.' in w else
                      'logogram or uppercase form' if any(c.isupper() for c in w) else
                      'unexplained form punctuation' if any(not(c.isalpha() or c.isdigit() or c=='-') for c in w) else
                      'short or empty form' if len(norm(w))<2 else 'eligible')
            audit.append(dict(id=identifier, category=category, reason=reason, period=r['period'],
                              cognate_flag=bool(r['cognate'])))
            if reason != 'eligible':
                continue
            eligible.append(dict(id=identifier, category=category, word=w, senses=ss,
                                 phon=norm(w), ascii=norm(w,'ascii'),
                                 periods=tuple(sorted(x.strip() for x in r['period'].split(',') if x.strip())),
                                 cognate_flag=r['cognate'], gloss_uncertain='?' in r['morphology'],
                                 source_annotations=f'{identifier}: {w} [{r["morphology"]}; {r["period"]}]'))
    write('source_inventory.csv',inventory)
    write('entry_eligibility.csv',audit)
    panels = json.loads((BASE.parent/'expanded_rebus_test/cases.json').read_text())['panels']
    claims = json.loads((BASE.parent/'ivc_language_test/claims.json').read_text())['claims']
    assert len(claims) == 67 and sum(map(len,panels.values())) == 178
    summaries, pair_rows, witnesses, direct_rows, direct_summary, null_rows, pool_rows = [], [], [], [], [], [], []
    for pi, pool in enumerate(POOLS):
        # Keep qualification groups separate before pooling: a flagged duplicate
        # cannot erase an independently unflagged record or an early period label.
        entries = {}
        for e in eligible:
            if in_pool(e,pool):
                key = (e['phon'], e['senses'])
                if key in entries:
                    old = entries[key]
                    old['periods'] = tuple(sorted(set(old['periods']) | set(e['periods'])))
                    old['word'] += ' / '+e['word']
                    old['id'] += ' | '+e['id']
                    old['source_annotations'] += ' | '+e['source_annotations']
                    old['gloss_uncertain'] |= e['gloss_uncertain']
                else:
                    entries[key] = dict(e)
        ee = list(entries.values())
        pool_rows.append(dict(pool=pool, eligible_source_rows=sum(in_pool(e,pool) for e in eligible),
                              unique_form_head_pairs=len(ee), unique_phon_forms=len({e['phon'] for e in ee}),
                              unique_heads=len({e['senses'] for e in ee})))
        for mi, mode in enumerate(['phon','ascii']):
            for pj, (panel, cases) in enumerate(panels.items()):
                result, detail, ww, tn, sn = rebus(ee,cases,mode,20261122+pi*100+mi*10+pj)
                scope = dict(pool=pool,mode=mode,panel=panel)
                summaries.append(dict(**scope,**result))
                pair_rows += [dict(**scope,**r) for r in detail]
                for w in ww:
                    c = cases[w['case']]
                    witnesses.append(dict(**scope,sign=c['sign'],title=c['title'],
                                          picture_word=w['a']['word'],target_word=w['b']['word'],
                                          picture_head='; '.join(w['a']['senses']),target_head='; '.join(w['b']['senses']),
                                          normalized_form=w['a'][mode],picture_id=w['a']['id'],target_id=w['b']['id'],
                                          picture_periods='; '.join(w['a']['periods']),target_periods='; '.join(w['b']['periods'])))
                if pool=='unflagged' and mode=='phon' and panel=='fixed48':
                    null_rows += [dict(test='rebus',draw=k+1,target_count=int(t),sound_count=int(s)) for k,(t,s) in enumerate(zip(tn,sn))]
            result, detail, ns, ne = direct(ee,claims,mode,20261222+pi*10+mi)
            direct_summary.append(dict(pool=pool,mode=mode,**result))
            direct_rows += [dict(pool=pool,mode=mode,**r) for r in detail]
            if pool=='unflagged' and mode=='phon':
                write('direct_primary_null.csv',[dict(draw=k+1,similarity=float(s),exact_hits=int(e)) for k,(s,e) in enumerate(zip(ns,ne))])
    r = next(x for x in summaries if x['pool']=='unflagged' and x['mode']=='phon' and x['panel']=='fixed48')
    d = next(x for x in direct_summary if x['pool']=='unflagged' and x['mode']=='phon')
    corrected = holm([r['target_p'],r['sound_p'],d['similarity_p'],d['exact_p']])
    write('rebus_summary.csv',summaries)
    write('all_pair_results.csv',pair_rows)
    write('rebus_witnesses.csv',witnesses,fields=['pool','mode','panel','sign','title','picture_word','target_word','picture_head','target_head','normalized_form','picture_id','target_id','picture_periods','target_periods'])
    write('direct_summary.csv',direct_summary)
    write('all_direct_results.csv',direct_rows)
    write('rebus_primary_null.csv',null_rows)
    write('pool_sizes.csv',pool_rows)
    tested = {c['sign'] for c in claims}
    paired = {c['sign'] for cases in panels.values() for c in cases}
    signs = read(BASE.parent/'translation_catalogue/results/all_163_sign_readings.csv')
    scope = [dict(sign=s['sign'],proposed_root=s['proposed_root'],proposed_meaning=s['proposed_meaning'],
                  direct_claim_tested=s['sign'] in tested, has_frozen_pair_recipe=s['sign'] in paired,
                  scope='fixed direct claim' if s['sign'] in tested else 'additional pair recipe only' if s['sign'] in paired else 'inventory only; no frozen standalone claim') for s in signs]
    assert len(scope)==163
    write('all_163_sign_scope.csv',scope)
    summary = dict(source_rows_retrieved=sum(x['rows'] for x in inventory),
                   common_category_rows=sum(x['rows'] for x in inventory if x['category'] in VOCAB),
                   eligible_source_rows=len(eligible),pool_sizes=pool_rows,
                   pair_formulations=178,current_sign_inventory=163,direct_claims=67,
                   primary_rebus=r,primary_direct=d,
                   primary_holm=dict(zip(['rebus_target','rebus_sound','direct_similarity','direct_exact'],corrected)),
                   controls_per_test=N,primary_gloss_field='morphology lexical head; full-head matching',
                   missing_personal_name_file_excluded=True,
                   historical_sound_correspondence_test_run=False,
                   independent_indus_semantic_assignment=False,
                   current_research_question='Can Elamite explain Indus inscriptions?',
                   direct_affinity_scope='Off target for Elamite–Indus; compares proposed Dravidian forms with Elamite forms.',
                   rebus_scope='Restricted test of the existing proposed picture/meaning pairs; not a full Elamite–Indus language test.',
                   runtime_seconds=round(time.monotonic()-started,2),colab_units=0)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-dir',type=Path,default=REPO.parent/'elamite-sources')
    main(ap.parse_args().source_dir)
