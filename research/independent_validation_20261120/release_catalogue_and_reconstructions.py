"""Package the catalogue, reconstruction screen and recorded-context comparison."""
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
for name,dest in folders:
    src=BASE/name;dest.mkdir(parents=True,exist_ok=True)
    for f in (src/'results').iterdir():
        if f.is_file() and f.name!='workbook_data.json':
            if f.suffix=='.html':(dest/f.name).write_text(f.read_text().replace('../../translation_catalogue/results/','../ivc-translation-catalogue/').replace('../../context_associations/results/','../ivc-context-associations/'))
            else:shutil.copy2(f,dest/f.name)
    readme=(src/'README.md').read_text().replace('../translation_catalogue/README.md','../ivc-translation-catalogue/README.md').replace('../proto_reconstruction/results/','../ivc-proto-reconstruction/').replace('../context_associations/results/','../ivc-context-associations/')
    (dest/'README.md').write_text(readme.replace('(results/','('))
    for f in ['SOURCE_README.md','source_corrections.json']:
        if (src/f).exists():shutil.copy2(src/f,dest/f)
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
