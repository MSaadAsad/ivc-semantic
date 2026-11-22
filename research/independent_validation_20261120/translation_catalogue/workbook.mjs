import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const base=path.dirname(fileURLToPath(import.meta.url));
const data=JSON.parse(await fs.readFile(path.join(base,'results/workbook_data.json'),'utf8'));
const output=process.argv[2]; if(!output) throw new Error('Supply output directory');
await fs.mkdir(output,{recursive:true});
const wb=Workbook.create();
function table(name,rows,cols){
  const s=wb.worksheets.add(name);s.showGridLines=false;
  const values=[cols.map(c=>c[1]),...rows.map(r=>cols.map(c=>{
    let v=r[c[0]]??'';
    if(c[0]==='sign')v='S'+v;
    if(c[0]==='face_id')v=r.catalogue+':'+v;
    return typeof v==='string'&&v.startsWith('=')?"'"+v:v;
  }))];
  s.getRangeByIndexes(0,0,values.length,cols.length).values=values;
  const used=s.getRangeByIndexes(0,0,values.length,cols.length);
  used.format.font={name:'Arial',size:11}; used.format.rowHeight=34;
  used.format.verticalAlignment='top';used.format.columnWidth=22;
  const headers=s.getRangeByIndexes(0,0,1,cols.length);
  headers.format={fill:'#243D53',font:{name:'Arial',bold:true,color:'#FFFFFF',size:11},wrapText:true,rowHeight:44};
  for(let i=0;i<cols.length;i++){
    const range=s.getRangeByIndexes(0,i,values.length,1);
    range.format.columnWidth=cols[i][2]??22;
    range.format.wrapText=true;
  }
  s.freezePanes.freezeRows(1);s.freezePanes.freezeColumns(2);
  const t=s.tables.add(s.getRangeByIndexes(0,0,values.length,cols.length),true,name.replaceAll(' ','')+'Table');
  t.showFilterButton=true;t.style='TableStyleMedium2';
  return s;
}
const overview=wb.worksheets.add('Overview');overview.showGridLines=false;
overview.getRange('A2').values=[['Indus readings and archaeological contexts']];
overview.getRange('A2').format.font={name:'Arial',size:15,bold:true};
overview.getRange('A4:B10').values=[['Measure','Records'],['Catalogue face/line records',data.summary.catalogue_face_records],['Lipi faces',data.summary.catalogues.Lipi],['Mahadevan lines',data.summary.catalogues.Mahadevan],['Archived reading versions',data.summary.archived_reading_records],['Proposed sign values',data.signs.length],['Additional reading records',data.summary.reading_records_outside_main_corpus]];
overview.getRange('A12').values=[['All readings remain proposals. Full sign assignment measures label coverage, not decipherment.']];
overview.getRange('A13').values=[['Paired catalogues, repeated texts and separate faces remain visible. Counts are not independent artifacts.']];
overview.getRange('A14').values=[['Missing excavation information is retained. Calculated depth-band dates are not presented as excavators’ dates.']];
overview.getRange('A16').values=[['Main list: Inscriptions. Every stored version: all_existing_reading_versions.csv in the accompanying folder.']];
overview.getRange('A17').values=[['Sources: Cúper’s committed corpus exports and Lipi metadata; the Sources columns identify each row’s origin.']];
overview.getRange('A1:H98').format.font={name:'Arial',size:11};
overview.getRange('A2').format.font.size=15;
overview.getRange('A:A').format.columnWidth=57;overview.getRange('B:B').format.columnWidth=20;
overview.getRange('A4:B4').format={fill:'#243D53',font:{bold:true,color:'#FFFFFF'}};
overview.getRange('B5:B10').setNumberFormat('#,##0');
overview.getRange('A4:B10').format.rowHeight=24;
const cityValues=[['City/site label','Catalogue records'],...data.cities.map(r=>[r.city,r.catalogue_face_records])];
overview.getRangeByIndexes(19,0,cityValues.length,2).values=cityValues;
overview.getRange('A20:B20').format={fill:'#243D53',font:{bold:true,color:'#FFFFFF'}};
overview.getRangeByIndexes(20,1,cityValues.length-1,1).setNumberFormat('#,##0');
const inscriptionCols=[['reference','Reference',21],['city','City / site',23],['existing_proposed_translation','Existing proposed translation',78],['excavation_area','Excavation area / locus',25],['block_or_house','Block / house',25],['room_or_grid','Room / grid',23],['depth_recorded','Depth / level as recorded',24],['period_recorded','Recorded period',23],['phase_recorded','Recorded phase',23],['chronology_recorded','Recorded chronology',24],['material','Material',19],['object_type','Object type',20],['context_status','Context availability',48],['existing_proposed_sounds','Existing proposed sounds',65],['sign_sequence','Sign sequence',49],['current_163_key_literal_meanings','Current 163-key literal meanings',90],['current_163_key_roots','Current 163-key roots',90],['assignment_status','Sign assignment status',38],['unassigned_signs','Unassigned signs',28],['intact_as_recorded','Intact as recorded',20],['paired_in_other_catalogue','Paired in other catalogue',25],['catalogue','Catalogue',18],['face_id','Catalogue face / line ID',24],['object_identifier','Object grouping within catalogue',33],['existing_reading_source','Existing reading source',62],['existing_reading_source_row','Source CSV row',18],['existing_reading_status','Source reading status',45],['context_source_url','Context source',65]];
const ins=table('Inscriptions',data.inscriptions,inscriptionCols);
ins.getRange('C2:C9253').format.rowHeight=66;
const signs=table('Sign meanings',data.signs,[['sign','Sign',12],['proposed_meaning','Proposed English meaning',35],['proposed_root','Proposed root',48],['cities','Recorded cities / sites',90],['catalogue_face_records','Catalogue face records',22],['evidence_note','Original evidence note',95],['proposal_source','Proposal source',30]]);
signs.getRange('A2:A164').setNumberFormat('@');
const check=await wb.inspect({kind:'table',range:'Inscriptions!A1:G4',include:'values',tableMaxRows:4,tableMaxCols:7,maxChars:2000});
console.log(check.ndjson);
wb.recalculate();
for(const [sheet,range] of [['Overview','A2:H17'],['Inscriptions','A1:G4'],['Sign meanings','A1:C7']]){
  const preview=await wb.render({sheetName:sheet,range,scale:1,format:'png'});
  await fs.writeFile(path.join(output,sheet.replaceAll(' ','_')+'_preview.png'),new Uint8Array(await preview.arrayBuffer()));
}
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:20},maxChars:1000});
console.log(errors.ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(output,'indus_readings_and_findspots.xlsx'));
console.log(JSON.stringify({exported:true,inscriptions:data.inscriptions.length,signs:data.signs.length}));
