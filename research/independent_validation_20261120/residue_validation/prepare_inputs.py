"""Extract public sample tables without inventing inscription identifications.

Usage: python prepare_inputs.py --source-dir /path/to/downloaded-sources
The source URLs and scope are recorded in SOURCES.md. No PDFs are republished.
"""
import argparse,csv,re,shutil,xml.etree.ElementTree as ET,zipfile
from html.parser import HTMLParser
from pathlib import Path
BASE=Path(__file__).resolve().parent
class Tables(HTMLParser):
    def __init__(self):super().__init__();self.tables=[];self.table=None;self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='table':self.table=[]
        elif tag=='tr' and self.table is not None:self.row=[]
        elif tag in {'td','th'} and self.row is not None:self.cell=''
    def handle_data(self,s):
        if self.cell is not None:self.cell+=s
    def handle_endtag(self,tag):
        if tag in {'td','th'} and self.cell is not None:self.row.append(' '.join(self.cell.split()));self.cell=None
        elif tag=='tr' and self.row is not None:self.table.append(self.row);self.row=None
        elif tag=='table' and self.table is not None:self.tables.append(self.table);self.table=None
def main(source_dir):
    out=BASE/'inputs';out.mkdir(exist_ok=True)
    src=Path(source_dir)
    shutil.copy2(src/'northwest2021-data.csv',out/'northwest2021_original_data.csv')
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tree=ET.fromstring(zipfile.ZipFile(src/'kotada2020-supp.docx').read('word/document.xml'))
    table=tree.findall('.//w:tbl',ns)[0]
    values=[[' '.join(x.text or '' for x in c.findall('.//w:t',ns)) for c in r.findall('w:tc',ns)] for r in table.findall('w:tr',ns)]
    samples=[r for r in values if r and re.fullmatch(r'(?:KB|A)-\d+',r[0])]
    assert len(samples)==59 and all(len(r)==15 for r in samples)
    cols=['sample_id','vessel_shape','fabric','surface_treatment','vessel_part','molecular_description','extraction_method','total_yield_text','C16_yield_ug_g','C18_yield_ug_g','tentative_ratio_interpretation','delta13C_C16','delta13C_C18','delta13C_difference','published_isotope_interpretation']
    with (out/'kotada2020_tableS1.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(cols);w.writerows(samples)
    parser=Tables();parser.feed((src/'gujarat2022.html').read_text())
    table=next(t for t in parser.tables if any(r and r[0]=='DTR101' for r in t))
    selected=[];site=None
    for r in table:
        if r and r[0] in {'Datrana','Loteshwar','Shikarpur'}:site=r[0]
        if r and re.match(r'^(DTR\d|\d{6}/)',r[0]):
            assert len(r)==13;selected.append([site]+r)
    assert len(selected)==28
    cols=['site','sample_id','lipid_ug_g','palmitic_stearic_ratio','delta13C_C16','delta13C_C18','delta13C_difference','small_millet_starch_count','jobs_tears_starch_count','wheat_barley_starch_count','pulse_starch_count','ginger_starch_count','other_USO_count','unidentified_starch_count']
    with (out/'gujarat2022_table2.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(cols);w.writerows(selected)
    import fitz
    pdf=fitz.open(src/'northwest2021-si3.pdf');excluded=[]
    pat=re.compile(r'\b(ALM\s*\d+(?:\s*-\s*\d+)?|FRN\s*\d+|KNK\s*\d+|LHR\s*\d+|MSD\s*\d+[A-Z]?|RGR\s*\d+)\b',re.I)
    for page_i in range(38,len(pdf)):
        for m in pat.finditer(pdf[page_i].get_text()):
            excluded.append([re.sub(r'\s+','',m[1]).upper(),page_i+1,'Table S15: listed as excluded for low lipid yield; not evidence of empty vessel'])
    assert len(excluded)==49 and len({r[0] for r in excluded})==49
    with (out/'northwest2021_SI3_low_yield_IDs.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['source_sample_id','source_pdf_page','source_status']);w.writerows(excluded)
    print('Extracted 59 Kotada Bhadli rows, the unmodified Cambridge CSV, 28 Gujarat vessel rows and 49 low-yield register IDs. No missing 50th record fabricated.')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',required=True);main(ap.parse_args().source_dir)
