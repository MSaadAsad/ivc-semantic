"""Retrospective dictionary portability audit, not an Indus language classifier.

No upstream analysis code is imported. Python 3.9+, standard library only.
Run --freeze once to record the source hypotheses; subsequent runs verify hashes.
"""
import argparse
import ast
import collections
import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
OUT = BASE / 'results'
LANGUAGES = dict([
    ('Ta', 'Tamil'), ('Ma', 'Malayalam'), ('Ka', 'Kannada'), ('Te', 'Telugu'),
    ('Tu', 'Tulu'), ('Ko', 'Kota'), ('To', 'Toda'), ('Koḍ', 'Kodagu'),
    ('Kol', 'Kolami'), ('Nk', 'Naikri'), ('Pa', 'Parji'), ('Ga', 'Gadaba'),
    ('Go', 'Gondi'), ('Konḍa', 'Konda'), ('Pe', 'Pengo'), ('Manḍ', 'Manda'),
    ('Kui', 'Kui'), ('Kuwi', 'Kuwi'), ('Kur', 'Kurukh'), ('Malt', 'Malto'),
    ('Br', 'Brahui'),
])
# Additional DEDR languages are recognized as boundaries even when not tabulated.
MARKERS = sorted(set(LANGUAGES) | {
    'Kuṛ', 'Koṇḍa', 'Ir', 'PāKu', 'PālKu', 'ĀlKu', 'AlKu', 'Kurub', 'Bel', 'Kor',
}, key=len, reverse=True)
LM = '|'.join(map(re.escape, MARKERS))
LANG_RE = re.compile(r'(?<!\w)(' + LM + r')\.?\s+')
GLUED = re.compile(r'(?<=[.;])\s+(\d{1,4}[a-z]?)(?:\s*\([a-z]\))?\s+(?=(?:' + LM + r')\.?\s)')
POS = {'n.', 'adj.', 'adv.', 'v.', 'v.i.', 'v.t.', 'intr.', 'tr.', 'pl.',
       'interj.', 'vb.', 'f.', 'm.', 'nom.', 'caus.', 'refl.'}
BAD = POS | {'id.', 'id', 'to', 'and', 'or', 'also', 'cf.', 'Cf.', 'see',
             'DED', 'DEN', 'Skt.', 'Pkt.', 'IA', 'not', 'a', 'an', 'the'}
INPUTS = ['work_data/lexicons/dedr/dedr_entries.tsv',
          'work_data/key6a/master_lexicon_after_key6a.csv',
          'work_scripts/key2a_rebus_lock.py', 'work_scripts/key4b_bootstrap_wave2.py',
          'work_scripts/key5a_big_six_strike.py', 'work_scripts/key6a_wave4_strike.py',
          'work_data/key5a/trackA_per_sign_bridges.csv',
          'work_data/key6a/trackA_per_sign_bridges.csv']


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def write_csv(name, rows, fields):
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def literal(path, name):
    for node in ast.parse((REPO / path).read_text()).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError(name)


