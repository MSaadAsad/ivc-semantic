"""Expanded, fixed-input filter sensitivity with two sound nulls and domain nulls."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

if os.environ.get('PYTHONHASHSEED') != '0':
    os.execve(sys.executable, [sys.executable] + sys.argv, dict(os.environ, PYTHONHASHSEED='0'))
import numpy as np

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
sys.path.insert(0, str(REPO / 'work_scripts'))
import key2a_rebus_lock as engine

MODES = ['phon_exact', 'phon_stem', 'ascii_exact']
GATES = ['legacy_cluster', 'distinct_entry']
CHANNELS = ['phonetic', 'phonetic_plus_polysemy']
POPCOUNT = getattr(int, 'bit_count', lambda x: bin(x).count('1'))

def write_csv(path, rows):
    with path.open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader(); w.writerows(rows)

def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def holm(values):
    order = np.argsort(values)
    out = np.zeros(len(values), dtype=float)
    high = 0.0
    for rank, i in enumerate(order):
        high = max(high, min(1.0, float(values[i]) * (len(values) - rank)))
        out[i] = high
    return out

def match_inputs(L, cases):
    sides = []
    per_sense = []
    for side in ['a', 'b']:
        rx = [re.compile(c[side + ('_de' if L.is_de else '_en')], re.I) for c in cases]
        ss = [L.match_regex_per_sense(r) for r in rx]
        sides.append(np.array([[bool(v) for v in row] for row in ss]))
        per_sense.append(ss)
    A, B = sides
    sa, sb = per_sense
    poly = np.zeros((len(cases), len(cases)), dtype=bool)
    for e in range(L.E):
        aa = np.flatnonzero(A[:, e]); bb = np.flatnonzero(B[:, e])
        for a in aa:
            for b in bb:
                if any(x != y for x in sa[a][e] for y in sb[b][e]):
                    poly[a, b] = True
    return A, B, poly, per_sense

def packed_columns(matrix):
    # Entry x 64-bit chunk; little-endian conversion is explicit for reproducibility.
    n = matrix.shape[0]
    packed = np.packbits(matrix.T, axis=1, bitorder='little')
    pad = np.zeros((len(packed), ((n+63)//64)*8), dtype=np.uint8)
    pad[:, :packed.shape[1]] = packed
    return pad.view('<u8')

def mask_integer(chunks):
    return int.from_bytes(chunks.astype('<u8', copy=False).tobytes(), 'little')

def edge_masks(L, mode, AP, BP, perm=None):
    U, V = L.edges[mode]
    if perm is not None:
        U, V = perm[U], perm[V]
    if not len(U):
        return (0, 0)
    bits = (AP[U] & BP[V]) | (AP[V] & BP[U])
    all_bits = mask_integer(np.bitwise_or.reduce(bits, axis=0))
    eligible = L.cid_int[U] != L.cid_int[V]
    legacy = mask_integer(np.bitwise_or.reduce(bits[eligible], axis=0)) if eligible.any() else 0
    return (legacy, all_bits)

def score_masks(masks, offsets, poly_bits):
    out = np.zeros((len(offsets), len(MODES), 2, 2), dtype=np.int16)
    for pi, (start, n) in enumerate(offsets):
        panel_mask = ((1 << n)-1) << start
        for mi, mm in enumerate(masks):
            for gi, bits in enumerate(mm):
                out[pi, mi, gi, 0] = POPCOUNT(bits & panel_mask)
                out[pi, mi, gi, 1] = POPCOUNT((bits | poly_bits) & panel_mask)
    return out

def domain_matrices(L, A, B, poly, offsets):
    matrices = []
    for start, n in offsets:
        a = A[start:start+n]; b = B[start:start+n]
        P = poly[start:start+n, start:start+n]
        arr = np.zeros((3, 2, 2, n, n), dtype=bool)
        for mi, mode in enumerate(MODES):
            U, V = L.edges[mode]
            for gi in range(2):
                if gi == 0:
                    good = L.cid_int[U] != L.cid_int[V]
                    u, v = U[good], V[good]
                else:
                    u, v = U, V
                if len(u):
                    arr[mi, gi, 0] = ((a[:, u].astype(np.uint16) @ b[:, v].T.astype(np.uint16)) +
                                          (a[:, v].astype(np.uint16) @ b[:, u].T.astype(np.uint16))) > 0
                arr[mi, gi, 1] = arr[mi, gi, 0] | P
        matrices.append(arr)
    return matrices

def strata(L):
    groups = {}
    for i, forms in enumerate(L.phons):
        length = min(map(len, forms))
        key = (min((length-2)//2, 3), len(forms)>1)
        groups.setdefault(key, []).append(i)
    return [np.array(v, dtype=np.int32) for _, v in sorted(groups.items())]

def entry_perm(L, groups, rng):
    p = np.arange(L.E, dtype=np.int32)
    for g in groups:
        p[g] = rng.permutation(g)
    return p

def sound_null(L, AP, BP, offsets, poly_bits, n, kind, seed):
    out = np.zeros((n, len(offsets), 3, 2, 2), dtype=np.int16)
    rng = np.random.default_rng(seed)
    groups = strata(L)
    for i in range(n):
        p = L.make_cluster_perm(rng) if kind == 'legacy_cluster' else entry_perm(L, groups, rng)
        masks = [edge_masks(L, mode, AP, BP, p) for mode in MODES]
        out[i] = score_masks(masks, offsets, poly_bits)
    return out

def pvalue(obs, null):
    return float((1 + np.count_nonzero(null >= obs))/(len(null)+1))

def witnesses(L, cases, A, B, per_sense):
    rows = []
    for k, c in enumerate(cases):
        for mode in MODES:
            U, V = L.edges[mode]
            good = (A[k, U] & B[k, V]) | (A[k, V] & B[k, U])
            forms = getattr(L, dict(phon_exact='phons', phon_stem='phon_stems', ascii_exact='asciis')[mode])
            for u, v in zip(U[good], V[good]):
                if not A[k, u]: u, v = v, u
                rows.append(dict(language=L.fam, panel=c['panel'], sign=c['sign'], mode=mode,
                    a_eid=L.eids[u], b_eid=L.eids[v],
                    a_word='; '.join(L.etyma[u]['hws']), b_word='; '.join(L.etyma[v]['hws']),
                    a_gloss='; '.join(L.senses[u]), b_gloss='; '.join(L.senses[v]),
                    shared_key='; '.join(sorted(set(forms[u]) & set(forms[v]))),
                    legacy_accepted=bool(L.cid_int[u]!=L.cid_int[v]),
                    a_cluster=L.cids[u], b_cluster=L.cids[v]))
        for i in np.flatnonzero(A[k] & B[k]):
            if not any(a!=b for a in per_sense[0][k][i] for b in per_sense[1][k][i]): continue
            rows.append(dict(language=L.fam, panel=c['panel'], sign=c['sign'], mode='distinct_sense_polysemy',
                a_eid=L.eids[i], b_eid=L.eids[i], a_word='; '.join(L.etyma[i]['hws']), b_word='; '.join(L.etyma[i]['hws']),
                a_gloss='; '.join(L.senses[i]), b_gloss='; '.join(L.senses[i]), shared_key='',
                legacy_accepted=True, a_cluster=L.cids[i], b_cluster=L.cids[i]))
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', type=Path, required=True)
    ap.add_argument('--n', type=int, default=9999)
    ap.add_argument('--output', type=Path, default=BASE/'results')
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    engine.TMP_LEX = str(args.cache)
    spec = json.loads((BASE/'cases.json').read_text())
    assert spec['plan_sha256'] == hash_file(BASE/'PLAN.md')
    for path, digest in spec['input_sha256'].items(): assert hash_file(REPO/path) == digest, path
    built = json.loads((args.cache/'built.json').read_text())
    for p, h in {**built['code'], **built['inputs']}.items(): assert hash_file(REPO/p)==h, p
    names = list(spec['panels'])
    cases = []; offsets = []
    for name in names:
        cc = spec['panels'][name]
        offsets.append((len(cases), len(cc)))
        cases.extend(dict(c, panel=name) for c in cc)
    # One shared, genuinely varying permutation schedule per panel.
    schedules = []
    for pi, (_, n) in enumerate(offsets):
        rng = np.random.default_rng(20261121+pi)
        schedules.append(np.array([rng.permutation(n) for _ in range(args.n)]))
    summary = []; details = []; all_witnesses = []; order_rows = []; eligibility = []
    saved = {}; all_dm = {}; coverage = {}; times = []
    started = time.monotonic()
    for li, (language, lexicon, is_de) in enumerate(engine.PRIMARY_7_FAMILIES):
        t = time.monotonic()
        L = engine.CleanCognateLex(language, lexicon, is_de=is_de)
        for mode in MODES:
            u, v = L.edges[mode]
            eligibility.append(dict(language=language, mode=mode, entries=L.E,
                candidate_edges=len(u), eligible_legacy_edges=int(np.sum(L.cid_int[u]!=L.cid_int[v])),
                eligible_uniform_edges=len(u),
                entry_shuffle_strata='; '.join(map(str, sorted(map(len, strata(L)))))))
        A, B, poly, ss = match_inputs(L, cases)
        AP, BP = packed_columns(A), packed_columns(B)
        poly_bits = sum(int(v) << i for i, v in enumerate(np.diag(poly)))
        masks = [edge_masks(L, mode, AP, BP) for mode in MODES]
        observed = score_masks(masks, offsets, poly_bits)
        dm = domain_matrices(L, A, B, poly, offsets)
        all_dm[language] = dm
        coverage[language] = A.any(axis=1) & B.any(axis=1)
        domain = np.zeros((args.n, len(names), 3, 2, 2), dtype=np.int16)
        for pi, ((start, n), perm) in enumerate(zip(offsets, schedules)):
            domain[:, pi] = dm[pi][:, :, :, np.arange(n)[None, :], perm].sum(axis=-1).transpose(3, 0, 1, 2)
            assert np.array_equal(np.diagonal(dm[pi], axis1=-2, axis2=-1).sum(axis=-1), observed[pi])
        print(language, 'observed/preparation seconds', round(time.monotonic()-t, 2), flush=True)
        legacy = sound_null(L, AP, BP, offsets, poly_bits, args.n, 'legacy_cluster', 20261122)
        neutral = sound_null(L, AP, BP, offsets, poly_bits, args.n, 'entry', 20261123)
        saved[language+'_domain'] = domain
        saved[language+'_legacy_sound'] = legacy
        saved[language+'_entry_sound'] = neutral
        saved[language+'_observed'] = observed
        saved[language+'_coverage'] = coverage[language]
        for pi, (start, n) in enumerate(offsets):
            saved[language+'_matrix_'+names[pi]] = dm[pi]
            both = coverage[language][start:start+n]
            for mi, mode in enumerate(MODES):
                for gi, gate in enumerate(GATES):
                    for ci, channel in enumerate(CHANNELS):
                        obs = int(observed[pi, mi, gi, ci])
                        dn = domain[:, pi, mi, gi, ci]
                        en = neutral[:, pi, mi, gi, ci]
                        ln = legacy[:, pi, mi, gi, ci]
                        pd, pe, pl = pvalue(obs, dn), pvalue(obs, en), pvalue(obs, ln)
                        summary.append(dict(panel=names[pi], language=language, dictionary=lexicon,
                            entries=L.E, n_pairs=n, both_domains=int(both.sum()), mode=mode, gate=gate, channel=channel,
                            hits=obs, domain_mean=float(dn.mean()), domain_sd=float(dn.std()), p_domain=pd,
                            entry_sound_mean=float(en.mean()), entry_sound_sd=float(en.std()), p_entry_sound=pe,
                            legacy_sound_mean=float(ln.mean()), p_legacy_sound=pl,
                            p_both_requirements=max(pd, pe), excess_over_domain=obs-float(dn.mean())))
            for k in range(start, start+n):
                details.append(dict(language=language, panel=names[pi], sign=cases[k]['sign'], title=cases[k]['title'],
                    a_entries=int(A[k].sum()), b_entries=int(B[k].sum()), polysemy=bool(poly[k, k]),
                    **{mode+'_'+gate:bool(masks[mi][gi] & (1<<k))
                       for mi, mode in enumerate(MODES) for gi, gate in enumerate(GATES)}))
        all_witnesses.extend(witnesses(L, cases, A, B, ss))
        # A pure input-order reversal leaves the multiset and dictionary content unchanged.
        reverse_cache = args.cache/'expanded_reverse'; reverse_cache.mkdir(exist_ok=True)
        raw = (args.cache/(lexicon+'.tsv')).read_text().splitlines()
        (reverse_cache/(lexicon+'.tsv')).write_text('\n'.join(reversed(raw))+'\n')
        engine.TMP_LEX = str(reverse_cache)
        R = engine.CleanCognateLex(language, lexicon, is_de=is_de)
        engine.TMP_LEX = str(args.cache)
        RA, RB, RP, _ = match_inputs(R, cases)
        rm = [edge_masks(R, mode, packed_columns(RA), packed_columns(RB)) for mode in MODES]
        rp = sum(int(v)<<i for i,v in enumerate(np.diag(RP)))
        reversed_scores = score_masks(rm, offsets, rp)
        assert np.array_equal(observed[:, :, 1, :], reversed_scores[:, :, 1, :])
        for pi, panel in enumerate(names):
            for ci, channel in enumerate(CHANNELS):
                order_rows.append(dict(language=language, panel=panel, channel=channel,
                    legacy_original=int(observed[pi,0,0,ci]), legacy_reversed=int(reversed_scores[pi,0,0,ci]),
                    uniform_original=int(observed[pi,0,1,ci]), uniform_reversed=int(reversed_scores[pi,0,1,ci])))
        times.append(dict(language=language, seconds=round(time.monotonic()-t, 3)))
        print(language, 'completed seconds', times[-1]['seconds'], flush=True)
    global_adjustment = holm([r['p_both_requirements'] for r in summary])
    for r, adj in zip(summary, global_adjustment): r['p_holm_global'] = float(adj)
    for panel in names:
        rr = [r for r in summary if r['panel']==panel and r['mode']=='phon_exact' and
              r['gate']=='distinct_entry' and r['channel']=='phonetic_plus_polysemy']
        for r, adj in zip(rr, holm([r['p_both_requirements'] for r in rr])):
            r['p_holm_primary7'] = float(adj)
    for r in summary: r.setdefault('p_holm_primary7', '')
    comparisons = []
    for pi, panel in enumerate(names):
        start, n = offsets[pi]
        for language, _, _ in engine.PRIMARY_7_FAMILIES:
            if language=='Dravidian': continue
            common = coverage['Dravidian'][start:start+n] & coverage[language][start:start+n]
            for subset, ids in [('all',np.arange(n)), ('common_coverage',np.flatnonzero(common))]:
                d = all_dm['Dravidian'][pi][0,1,1][np.ix_(ids,ids)]
                r = all_dm[language][pi][0,1,1][np.ix_(ids,ids)]
                m = len(ids)
                dd, rd = int(np.trace(d)), int(np.trace(r))
                if m:
                    if subset=='all': permutations=schedules[pi]
                    else:
                        rng=np.random.default_rng(20261201+pi)
                        permutations=np.array([rng.permutation(m) for _ in range(args.n)])
                    null=(d[np.arange(m)[None,:],permutations].sum(axis=1)-
                          r[np.arange(m)[None,:],permutations].sum(axis=1))
                    p=pvalue(dd-rd,null)
                    mean=float(null.mean())
                else: p=1.0;mean=0.0
                comparisons.append(dict(panel=panel, rival=language, subset=subset, n_pairs=m,
                    dravidian_hits=dd, rival_hits=rd, observed_difference=dd-rd,
                    domain_null_difference_mean=mean, excess_difference=dd-rd-mean,
                    p_dravidian_advantage=p))
        for subset in ['all','common_coverage']:
            rr=[r for r in comparisons if r['panel']==panel and r['subset']==subset]
            for r, adj in zip(rr,holm([r['p_dravidian_advantage'] for r in rr])):
                r['p_holm6']=float(adj)
    # Reproduce the two most relevant original panels without changing source regexes.
    old=list(csv.DictReader((REPO/'work_data/key2a/test_a2_anchors_summary.csv').open()))
    reproduction=[]
    for panel, old_name in [('legacy12','A2c_Wave2B_12_Clean'),('auto51','A2a_AutoTier1_All51')]:
        for family, _, _ in engine.PRIMARY_7_FAMILIES:
            before=next(r for r in old if r['suite']==old_name and r['family']==family)
            now=next(r for r in summary if r['panel']==panel and r['language']==family and
                     r['mode']=='phon_exact' and r['gate']=='legacy_cluster' and r['channel']=='phonetic')
            assert int(before['phon_exact'])==now['hits'], (panel,family)
            reproduction.append(dict(panel=panel,language=family,stored_hits=before['phon_exact'],
                reproduced_hits=now['hits'],stored_entries=before['n_etyma'],regenerated_entries=now['entries']))
    write_csv(args.output/'summary.csv',summary)
    write_csv(args.output/'case_scores.csv',details)
    write_csv(args.output/'witnesses.csv',all_witnesses)
    write_csv(args.output/'pairwise.csv',comparisons)
    write_csv(args.output/'row_order.csv',order_rows)
    write_csv(args.output/'reproduction.csv',reproduction)
    write_csv(args.output/'eligibility.csv',eligibility)
    np.savez_compressed(args.output/'nulls_and_matrices.npz',**saved)
    meta=dict(n_controls=args.n,seed_domain=20261121,seed_legacy_sound=20261122,seed_entry_sound=20261123,
        panels={k:len(v) for k,v in spec['panels'].items()},
        cases_sha256=hash_file(BASE/'cases.json'),plan_sha256=hash_file(BASE/'PLAN.md'),
        runner_sha256=hash_file(Path(__file__)),source_inputs=spec['input_sha256'],
        prior_a2_summary_sha256=hash_file(REPO/'work_data/key2a/test_a2_anchors_summary.csv'),
        lexical_inputs=built,
        generated_lexica={name:hash_file(args.cache/(name+'.tsv')) for _,name,_ in engine.PRIMARY_7_FAMILIES},
        language_times=times,total_seconds=round(time.monotonic()-started,3))
    (args.output/'run.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('COMPLETE seconds', meta['total_seconds'], flush=True)

if __name__ == '__main__':
    main()
