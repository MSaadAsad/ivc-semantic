"""Extract factual source tables and labelled illustrations; do not invent sign readings."""
import argparse
import collections
import csv
import json
import hashlib
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile

BASE = Path(__file__).resolve().parent
INPUT = BASE / 'online_expansion_inputs'
NS = {'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
COLS = ['raw_cisi','formative','additive','features','extractive','subtractive','right_behavior','left_behavior',
        'source_f3_signs_mahadevan'] + [f'{kind}_face_{face}' for kind in ['seal','impression'] for face in 'ABCDEF']


def canonical(text):
    text = text.strip().replace('–','-').replace('−','-')
    match = re.fullmatch(r'([A-Za-z]+)\s*-\s*0*(\d+)',text)
    return f'{match[1].lower()}-{int(match[2])}' if match else ''


def write(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)


def compare_versions(old_path):
    """Compare common source fields, preserving labelled rows and whitespace variants."""
    blob=old_path.read_bytes()
    archived_match=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()=='680420e98c40c66ef3edcc9d115c821133760ccc'
    assert archived_match,'The public 2022 file differs from the locally recorded archived workbook; review the baseline before comparing.'
    fields=COLS[:8]+COLS[9:]
    old=[]
    with zipfile.ZipFile(old_path) as z:
        shared=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('s:sheetData/s:row',NS):
            n=int(row.get('r'))
            if not 6<=n<=2410:continue
            cells={}
            for c in row.findall('s:c',NS):
                v=c.find('s:v',NS);value=v.text if v is not None else ''
                if c.get('t')=='s':value=shared[int(value)] if value else ''
                cells[re.sub(r'\d','',c.get('r'))]=value
            if cells.get('A',''):
                old.append(dict(source_row=n,**dict(zip(fields,[cells.get(chr(65+i),'') for i in range(20)]))))
    with (INPUT/'animal2024_rows.csv').open() as f:new=[r for r in csv.DictReader(f) if r['source_named_row']=='True']
    def key(r):
        raw=r['raw_cisi'].strip().replace('–','-').replace('−','-')
        match=re.fullmatch(r'([A-Za-z]+)\s*-\s*0*(\d+)\s*(i?)',raw)
        return f'{match[1].lower()}-{int(match[2])}{match[3]}' if match else raw.lower()
    def group(records):
        result=collections.defaultdict(list)
        for r in records:result[key(r)].append(r)
        return result
    a,b=group(old),group(new);common=set(a)&set(b);changes=[]
    for ref in sorted(common):
        for field in fields[1:]:
            av=sorted({r[field].strip() for r in a[ref]});bv=sorted({r[field].strip() for r in b[ref]})
            if av!=bv:changes.append(dict(reference=ref,field=field,old=json.dumps(av,ensure_ascii=False),new=json.dumps(bv,ensure_ascii=False)))
    write(INPUT/'animal2022_named_records.csv',old)
    write(INPUT/'animal_version_changes.csv',changes)
    summary=dict(old_named_rows=len(old),old_distinct_normalized_reference_labels=len(a),new_named_rows=len(new),
                 new_distinct_normalized_reference_labels=len(b),common_normalized_reference_labels=len(common),
                 new_only_reference_labels=sorted(set(b)-set(a)),old_only_reference_labels=sorted(set(a)-set(b)),
                 changed_reference_labels=len({r['reference'] for r in changes}),changed_common_field_groups=len(changes),
                 new_f3_coding_named_rows=sum(bool(r['source_f3_signs_mahadevan']) for r in new),new_column='source_f3_signs_mahadevan',
                 baseline_byte_identical_to_archived_workbook=archived_match,
                 comparison_scope='Named source rows, common fields aggregated as value sets by normalized reference. Whitespace and numeric zero padding normalized; suffix i retained. Changes include terminology and label corrections, not necessarily new archaeological observations.')
    (INPUT/'animal_version_summary.json').write_text(json.dumps(summary,indent=2)+'\n')


def extract(cache, metadata):
    INPUT.mkdir(exist_ok=True)
    with zipfile.ZipFile(cache/'animal_catalogue2024.xlsx') as z:
        shared = [''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        rows = []
        previous = ''
        for row in sheet.findall('s:sheetData/s:row',NS):
            n = int(row.get('r'))
            # Rows 1–5 are the multirow header; 2381–2383 are illegibility/legend/exclusion notes.
            if not 6 <= n <= 2380:
                continue
            cells = {}
            for c in row.findall('s:c',NS):
                v = c.find('s:v',NS);value = v.text if v is not None else ''
                if c.get('t') == 's':
                    value = shared[int(value)] if value else ''
                elif c.get('t') == 'inlineStr':
                    value = ''.join(c.itertext())
                cells[re.sub(r'\d','',c.get('r'))] = value
            values = [cells.get(chr(65+i),'') for i in range(21)]
            named = bool(values[0])
            if named:
                previous = canonical(values[0])
            rows.append(dict(source_row=n,source_named_row=named,source_canonical_id=canonical(values[0]),
                             preceding_named_canonical_id=previous if not named else '',
                             continuation_scope='preceding row-group only; no independent object counted' if not named else '',
                             **dict(zip(COLS,values))))
        # Preserve all trailing source notes verbatim as source context, outside the analytical table.
        notes=[]
        for row in sheet.findall('s:sheetData/s:row',NS):
            if int(row.get('r'))<2381:continue
            for c in row.findall('s:c',NS):
                v=c.find('s:v',NS)
                if v is not None and c.get('t')=='s':notes.append(dict(cell=c.get('r'),source_text=shared[int(v.text)]))
    write(INPUT/'animal2024_rows.csv',rows)
    write(INPUT/'animal2024_source_notes.csv',notes)
    compare_versions(cache/'animal_catalogue2022.xlsx')
    references={r['source_canonical_id'] for r in rows if r['source_canonical_id']}
    references.update(canonical(r['cisi']) for r in csv.DictReader((INPUT/'frontal33_review.csv').open()))
    with metadata.open() as f:
        old=[r for r in csv.DictReader(f) if canonical(r['cisi']) in references]
    fields=['id','cisi','site','symbol','cult','type','material','area-section','block-house','room-grid','excavation-idno','period','phase','time','depth','text']
    write(INPUT/'existing_animal_metadata.csv',[{k:r[k] for k in fields} for r in old])
    # The PDF embeds some photos beyond their visible cell, so crop displayed table cells rather than infer identity from raw image bboxes.
    import fitz
    doc=fitz.open(cache/'animal_frontal33.pdf')
    images=INPUT/'images';images.mkdir(exist_ok=True)
    image_rows=[]
    expected=[range(1,6),range(6,11),range(11,17),range(17,23),range(23,29),range(29,34)]
    for page_index, expected_rows in enumerate(expected):
        page=doc[page_index]
        starts={int(w[4]):w[1] for w in page.get_text('words') if 50<w[0]<72 and w[4].isdigit() and int(w[4]) in expected_rows}
        assert set(starts)==set(expected_rows),(page_index,starts)
        ordered=sorted(starts.items())
        for i,(number,y) in enumerate(ordered):
            bottom=ordered[i+1][1]-2 if i+1<len(ordered) else (590 if page_index==5 else 775)
            filename=f'frontal-{number:02}.jpg'
            page.get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(73,y-2,246,bottom)).save(images/filename)
            image_rows.append(dict(file=filename,source='Bhaskar 2024 ESM1',source_pdf_page=page_index+1,source_row=number,
                                   source_url='https://static-content.springer.com/esm/art%3A10.1007%2Fs43539-023-00102-3/MediaObjects/43539_2023_102_MOESM1_ESM.pdf',
                                   treatment='Displayed image/reference table cell cropped from original PDF; no restoration or inferred signs.'))
    binjor=fitz.open(cache/'binjor_photo_reproduction.pdf')
    pictures=binjor[16].get_images(full=True)
    # Source page 17 contains a map, the seal photo, and a hearth photo, in that order.
    seal=binjor.extract_image(pictures[1][0]);assert (seal['width'],seal['height'])==(464,334)
    (images/'binjor-unicorn-photo.jpeg').write_bytes(seal['image'])
    image_rows.append(dict(file='binjor-unicorn-photo.jpeg',source='Photograph reproduced in Kalyanaraman compilation; original credited to S. Subramanium / Frontline 2015',
                           source_pdf_page=17,source_row='',source_url='https://faculty.fordham.edu/vinod/kalyanaraman2021.pdf',
                           treatment='Unmodified embedded photograph. Secondary reproduction only; Vedic/metalwork interpretations are not adopted. No numeric transcription asserted.'))
    write(INPUT/'image_sources.csv',image_rows)
    print(dict(worksheet_data_rows=len(rows),named_rows=sum(r['source_named_row'] for r in rows),
               canonical_ids=len({r['source_canonical_id'] for r in rows if r['source_canonical_id']}),
               frozen_existing_faces=len(old),illustrated_frontal_rows=len(image_rows)-1,binjor_photos=1))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,required=True);parser.add_argument('--metadata',type=Path,required=True)
    args=parser.parse_args();extract(args.cache,args.metadata)
