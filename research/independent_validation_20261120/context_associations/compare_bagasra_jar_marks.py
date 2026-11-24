"""Screen the excavator's verbal description of BSR J1 against Lipi.

The grouped codes come from the shape descriptions in sign_shapes.csv.
The source drawing is needed to choose among them or identify a compound glyph.
"""
import csv
from pathlib import Path


CATALOGUE = (
    Path(__file__).resolve().parents[1]
    / "translation_catalogue/results/all_inscriptions.csv"
)
PLAIN_CARET = {"480"}
SIDE_STROKE_FISH = {"226", "227", "228", "232", "234", "236", "240", "241", "242"}
MORE_CARETS = {"066", "482", "483", "484"}
MORE_FISH = {"220", "222", "231", "233", "235", "243", "244"}
TWO_STROKES = [("002",), ("032",), ("001", "001"), ("031", "031")]


def ordered_patterns(carets, stroke_codes, fish):
    forward = {(caret, *strokes, animal) for caret in carets
               for strokes in stroke_codes for animal in fish}
    return forward | {pattern[::-1] for pattern in forward}


def matching_faces(faces, patterns):
    lengths = {len(pattern) for pattern in patterns}
    for row in faces:
        signs = row["sign_sequence"].split("-")
        if any(
            tuple(signs[start:start + length]) in patterns
            for length in lengths
            for start in range(len(signs) - length + 1)
        ):
            yield row


def main():
    with CATALOGUE.open(newline="", encoding="utf-8") as catalogue:
        faces = [row for row in csv.DictReader(catalogue) if row["catalogue"] == "Lipi"]

    broad_carets = PLAIN_CARET | MORE_CARETS
    broad_fish = SIDE_STROKE_FISH | MORE_FISH
    screens = [
        ("Plain caret, two strokes, fish with extra strokes",
         ordered_patterns(PLAIN_CARET, TWO_STROKES, SIDE_STROKE_FISH)),
        ("Expanded shapes, two strokes",
         ordered_patterns(broad_carets, TWO_STROKES, broad_fish)),
        ("Expanded shapes, one stroke",
         ordered_patterns(broad_carets, [("001",), ("031",)], broad_fish)),
    ]
    print(f"{len(faces):,} Lipi faces. Both orientations, contiguous signs.")
    for name, patterns in screens:
        matches = list(matching_faces(faces, patterns))
        print(f"\n{name}: {len(patterns)} strings, {len(matches)} faces")
        for row in matches:
            print(
                row["reference"], row["face_id"], row["object_type"],
                row["sign_sequence"], row["existing_proposed_translation"], sep=" | "
            )


if __name__ == "__main__":
    main()