def freeze():
    domains = {}
    history = []
    p = INPUTS[2]
    for s, label, a, _, b, _ in literal(p, 'CLEAN_WAVE2B_12'):
        item = dict(sign=s, shape=label, a=a, b=b, source=p, wave=1)
        history.append(item)
        domains[s] = item
    # No manual synonym additions, repairs or successful-sign selection.
    for wave, p, variable in [(2, INPUTS[3], 'WAVE2_SPECS'),
                              (3, INPUTS[4], 'TRACK_A_SPECS'),
                              (4, INPUTS[5], 'TRACK_A_WAVE4_SPECS')]:
        for rec in literal(p, variable):
            s, novel, label, a, b = rec[:5]
            item = dict(sign=s, shape=label, a=r'\b(?:' + '|'.join(map(re.escape, a)) + r')\b',
                        b=r'\b(?:' + '|'.join(map(re.escape, b)) + r')\b', source=p, wave=wave)
            history.append(item)
            domains[s] = item
    fixed_pairs = {}
    for path in INPUTS[6:]:
        with (REPO / path).open() as f:
            for row in csv.DictReader(f):
                for column in ('phonex_bridges', 'phonst_bridges'):
                    for bridge in row[column].split('|'):
                        m = re.search(r'DEDR\s+(\d+[a-z]?)\s+[^<>]+<->\s*(?:DEDR\s+)?(\d+[a-z]?)\b', bridge)
                        if m:
                            a, b = m.groups()
                            fixed_pairs[(row['sign'], a, b)] = dict(sign=row['sign'], a_eid=a, b_eid=b,
                                                                    source=path, source_claim=bridge.strip())
    dump(BASE / 'design.json', dict(
        source_commit='727dfd411a4faa44d193d204757540d45c7b139b',
        input_sha256={p: hashlib.sha256((REPO / p).read_bytes()).hexdigest() for p in INPUTS},
        languages=LANGUAGES, domains=list(domains.values()), historical_specs=history,
        fixed_claimed_pairs=list(fixed_pairs.values()),
        design='Latest specification per sign, including failures and retested signs; '
               'English domains copied without amendments. Retrospective and selected within Dravidian.',
    ))


def outside(text, pos):
    return text[:pos].count('(') == text[:pos].count(')')


def remove_parentheses(text):
    # Nested phonetic/dialect notes excluded, including optional sounds: conservative.
    # Retain the shorter of an internal optional-phone variant, e.g. k(r)u -> ku.
    text = re.sub(r'(?<=[^\W\d_])\([^()]*\)(?=[^\W\d_])', '', text)
    out, depth = [], 0
    for c in text:
        if c == '(':
            depth += 1
            out.append(' ')
        elif c == ')':
            depth = max(0, depth - 1)
        elif not depth:
            out.append(c)
    return ''.join(out)


def clean_form(form):
    form = unicodedata.normalize('NFC', form.strip(" ,.;:*[]\""))
    if form in BAD or not form or len(form) > 40 or not any(c.isalpha() for c in form):
        return None
    if any(not (c.isalpha() or unicodedata.category(c).startswith('M') or c in "-ʼ'··") for c in form):
        return None
    return form


def norm(form, fold_length=False):
    # DEDR r-with-subscript is conventionally also represented by ḻ in the key.
    form = unicodedata.normalize('NFC', form).replace('r̤', 'ḻ')
    form = re.sub(r'([aeiou])[··]', lambda m: dict(zip('aeiou', 'āēīōū'))[m.group(1)], form)
    if fold_length:
        form = form.translate(str.maketrans('āēīōū', 'aeiou'))
    # Keep vowel length, retroflexion, n/ṉ/ṇ and doubled consonants in primary test.
    return ''.join(c.lower() for c in form if c.isalpha() or unicodedata.category(c).startswith('M'))


