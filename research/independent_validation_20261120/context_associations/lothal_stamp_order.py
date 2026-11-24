"""Join manual plate observations to Lothal inventory and unchanged Lipi readings."""
from collections import Counter
import csv
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results/lothal_stamp_order"


def load(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def save(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    inventory = {
        row["cisi"]: row
        for row in load(BASE / "results/lothal_tables/all_93_sealings.csv")
        if int(row["impressions"]) > 1
    }
    review = load(RESULTS / "plate_review.csv")
    assert len(review) == len(inventory)
    assert {row["reference"] for row in review} == set(inventory)
    for row in review:
        entry = inventory[row["reference"]]
        row["published_impressions"] = entry["impressions"]
        row["physical_support"] = entry["container"]
        row["find_context"] = entry["context"]
        row["existing_proposed_translations"] = entry["proposed_translations"]
    save(RESULTS / "review_with_context.csv", review)

    catalogue = BASE.parent / "translation_catalogue/results/all_inscriptions.csv"
    readings = {
        row["face_id"]: row
        for row in load(catalogue)
        if row["catalogue"] == "Lipi" and row["reference"] in inventory
    }
    alignment = load(RESULTS / "panel_alignment.csv")
    assert len({(row["reference"], row["printed_panel"]) for row in alignment}) == len(alignment)
    assert len({row["lipi_face"] for row in alignment}) == len(alignment)
    for row in alignment:
        entry = readings[row["lipi_face"]]
        assert row["reference"] == entry["reference"]
        row["sequence"] = entry["sign_sequence"]
        row["existing_proposed_translation"] = entry["existing_proposed_translation"]
        row["ordinal_agrees"] = row["printed_panel"][1:] == row["lipi_face"].split(".")[-1]
    save(RESULTS / "aligned_readings.csv", alignment)
    mismatches = {
        row["reference"]
        for row in alignment
        if row["assessment"] == "supported" and not row["ordinal_agrees"]
    }
    summary = {
        "sealing_objects_reviewed": len(review),
        "published_impressions_on_reviewed_objects": sum(int(row["published_impressions"]) for row in review),
        "physical_assessments": dict(Counter(row["physical_assessment"] for row in review)),
        "objects_with_supported_panel_ordinal_mismatch": sorted(mismatches),
        "secure_name_quantity_order_comparisons": 0,
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
