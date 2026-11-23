"""Build a shareable scientific chart from the released measurements/predictions.

Requires matplotlib and Pillow. The archaeological drawing is extracted unchanged
from the attributed source underlay already embedded in h95_profile_overlay.svg.
No archaeological image is generated and no model is refitted here.
"""
import base64
import csv
import io
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image

BASE = Path(__file__).resolve().parent
OUT = BASE / 'results'
BG, INK, MUTED = '#f6f4ef', '#23383c', '#56686a'
BLUE, GOLD, GREEN = '#287ba3', '#a76c15', '#49795b'
MODELS = [('diameter_length', 'Width', BLUE),
          ('circular_section_area', 'Cross-section area', GOLD),
          ('interior_volume', 'Interior capacity', GREEN)]
W, H = 1600, 1800


def read(name):
    with (OUT / name).open(newline='') as f:
        return list(csv.DictReader(f))


def main():
    data = {r['id']: r for r in read('dimension_eligible_measurements.csv') if r['primary'] == 'True'}
    summary = json.loads((OUT / 'dimension_summary.json').read_text())
    predictions = {r['model']: r for r in summary['h95_predictions']}
    scores = {r['model']: r for r in summary['primary_scores']}
    assert len(data) == 4 and summary['primary_objects'] == 4
    assert all(r['actual_count'] == 4 for r in predictions.values())
    overlay = ET.parse(OUT / 'h95_profile_overlay.svg').getroot()
    src = overlay.find('{http://www.w3.org/2000/svg}image').attrib['href']
    drawing = Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1])))

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none',
                         'svg.hashsalt': 'ivc-jar-marks-comparison'})
    fig = plt.figure(figsize=(16, 18), dpi=140, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, W), ylim=(H, 0))
    ax.axis('off')

    def txt(x, y, text, size=15, color=INK, bold=False, **kwargs):
        return ax.text(x, y, text, fontsize=size, color=color,
                       fontweight='bold' if bold else 'normal', va='top', **kwargs)

    def box(x, y, w, h, fill='white', edge='none', radius=12):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={radius}',
                                   facecolor=fill, edgecolor=edge, linewidth=1))

    def tally(x, y, n, color=INK):
        for i in range(n):
            ax.plot([x+i*12, x+i*12], [y, y+28], color=color, lw=2.7, solid_capstyle='round')

    txt(60, 48, 'What do the jar marks measure?', 32, bold=True)
    txt(60, 110, 'Four Harappa jars • published measurements + an additional profile reconstruction', 15, MUTED)
    txt(60, 147, 'Compare width, cross-section area and capacity against the same proposed mark counts.', 15)

    txt(60, 218, '1   THE ARCHAEOLOGICAL EXAMPLE', 13, MUTED, True)
    box(60, 258, 390, 520)
    image_ax = fig.add_axes([76/W, 1-762/H, 358/W, 488/H])
    image_ax.imshow(drawing)
    image_ax.axis('off')
    txt(60, 794, 'Published drawing, not a photograph or generated image.', 10, MUTED)

    txt(510, 218, 'H95-2661/6640-501 • Harappa', 23, bold=True)
    tally(514, 279, 4)
    txt(588, 278, '4 marks = proposed reading “four”', 18, bold=True)
    txt(510, 325, 'Catalogue rim sign 034; other body marks are a separate inscription.', 12, MUTED)
    chips = [(510, 'WIDTH', '58 cm', 'Maximum external diameter', BLUE),
             (860, 'CROSS-SECTION AREA', '2,642 cm²', 'Calculated as π × diameter² ÷ 4', GOLD),
             (1210, 'INTERIOR CAPACITY', '88.9 L', 'Reconstructed to the rim', GREEN)]
    for x, label, value, explanation, color in chips:
        box(x, 375, 330, 124)
        txt(x+18, 389, label, 10, color, True)
        txt(x+18, 418, value, 24, color, True)
        txt(x+18, 465, explanation, 10, MUTED)

    txt(510, 531, 'What do the other three jars predict for this jar?', 18, bold=True)
    txt(510, 568, 'Learn one unit from those three; use this jar’s measurement to predict its count.', 11, MUTED)
    x0, unit = 850, 112
    actual_x = x0+4*unit
    ax.plot([actual_x, actual_x], [614, 781], color=INK, lw=1.5, linestyle=(0, (4, 4)))
    txt(actual_x, 604, 'Actual: 4', 11, bold=True, ha='center')
    for (model, label, color), y in zip(MODELS, [652, 705, 758]):
        predicted = predictions[model]['predicted_count']
        txt(510, y-12, label, 15, color, True)
        ax.plot([x0, x0+5*unit], [y, y], color='#d8ddda', lw=2)
        ax.plot([x0, x0+predicted*unit], [y, y], color=color, lw=4, alpha=.5)
        ax.scatter([x0+predicted*unit], [y], s=100, color=color, zorder=4)
        txt(x0+predicted*unit, y-30, f'{predicted:.2f}', 13, color, True, ha='center')
    for i in range(6):
        txt(x0+i*unit, 789, str(i), 10, MUTED, ha='center')
    txt(1550, 789, 'marks', 10, MUTED, ha='right')

    txt(60, 855, '2   THE SAME FOUR JARS, SIDE BY SIDE', 13, MUTED, True)
    txt(60, 890, 'Marks below are schematic tallies of source counts, not facsimiles of the inscriptions.', 12, MUTED)
    box(60, 937, 1480, 356)
    ax.add_patch(plt.Rectangle((60, 937), 1480, 59, color=INK))
    for x, label in [(83, 'Vessel / role'), (450, 'Marks / count'), (815, 'Width (cm)'),
                     (1080, 'Area (cm²)'), (1360, 'Capacity (L)')]:
        txt(x, 956, label, 13, 'white', True, ha='center' if x >= 815 else 'left')
    for i, identifier in enumerate(['H-372', 'H-371', 'H-370', 'H95-2661']):
        r = data[identifier]
        y = 997+i*74
        if identifier == 'H95-2661':
            ax.add_patch(plt.Rectangle((60, y), 1480, 74, color='#e3ece4'))
        elif i%2 == 0:
            ax.add_patch(plt.Rectangle((60, y), 1480, 74, color='#f0f1ee'))
        txt(83, y+11, identifier, 16, bold=True)
        txt(83, y+42, 'Additional jar' if identifier == 'H95-2661' else 'Original calibration jar', 10, MUTED)
        tally(453, y+21, int(r['count']))
        txt(590, y+21, r['count'], 17, bold=True)
        d = float(r['diameter_cm'])
        for x, value, color in [(815, f'{d:.1f}', BLUE),
                                 (1080, f'{math.pi*d*d/4:,.0f}', GOLD),
                                 (1360, f'{float(r["volume_l"]):.1f}', GREEN)]:
            txt(x, y+21, value, 17, color, True, ha='center')

    txt(60, 1330, '3   OVERALL FIT: PREDICT EACH JAR’S COUNT FROM THE OTHER THREE', 13, MUTED, True)
    for (model, label, color), x in zip(MODELS, [60, 565, 1070]):
        box(x, 1372, 470, 123)
        txt(x+22, 1387, label, 15, color, True)
        value = scores[model]['mean_absolute_percentage_count_error']
        txt(x+22, 1424, f'{value:.0f}%', 30, color, True)
        txt(x+147, 1443, 'average count error', 13, MUTED)
    txt(60, 1514, 'Lower error = closer predictions. Ignoring dimensions gives 44% average count error.', 12, MUTED)

    box(60, 1566, 1480, 117, fill='#e9e4d9')
    txt(82, 1581, 'Area fits the four-jar panel best; width best predicts the additional jar.', 19, bold=True)
    txt(82, 1622, 'The original three favor volume. Including uncertain cases can change the winner.', 13)
    txt(82, 1650, 'This does not identify an ancient unit, a language, or accounts for cloth length / land area.', 12, MUTED)

    txt(60, 1706, 'Sources: Kenoyer, Fig. 7.2 (drawing); Fuls 2012, Tables 1–3 (dimensions / original capacities); released H95 inner-profile trace.', 9, MUTED)
    txt(60, 1730, 'Source limits: Fuls table layout not visually verified; H95 accession/caption conflict and candidate H-2263 join retained in the source notes.', 9, MUTED)
    txt(60, 1754, 'One drawing shown; four objects tested. Redrawn marks show the numerical hypothesis only. Calculations and source links accompany this chart.', 9, MUTED)
    for ext in ['png', 'svg']:
        destination = OUT / f'jar_marks_comparison.{ext}'
        metadata = {'Date': None} if ext == 'svg' else None
        fig.savefig(destination, dpi=140, facecolor=BG, metadata=metadata)
        if ext == 'svg':
            destination.write_text('\n'.join(line.rstrip() for line in destination.read_text().splitlines())+'\n')
    plt.close(fig)
    print('Created jar_marks_comparison.png and jar_marks_comparison.svg from released results.')


if __name__ == '__main__':
    main()