def load_dictionary():
    entries = {}
    raw_rows = 0
    for line in (REPO / INPUTS[0]).read_text().splitlines():
        raw_rows += 1
        eid, text = line.split('\t', 1)
        cuts = [m for m in GLUED.finditer(text) if outside(text, m.start())
                and not re.search(r'(?:s\.v\.|cf\.|nos?\.|see)\s*$', text[max(0, m.start()-18):m.start()], re.I)]
        chunks = [(eid, text[:cuts[0].start()] if cuts else text)]
        chunks += [(m.group(1), text[m.end():cuts[i+1].start() if i+1 < len(cuts) else len(text)])
                   for i, m in enumerate(cuts)]
        for eid, txt in chunks:
            if len(txt) > len(entries.get(eid, '')):
                entries[eid] = txt
    records, skipped_loans = [], []
    for eid, text in entries.items():
        text = re.split(r'\s/\s*Cf\.|DED\(S|DEN\b|Previous Page', text)[0]
        # Only explicit loan-marked PRIMARY entry headers. This is not full loan cleaning.
        if re.search(r'<\s*(?:Skt|Pkt|IA)\b', text[:120]):
            skipped_loans.append(eid)
            continue
        marks = [m for m in LANG_RE.finditer(text) if outside(text, m.start())]
        previous_global_gloss = None
        for i, m in enumerate(marks):
            lang = {'Kuṛ': 'Kur', 'Koṇḍa': 'Konḍa'}.get(m.group(1), m.group(1))
            segment = text[m.end():marks[i+1].start() if i+1 < len(marks) else len(text)]
            segment = re.split(r'\s/\s', segment)[0]
            previous_forms = None
            for raw_chunk in remove_parentheses(segment).split(';'):
                tokens = raw_chunk.strip().split()
                if not tokens:
                    continue
                if tokens[0] in POS or tokens[0] == 'to':
                    if not previous_forms:
                        continue
                    forms = previous_forms
                    gloss = ' '.join(tokens)
                else:
                    forms, k = [], 0
                    while k < len(tokens):
                        token = tokens[k]
                        k += 1
                        for part in token.rstrip(',').split('/'):
                            form = clean_form(part)
                            if form:
                                forms.append(form)
                        if not token.endswith(','):
                            break
                    gloss = ' '.join(tokens[k:]).strip()
                if not forms:
                    continue
                previous_forms = forms
                # Resolve only a whole 'id.' gloss; additional prose is not guessed.
                is_id = bool(re.fullmatch(r'id\.?', gloss))
                inferred = (is_id or not gloss) and previous_global_gloss is not None
                resolved = previous_global_gloss if inferred else gloss
                if gloss and not is_id:
                    previous_global_gloss = gloss
                if not resolved or is_id and not inferred:
                    continue
                for form in forms:
                    records.append(dict(eid=eid, lang=lang, form=form, gloss=resolved,
                                        gloss_inferred_id=inferred,
                                        gloss_inference=('explicit_id' if is_id else 'implicit_same_etymon') if inferred else 'none',
                                        raw_chunk=raw_chunk.strip()))
    return records, dict(raw_rows=raw_rows, split_entries=len(entries),
                         skipped_header_loan_entries=skipped_loans)


def distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        row = [i]
        for j, cb in enumerate(b, 1):
            row.append(min(row[-1] + 1, prev[j] + 1, prev[j-1] + (ca != cb)))
        prev = row
    return prev[-1] / max(len(a), len(b), 1)


def key_affinity(records):
    index = collections.defaultdict(list)
    by_eid = collections.defaultdict(list)
    for r in records:
        index[norm(r['form'])].append(r)
        by_eid[r['eid']].append(r)
    roots = collections.defaultdict(list)
    # Only starred lexical atoms, not English labels or inferred phonetic transcriptions.
    with (REPO / INPUTS[1]).open() as f:
        for row in csv.DictReader(f):
            for option in row['root_or_gloss'].split('/'):
                if '*' not in option:
                    continue
                lexical = re.sub(r'\[[^]]*\]', '', option.split('*', 1)[1].split()[0])
                for atom in lexical.split('-'):
                    atom = clean_form(atom)
                    if atom:
                        roots[norm(atom)].append(dict(sign=row['sign'], display=atom))
    rows = []
    for root, uses in sorted(roots.items()):
        eids = sorted({r['eid'] for r in index[root]})
        candidate = [r for eid in eids for r in by_eid[eid]]
        for lang, language in LANGUAGES.items():
            options = [r for r in candidate if r['lang'] == lang]
            best = min(options, key=lambda r: distance(root, norm(r['form']))) if options else None
            rows.append(dict(root=root, signs=' '.join(sorted({u['sign'] for u in uses})),
                             language=language, code=lang, reference_etyma=' '.join(eids),
                             has_candidate=bool(best), nearest_form=best['form'] if best else '',
                             nearest_eid=best['eid'] if best else '',
                             normalized_edit_distance=distance(root, norm(best['form'])) if best else '',
                             exact=bool(best and root == norm(best['form']))))
    write_csv('key_root_affinity.csv', rows, list(rows[0]))
    common_roots = {root for root in roots if all(any(r['root'] == root and r['code'] == lang and r['has_candidate']
                                                     for r in rows) for lang in ('Ta', 'Ma', 'Ka', 'Te'))}
    summary = []
    for lang, language in LANGUAGES.items():
        rr = [r for r in rows if r['code'] == lang]
        covered = [r for r in rr if r['has_candidate']]
        common = [r for r in covered if r['root'] in common_roots]
        summary.append(dict(code=lang, language=language, total_unique_key_atoms=len(roots),
                            dictionary_located_atoms=sum(bool(index[root]) for root in roots),
                            cognate_set_covered=len(covered), exact_key_atoms=sum(r['exact'] for r in rr),
                            four_major_common_atoms=len(common_roots),
                            common_atoms_covered=len(common),
                            common_mean_distance=sum(r['normalized_edit_distance'] for r in common)/len(common) if common else None))
    return summary


