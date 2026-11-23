# Vessel-capacity sources and prior work

Accessed 22 November 2026. A catalogue reference, an excavation accession and a book's plate/item number are different namespaces. They are not merged because their digits resemble one another. Original scans remain outside this repository; the source-derived crop/trace is included for scientific inspection with attribution.

## 1. Primary scaled drawing: additional Harappa jar

J. M. Kenoyer, *The Origin, Context and Function of the Indus Script: Recent Insights from Harappa*. [Original Harappa-hosted version](https://www.harappa.com/sites/default/files/pdf/Kenoyer2006_The%20Origin%2C%20Context%20and%20Function%20of%20the%20Indus%20Sc.pdf); [journal-hosted reprint PDF](https://mohenjodarorj.sindhila.org/index.php/journal/article/download/105/81), [2025 hosting metadata](https://mohenjodarorj.sindhila.org/index.php/journal/article/view/105).

The later hosting date is not a new excavation date. The reprint supplies the same older archaeological illustration, Figure7.2, printed156/PDF21. The figure has a labelled0–20cm scale and an interior section. The drawing says **H95-2661/6640-501**, while its caption says **H95-2662/6640-501**. The catalogue candidate H-2263 has raw excavation string **H95-2661640-0501**, retaining the drawing's accession2661 but a differently recorded unit. The match is an accession-based candidate with these conflicts preserved; no raw catalogue correction is made. Fuls's account independently names2661 and unit6640-501.

The rim is proposed as four strokes in both the source discussion and the catalogue. The figure also shows body graffiti and pre-firing potter's marks. **A rim-only catalogue transcription is not a complete transcription of every mark on this vessel.** Kenoyer's pp.150–151 discuss rim marks as possible accounting quantities, not established full-capacity labels.

Direct downloads returned403 from Harappa and406 from the journal. The same public primary PDF was recovered from a [public Git-LFS mirror](https://media.githubusercontent.com/media/chinmaymk/indus-script/main/data/raw/kenoyer_sindhila_inscribed_pottery.pdf). The [mirror pointer](https://github.com/chinmaymk/indus-script/blob/main/data/raw/kenoyer_sindhila_inscribed_pottery.pdf) records1,973,375bytes and SHA256 `094f3b1b451cef378490ac3c95ba6ab73a62ae718ade0a433262c8fe3825efcc`; downloaded bytes match. This verifies mirror-file identity, not every archaeological assertion. The PDF page and embedded696×803 illustration (xref101) were inspected visually. The trace uses native image coordinates and a149px20cm scale; the full source PDF is not redistributed.

## 2. Published eight-vessel reconstruction inventory

Andreas Fuls (2012), *Volumenmaße von Tongefäßen der Induskultur*, in Sven Weisbrich and Robert Kaden, eds., *Entwicklerforum Geoinformationstechnik2011*, pp.101–114, Shaker. Bibliography corroborated on the [authors' ICIT page](https://epigraphica.de/indus/menueindus.htm). [Author-posted public text](https://www.academia.edu/8808307/VOLUMENMA%C3%9FE_VON_TONGEF%C3%84%C3%9FEN_DER_INDUSKULTUR).

Inspected sections2–5, Tables1–3 and figure descriptions. Direct download returned403; **the original PDF table layout was not visually verified**. All eight Table3 rows are transcribed into `inputs/fuls2012_inventory.csv`; uncertainty is retained. The relevant source reports are:

| Source ID | Profile capacity reported, L | Stroke count as reported | Qualification |
|---|---:|---:|---|
| H95-2661 |88.3|4|Additional scaled jar, traced afresh here from Kenoyer's illustration.|
| MD-1374 |138.8|6|Three vertical and three oblique marks; not automatically six equivalent tall strokes. Exact catalogue join absent.|
| MD-63-3 |40.3|1?|Mackay LXIII:3; tentative number, not a fixed current capacity reading.|
| H-372 |121.0|3|Original calibration jar, based on Wells2009 measurements; not a new observation.|
| H-371 |240.6|6|Original calibration jar; not a new observation.|
| H-370 |283.8|7|Original calibration jar; not a new observation.|
| K-90 |103.0|2|Exterior photograph rectified using an interpreted30cm scale; absolute scale remains conditional.|
| MD-63-6 |52.8|1?|Mackay LXIII:6; tentative number, not a fixed current capacity reading.|

Fuls reports maximum diameter58cm and exterior height71cm for H95-2661; these are comparison information, not the scale imposed on our trace. The source's H95 capacity was known before tracing. Its original three Harappa jar profiles reuse Wells's2009 measurements, so they do not supply independent physical measurements of those objects. Its volume models differ by up to8% for those jars.

Source inconsistencies remain visible: Table1 assigns12908 to H-372 and1033b to H-370, while the imported catalogue assigns12908 to H-370 and gives no accession for H-372. K-90's running discussion mentions56.7L/stroke while Table3 gives103L divided by2=51.5. These differences are not silently repaired. No calibrated prediction for K-90 is scored from them.

The two Mackay plate links match the catalogue's explicit `DK8990LXIII:3` (M-2063) and `DK7286LXIII:6` (M-2061). These links are textual plate-reference joins; the original Mackay profile plates were not newly traced. MD-1374 in the Fuls paper is not equated with CISI M-1374, whose catalogue accession is UPM/MD-138 and whose object type is a stamped sherd. Similar numbers cannot supply that crosswalk.

## 3. Later primary account of the three original jars

Bryan K. Wells (2015), *The Archaeology and Epigraphy of Indus Writing*, Archaeopress, chapter4, pp.55–65, especially pp.61–62. [Publicly readable book text](https://ru.scribd.com/document/1007007442/The-Archaeology-and-Epigraphy-of-Indus-Writing-Bryan-K-Wells-Andreas-Fuls-Archaeopress-Publishing-Ltd-Oxford-2015-Archaeopress-Publishing).

The author's running text describes measuring the Purana Qila vessels in2009, notes that a stand was removed from the H-372 catalogue photograph, and estimates **40.4L per tall stroke**. This differs from the repo's9.24L conversion based on an older news summary. Its K-90 discussion explicitly says the photo scale units are unknown; assuming5cm increments lets that jar approximately fit the proposed system. That is a conditional check, not independent scale calibration.

The public text was inspected without logging in, restricted access or downloading a complete book. Tables4.1/4.2 were not visually authenticated. The40.4 value is directly stated in the prose, independently of the Fuls table-text extraction. This task does not establish why the older reported27.30/55.56/65.89L figures differ; it therefore does not diagnose a conversion, arithmetic or transcription error as the cause.

## 4. K-90 primary catalogue photograph

J. P. Joshi and A. Parpola, eds. (1987), *Corpus of Indus Seals and Inscriptions*, Vol.I: *Collections in India*, printed319. [Public institutional scan](https://ignca.gov.in/Asi_data/76884.pdf), recovered from a [public scan mirror](https://media.githubusercontent.com/media/chinmaymk/indus-script/main/data/raw/cisi_76884.pdf).

The31,508,998-byte mirror matches SHA256 `47a4da4227cfb7baa56d6a561e25797225499d0ec54f5a702a82c67ab4746d4d`. Printed319 is PDF355. This page was rendered and visually inspected: K-90A1 has two rim strokes, K-90A2 shows the distinct body inscription, and the whole-vessel photo has an **unlabelled** bar/block feature below it. No independently labelled centimetre scale was recovered on that page. The scan contains862PDF pages, reportedly two copies of the book; the second half was not reviewed or counted as more evidence.

## Prior work, discovery route and independence

- Cúper's `met_03_physical.py` already fits the three news-derived jar capacities, estimates M-2066 with an assumed shape/wall thickness, and tests pottery wall thickness. Those analyses are not rerun as new evidence. The fixed9.24 value also appears in `measures_4_scale.py` and related reports. The new screen extracts the original pure parser definitions with Python AST, without importing modules that create upstream logs or running old analyses.
- Targeted searches of materialized `work_scripts`, `jobs/out` and `work_data/met` found no H95-2661 profile integration, no test of its four-stroke capacity prediction, and no Fuls eight-vessel comparison. K-90's signs/ownership already occur upstream; its presence there is credited. This is a bounded implementation finding, not a claim that every historical blob or source ever read by Cúper was checked.
- Search surfaced [chinmaymk/indus-script](https://github.com/chinmaymk/indus-script), whose [H95 profile study](https://github.com/chinmaymk/indus-script/blob/main/docs/H95_PROFILE_CAPACITY.md) already traces this drawing and reports85.96L. That work supplied a source-location and public-copy lead. **This is not the first published analysis of the vessel or the first digital trace.** No coordinates or analysis code were copied from it. Our fresh trace returns88.90L; seeing its result and Fuls's88.3 before tracing prevents a claim of blinding.
- Fuls's metrology study and Wells's primary account also predate this project. The addition here is the comparison against **Cúper's unchanged9.24L/stroke prediction**, the source reconciliation, full exclusions, actual catalogue readings and a reproducible contour/sensitivity calculation. One additional jar is a case test, not a general decipherment success/failure rate.
