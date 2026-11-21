#!/usr/bin/env python3
"""Read-only independent audit of IVC work commit 8259c47.

Usage: python3 ivc_audit.py --repo /path/to/ivc --output audit.json
Requires only the Python standard library. Does not import repository code.
"""
import argparse
import ast
import collections
import csv
import json
import math
from pathlib import Path
import subprocess
import sys


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def coverage(rows, lexicon, numeric_only=False):
    faces = []
    for row in rows:
        tokens = [t.strip() for t in row["signs"].split("-") if t.strip()]
        if numeric_only:
            tokens = [t for t in tokens if t.isdigit()]
        if tokens:
            faces.append(tokens)
    total = sum(map(len, faces))
    covered = sum(t.zfill(3) in lexicon for f in faces for t in f)
    complete = [f for f in faces if all(t.zfill(3) in lexicon for t in f)]
    return dict(faces=len(faces), total_tokens=total, covered_tokens=covered,
                token_pct=100 * covered / total,
                fully_covered_faces=len(complete),
                fully_covered_pct=100 * len(complete) / len(faces),
                fully_covered_len3plus=sum(len(f) >= 3 for f in complete))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    rows = read_csv(repo / "work_data/reader_v3/corpus_soundfree_readings.csv")
    lex_rows = read_csv(repo / "work_data/key4_master/master_locked_lexicon.csv")
    lex = {r["sign"] for r in lex_rows}
    lipi = [r for r in rows if r["catalogue"] == "Lipi" and r["intact"] == "True"]
    new = [r for r in rows if r["catalogue"] != "Lipi" and
           r["partnered"] == "False" and r["intact"] == "True"]
    subsets = {"lipi": lipi, "unpartnered_new": new, "combined": lipi + new}
    results = {}
    for name, subset in subsets.items():
        results[name] = {
            "all_signs_retained": coverage(subset, lex),
            "master_numeric_filter": coverage(subset, lex, True),
        }
    false_complete = []
    for r in new:
        ts = r["signs"].split("-")
        numeric = [t for t in ts if t.isdigit()]
        if numeric and all(t.zfill(3) in lex for t in numeric) and not all(t.zfill(3) in lex for t in ts):
            false_complete.append({"id": r["id"], "signs": r["signs"]})
    stored = json.loads((repo / "work_data/key4_master/master_summary.json").read_text())
    for label, split in [("lipi", "lipi_intact_3600"), ("unpartnered_new", "new_intact_627"),
                         ("combined", "combined_intact_4227")]:
        reported = stored["results"][split]["T5_Master_Plus_ExtNumsMeas"]
        actual = results[label]["master_numeric_filter"]
        assert actual["total_tokens"] == reported["total_tokens"]
        assert actual["covered_tokens"] == reported["covered_tokens"]
        assert actual["fully_covered_faces"] == reported["faces_100pct"]
    syntax_errors = []
    scripts = sorted((repo / "work_scripts").glob("*.py"))
    for p in scripts:
        try:
            ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError as e:
            syntax_errors.append({"file": str(p.relative_to(repo)), "line": e.lineno, "message": e.msg})
    sequences = {r["signs"] for r in lipi}
    all_counts = collections.Counter(t for r in lipi + new for t in r["signs"].split("-"))
    source_counts = collections.Counter()
    for r in lex_rows:
        source_counts[r["source_lever"].split("(")[0]] += all_counts[r["sign"]]
    wave2 = read_csv(repo / "work_data/key4b/test4b1_top30_sign_table.csv")
    promoted = [r for r in wave2 if r["status"] == "building on it"]
    cup = next(r for r in read_csv(repo / "work_data/met/unit_ladder.csv") if r["unit_group"] == "cup")
    cup_dist = {int(k): int(v) for k, v in (s.split(":") for s in cup["value_distribution"].split())}
    grammar = ast.parse((repo / "work_scripts/typo_02_grammar_fit.py").read_text())
    score_func = next(n for n in grammar.body if isinstance(n, ast.FunctionDef) and n.name == "score_candidate_languages")
    candidate_assign = next(n for n in score_func.body if isinstance(n, ast.Assign) and
                            any(isinstance(t, ast.Name) and t.id == "CANDIDATES" for t in n.targets))
    candidates = ast.literal_eval(candidate_assign.value.args[0])
    sensitivity = {}
    for mode in ("original", "drop_G7", "drop_G5_G7", "halfway_to_0.5"):
        scores = {}
        for name, features in candidates:
            if name.startswith("North Munda"):
                continue
            probs = [v[0] for v in features.values()]
            weights = [.75, .5, .5, 1, 1, .5, 1]
            if mode == "drop_G7": weights[6] = 0
            if mode == "drop_G5_G7": weights[4] = weights[6] = 0
            if mode == "halfway_to_0.5": probs = [(p + .5) / 2 for p in probs]
            scores[name] = math.prod(p ** w for p, w in zip(probs, weights))
        sensitivity[mode] = 100 * next(v for k, v in scores.items() if k.startswith("Proto-Dravidian")) / sum(scores.values())
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    report = {
        "commit": sha, "python": sys.version, "coverage": results,
        "false_fully_covered_new_faces": false_complete,
        "new_faces_with_no_numeric_sign": sum(not any(t.isdigit() for t in r["signs"].split("-")) for r in new),
        "new_faces_with_sequence_already_in_lipi": sum(r["signs"] in sequences for r in new),
        "new_unique_sequences": len({r["signs"] for r in new}),
        "coverage_tokens_by_source": dict(source_counts),
        "promoted_wave2": {
            "n": len(promoted),
            "stem_p_below_0.05": sum(float(r["p_shuf_phonst"]) < .05 for r in promoted),
            "exact_p_below_0.05": sum(float(r["p_shuf_phonex"]) < .05 for r in promoted),
            "stem_p_below_0.05_div_30": sum(float(r["p_shuf_phonst"]) < .05 / 30 for r in promoted),
        },
        "cup_divisor_compatibility": {base: sum(v for k, v in cup_dist.items() if k < base and base % k == 0) / sum(cup_dist.values()) for base in [12, 24, 36, 60]},
        "assigned_likelihood_score_sensitivity_pct": sensitivity,
        "syntax_checked_scripts": len(scripts), "syntax_errors": syntax_errors,
        "stored_T5_counts_reproduced": True,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