def portability(records, domains):
    evidence, scores = [], []
    for include_id in (False, True):
        for fold_length in (False, True):
            for lang, language in LANGUAGES.items():
                rr = [r for r in records if r['lang'] == lang and (include_id or not r['gloss_inferred_id'])]
                for d in domains:
                    aa = [r for r in rr if re.search(d['a'], r['gloss'], re.I)]
                    bb = [r for r in rr if re.search(d['b'], r['gloss'], re.I)]
                    ia, ib = collections.defaultdict(list), collections.defaultdict(list)
                    for records_, index in ((aa, ia), (bb, ib)):
                        for r in records_:
                            index[norm(r['form'], fold_length)].append(r)
                    intersect = sorted(set(ia) & set(ib))
                    direct, rebus = False, False
                    for form in intersect:
                        # One witness per etymon pair; detailed lexemes/glosses released.
                        pairs = {}
                        for a in ia[form]:
                            for b in ib[form]:
                                pairs.setdefault((a['eid'], b['eid']), (a, b))
                        for a, b in pairs.values():
                            same = a['eid'] == b['eid']
                            direct |= same
                            rebus |= not same
                            evidence.append(dict(sign=d['sign'], code=lang, language=language,
                                include_id=include_id, fold_length=fold_length,
                                kind='same_etymon' if same else 'cross_etymon',
                                normalized_form=form, a_form=a['form'], b_form=b['form'],
                                a_eid=a['eid'], b_eid=b['eid'], a_gloss=a['gloss'], b_gloss=b['gloss'],
                                a_id=a['gloss_inferred_id'], b_id=b['gloss_inferred_id']))
                    scores.append(dict(sign=d['sign'], code=lang, language=language,
                                       include_id=include_id, fold_length=fold_length,
                                       a_forms=len(aa), b_forms=len(bb), opportunity=bool(aa and bb),
                                       direct=direct, rebus=rebus, either=bool(intersect)))
    write_csv('bridge_evidence.csv', evidence, list(evidence[0]))
    write_csv('bridge_sign_scores.csv', scores, list(scores[0]))
    summaries = []
    for include_id in (False, True):
        for fold_length in (False, True):
            ss = [s for s in scores if s['include_id'] == include_id and s['fold_length'] == fold_length]
            common = {d['sign'] for d in domains if all(any(s['sign'] == d['sign'] and s['code'] == lg and s['opportunity']
                          for s in ss) for lg in ('Ta', 'Ma', 'Ka', 'Te'))}
            for lang, language in LANGUAGES.items():
                ll = [s for s in ss if s['code'] == lang]
                cc = [s for s in ll if s['sign'] in common]
                summaries.append(dict(code=lang, language=language, include_id=include_id,
                    fold_length=fold_length, proposed_signs=len(domains),
                    opportunity_signs=sum(s['opportunity'] for s in ll),
                    direct_signs=sum(s['direct'] for s in ll),
                    cross_etymon_signs=sum(s['rebus'] for s in ll),
                    supported_signs=sum(s['either'] for s in ll),
                    common_four_signs=len(common), common_opportunities=sum(s['opportunity'] for s in cc),
                    common_supported=sum(s['either'] for s in cc),
                    common_sign_ids=' '.join(sorted(common))))
    return summaries


