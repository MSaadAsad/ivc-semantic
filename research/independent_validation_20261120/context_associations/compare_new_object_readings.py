"""Compare observed sign candidates without adding them to the reference corpus."""

import csv
from collections import Counter
from pathlib import Path

from compare_bagasra_jar_marks import CATALOGUE, matching_faces


KEY = Path(__file__).resolve().parents[3] / "work_data/key6a/master_lexicon_after_key6a.csv"


def describe(faces, label, patterns):
    hits = list(matching_faces(faces, patterns))
    exact = [row for row in hits if tuple(row["sign_sequence"].split("-")) in patterns]
    object_types = Counter(row["object_type"].split(":")[0] for row in hits)
    objects = len({row["object_identifier"] for row in hits})
    print(f"{label}: {len(hits)} faces on {objects} objects, {len(exact)} whole faces")
    print("  Object types:", dict(sorted(object_types.items())))
    for row in exact:
        print(f"  {row['reference']} {row['sign_sequence']} {row['existing_proposed_translation']}")
    return hits


def repeat_pattern(sequence):
    codes = {}
    return tuple(codes.setdefault(token, len(codes)) for token in sequence)


def bone_patterns(faces):
    # The excavator's letters describe shapes. Their repeated positions alone are tested.
    observed = "INIXIXX"
    expected = {repeat_pattern(observed), repeat_pattern(reversed(observed))}
    for catalogue in sorted({row["catalogue"] for row in faces}):
        eligible = 0
        same_counts = 0
        order_matches = 0
        for row in faces:
            if row["catalogue"] != catalogue:
                continue
            signs = row["sign_sequence"].split("-")
            for start in range(len(signs) - 6):
                window = signs[start:start + 7]
                if any(len(sign) != 3 or not sign.isdecimal() or sign == "000" for sign in window):
                    continue
                eligible += 1
                same_counts += sorted(Counter(window).values()) == [1, 3, 3]
                order_matches += repeat_pattern(window) in expected
        print(f"Bone, {catalogue}: {eligible} windows, {same_counts} with counts 3/3/1,"
              f" {order_matches} with observed order")


def main():
    with CATALOGUE.open(newline="", encoding="utf-8") as catalogue:
        faces = list(csv.DictReader(catalogue))
    with KEY.open(newline="", encoding="utf-8") as source:
        key = {row["sign"]: row["root_or_gloss"] for row in csv.DictReader(source)}
    lipi = [row for row in faces if row["catalogue"] == "Lipi"]
    print(f"Lipi reference: {len(lipi):,} faces")
    print("Key 6A:", {sign: key[sign] for sign in ("820", "032", "405", "407", "220", "480")})

    describe(lipi, "J101 wheel followed by tall two", {("820", "032")})
    describe(lipi, "J101 wheel followed by short two", {("820", "002")})
    describe(lipi, "J101 both stroke heights, reverse", {("032", "820"), ("002", "820")})

    four_and_branch = {(n, sign) for n in ("004", "034") for sign in ("405", "407")}
    describe(lipi, "6606 four followed by branched variants", four_and_branch)
    describe(lipi, "6606 branched variants followed by four", {pair[::-1] for pair in four_and_branch})

    describe(lipi, "Rakhigarhi ingot plain fish candidate", {("220",)})
    hits = describe(lipi, "Rakhigarhi one stroke and plain fish, either order", {
        ("001", "220"), ("031", "220"), ("220", "001"), ("220", "031"),
    })
    for row in hits:
        if row["object_type"].startswith("POT"):
            print(f"  Pottery comparator: {row['reference']} {row['existing_proposed_translation']}")
    print("  Faces with recorded lead:", sum("lead" in row["material"].casefold() for row in lipi))

    describe(lipi, "Plain caret followed by two, without fish", {("480", "002"), ("480", "032")})
    bone_patterns(faces)


if __name__ == "__main__":
    main()
