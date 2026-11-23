"""Package the catalogue, reconstruction and archaeological-source work."""
import argparse, gzip, shutil, zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parent;REPO=BASE.parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--output-root',required=True);args=ap.parse_args()
root=Path(args.output_root);root.mkdir(parents=True,exist_ok=True)
catalogue=BASE/'translation_catalogue';catout=root/'ivc-translation-catalogue'
archive=catalogue/'results/all_existing_reading_versions.csv'
archive.with_suffix('.csv.gz').write_bytes(gzip.compress(archive.read_bytes(),mtime=0))
workbook=catout/'indus_readings_and_findspots.xlsx'
assert workbook.exists(),'Build the current catalogue workbook first.'
shutil.copy2(workbook,catalogue/'results'/workbook.name)
folders=[('translation_catalogue',catout),('proto_reconstruction',root/'ivc-proto-reconstruction')]
if (BASE/'context_associations/results/associations.html').exists():folders.append(('context_associations',root/'ivc-context-associations'))
if (BASE/'residue_validation/results/feasibility.html').exists():folders.append(('residue_validation',root/'ivc-residue-validation'))
if (BASE/'context_validation/results/contexts.html').exists():folders.append(('context_validation',root/'ivc-context-validation'))
if (BASE/'capacity_validation/results/capacity.html').exists():folders.append(('capacity_validation',root/'ivc-capacity-validation'))
for name,dest in folders:
    src=BASE/name;dest.mkdir(parents=True,exist_ok=True)
    for f in (src/'results').iterdir():
        if f.is_dir():shutil.copytree(f,dest/f.name,dirs_exist_ok=True)
        if f.is_file() and f.name!='workbook_data.json':
            if f.suffix=='.html':
                page=f.read_text().replace('../../translation_catalogue/results/','../ivc-translation-catalogue/').replace('../../context_associations/results/','../ivc-context-associations/')
                if name in {'residue_validation','context_validation','capacity_validation'}:page=page.replace('href="../README.md"','href="README.md"').replace('href="../SOURCES.md"','href="SOURCES.md"')
                (dest/f.name).write_text(page)
            else:shutil.copy2(f,dest/f.name)
    readme=(src/'README.md').read_text().replace('../translation_catalogue/README.md','../ivc-translation-catalogue/README.md').replace('../proto_reconstruction/results/','../ivc-proto-reconstruction/').replace('../context_associations/results/','../ivc-context-associations/')
    (dest/'README.md').write_text(readme.replace('(results/','('))
    for extra in ['CLUE_FOLLOWUP.md','SCREENSHOT_READINGS.md','PHYSICAL_NEXT_TESTS.md','SAME_CONTEXT_READINGS.md']:
        if (src/extra).exists():
            (dest/extra).write_text((src/extra).read_text().replace('(results/','('))
    for f in ['SOURCE_README.md','source_corrections.json','SOURCES.md','COLLECTION_PROTOCOL.md','DESIGN.md']:
        if (src/f).exists():shutil.copy2(src/f,dest/f)
    if name in {'context_validation','capacity_validation'}:shutil.copy2(src/'run.py',dest/'run.py')
    if name in {'residue_validation','context_validation','capacity_validation'}:shutil.copytree(src/'inputs',dest/'inputs',dirs_exist_ok=True)
books=catout/'original_reading_books';books.mkdir(exist_ok=True)
for f in list(REPO.glob('READINGS*.md'))+[REPO/'CORPUS.md']:shutil.copy2(f,books/f.name)
for _,folder in folders:
    with zipfile.ZipFile(folder.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for f in folder.rglob('*'):
            if f.is_file() and f.suffix!='.png' and 'preview' not in f.name and '.inspect.' not in f.name:z.write(f,Path(folder.name)/f.relative_to(folder))
    print(folder.with_suffix('.zip'))
with zipfile.ZipFile(root/'ivc-research-with-findspots.zip','w',zipfile.ZIP_DEFLATED) as z:
    for _,folder in folders:
        for f in folder.rglob('*'):
            if f.is_file() and f.suffix!='.png' and 'preview' not in f.name and '.inspect.' not in f.name:z.write(f,Path(folder.name)/f.relative_to(folder))
print(root/'ivc-research-with-findspots.zip')