def fixed_pair_portability(records, pairs):
    """Hold claimed DEDR pairs fixed; allow no replacement etyma for any language."""
    by_lang_eid = collections.defaultdict(list)
    for r in records:
        by_lang_eid[(r['lang'], r['eid'])].append(r)
    rows = []
    for p in pairs:
        for lang, language in LANGUAGES.items():
            aa, bb = by_lang_eid[(lang, p['a_eid'])], by_lang_eid[(lang, p['b_eid'])]
            for fold in (False, True):
                best = min(((distance(norm(a['form'], fold), norm(b['form'], fold)), a, b)
                            for a in aa for b in bb), key=lambda x: x[0], default=None)
                rows.append(dict(sign=p['sign'], a_eid=p['a_eid'], b_eid=p['b_eid'], code=lang,
                    language=language, fold_length=fold, opportunity=bool(best),
                    a_form=best[1]['form'] if best else '', b_form=best[2]['form'] if best else '',
                    a_gloss=best[1]['gloss'] if best else '', b_gloss=best[2]['gloss'] if best else '',
                    normalized_edit_distance=best[0] if best else '', exact=bool(best and best[0] == 0)))
    write_csv('fixed_pair_portability.csv', rows, list(rows[0]))
    summary = []
    common = {(p['sign'], p['a_eid'], p['b_eid']) for p in pairs
              if all(by_lang_eid[(lg, p['a_eid'])] and by_lang_eid[(lg, p['b_eid'])]
                     for lg in ('Ta', 'Ma', 'Ka', 'Te'))}
    for fold in (False, True):
        for lang, language in LANGUAGES.items():
            rr = [r for r in rows if r['code'] == lang and r['fold_length'] == fold]
            cc = [r for r in rr if (r['sign'], r['a_eid'], r['b_eid']) in common and r['opportunity']]
            summary.append(dict(code=lang, language=language, fold_length=fold, fixed_claimed_pairs=len(pairs),
                opportunity_pairs=sum(r['opportunity'] for r in rr), exact_pairs=sum(r['exact'] for r in rr),
                major_four_common_pairs=len(common), common_opportunities=len(cc),
                common_exact_pairs=sum(r['exact'] for r in cc),
                common_mean_distance=sum(r['normalized_edit_distance'] for r in cc)/len(cc) if cc else None))
    write_csv('fixed_pair_summary.csv', summary, list(summary[0]))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
    design = json.loads((BASE / 'design.json').read_text())
    for p, sha in design['input_sha256'].items():
        if hashlib.sha256((REPO / p).read_bytes()).hexdigest() != sha:
            raise RuntimeError('Input mismatch: ' + p)
    OUT.mkdir(exist_ok=True)
    records, metadata = load_dictionary()
    write_csv('parsed_forms.csv', records, list(records[0]))
    coverage = []
    for lg, name in LANGUAGES.items():
        rr = [r for r in records if r['lang'] == lg]
        coverage.append(dict(code=lg, language=name, parsed_records=len(rr),
            etymon_groups=len({r['eid'] for r in rr}), unique_forms=len({norm(r['form']) for r in rr}),
            explicit_gloss_records=sum(not r['gloss_inferred_id'] for r in rr),
            id_gloss_records=sum(r['gloss_inferred_id'] for r in rr)))
    summary = dict(dictionary=metadata, dictionary_coverage=coverage,
                   unique_semantic_signs=len(design['domains']),
                   historical_specifications=len(design['historical_specs']),
                   key_affinity=key_affinity(records),
                   fixed_pair_portability=fixed_pair_portability(records, design['fixed_claimed_pairs']),
                   portability=portability(records, design['domains']))
    dump(OUT / 'summary.json', summary)
    write_csv('dictionary_coverage.csv', coverage, list(coverage[0]))
    write_csv('key_affinity_summary.csv', summary['key_affinity'], list(summary['key_affinity'][0]))
    write_csv('portability_summary.csv', summary['portability'], list(summary['portability'][0]))
    print('Wrote language-affinity results for', len(LANGUAGES), 'languages,',
          len(design['domains']), 'sign domains and', len(design['fixed_claimed_pairs']), 'fixed claimed pairs.')


if __name__ == '__main__':
    main()
